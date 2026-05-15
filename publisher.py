"""
publisher.py — Módulo 3: Publisher WordPress
Publica posts no WordPress via REST API com retry automático,
cache de slug para evitar duplicatas e logging estruturado.
"""

import base64
import logging
import mimetypes
import re
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import telegram_notifier

logger = logging.getLogger(__name__)


class WordPressApiError(RuntimeError):
    pass


class WordPressPublisher:

    def __init__(self, config: dict):
        self.config   = config
        self.wp_url   = config["wp_url"].rstrip("/")
        self.user     = config["wp_user"]
        self.password = config["wp_app_password"]
        self.api      = f"{self.wp_url}/wp-json/wp/v2"
        self.timeout  = int(config.get("wp_timeout", 45))
        # Quando true, usa /?rest_route= em vez de /wp-json/ (fallback p/ rewrite quebrado)
        self.use_rest_route = bool(config.get("wp_use_rest_route", False))

        self._slug_cache:       dict[str, dict | None] = {}
        self._cache_tags:       dict[str, int] = {}
        self._cache_categorias: dict[str, int] = {}

        self.session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=1.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT"),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://",  HTTPAdapter(max_retries=retry))

        token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "Accept":        "application/json",
            "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        })
        self._lock = threading.Lock()

    # ── Requisições ───────────────────────────────────────────────────────────

    def _build_url(self, path: str) -> tuple[str, dict]:
        """Constrói URL respeitando use_rest_route. Retorna (url, query_params_extra)."""
        path = path.lstrip("/")
        # Separa query string já presente em path
        extra_params: dict = {}
        if "?" in path:
            path_only, qs = path.split("?", 1)
            from urllib.parse import parse_qsl
            extra_params = dict(parse_qsl(qs, keep_blank_values=True))
            path = path_only
        if self.use_rest_route:
            url = f"{self.wp_url}/?rest_route=/wp/v2/{path}"
        else:
            url = f"{self.api}/{path}"
        return url, extra_params

    def _request(self, method: str, path: str, **kwargs) -> dict | list:
        url, extra_params = self._build_url(path)
        if extra_params:
            params = kwargs.pop("params", None) or {}
            if isinstance(params, dict):
                merged = {**extra_params, **params}
                kwargs["params"] = merged
            else:
                kwargs["params"] = list(extra_params.items()) + list(params)
        try:
            r = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            logger.exception("Falha de rede: %s %s", method, path)
            raise WordPressApiError(f"Falha de rede na API WordPress: {exc.__class__.__name__}") from exc

        # Auto-fallback: se primeira tentativa pretty permalink falhou com 404 HTML, tenta rest_route
        if (r.status_code == 404 and not self.use_rest_route
                and "wp-json" in url and "<!DOCTYPE html>" in r.text[:200]):
            logger.warning("Pretty permalink /wp-json/ falhou (404 HTML). Auto-fallback para ?rest_route=")
            self.use_rest_route = True
            url, extra_params = self._build_url(path)
            if extra_params:
                params = kwargs.pop("params", None) or {}
                if isinstance(params, dict):
                    kwargs["params"] = {**extra_params, **params}
            try:
                r = self.session.request(method, url, timeout=self.timeout, **kwargs)
            except requests.RequestException as exc:
                raise WordPressApiError(f"Falha de rede no fallback: {exc.__class__.__name__}") from exc

        if r.status_code >= 400:
            body = r.text[:500]
            logger.error("WordPress API erro %s em %s %s: %s", r.status_code, method, path, body)
            raise WordPressApiError(f"WordPress API erro {r.status_code}: {body}")

        try:
            return r.json()
        except ValueError as exc:
            raise WordPressApiError("WordPress retornou resposta sem JSON válido.") from exc

    # ── Conexão ───────────────────────────────────────────────────────────────

    def testar_conexao(self) -> bool:
        try:
            data = self._request("GET", "users/me")
            nome = data.get("name", "")
            logger.info("WordPress conectado como: %s", nome)
            print(f"  ✅ WordPress conectado como: {nome}")
            return True
        except WordPressApiError as exc:
            logger.error("Falha na autenticação: %s", exc)
            print(f"  ❌ Falha na autenticação: {exc}")
            return False

    # ── Cache de slug ─────────────────────────────────────────────────────────

    def _buscar_post_por_slug(self, slug: str) -> dict | None:
        with self._lock:
            if slug in self._slug_cache:
                return self._slug_cache[slug]
        try:
            from urllib.parse import quote
            posts = self._request("GET", f"posts?slug={quote(slug)}&status=publish,draft,future,pending")
        except WordPressApiError:
            logger.warning("Não foi possível verificar slug existente: %s", slug)
            return None
        result = posts[0] if isinstance(posts, list) and posts else None
        with self._lock:
            self._slug_cache[slug] = result
        return result

    # ── Tags e Categorias ─────────────────────────────────────────────────────

    def _term_id_from_400(self, body: dict) -> int:
        """Extrai term_id de resposta 400 term_exists do WP."""
        term_id = body.get("data", {}).get("term_id", 0)
        if not term_id:
            additional = body.get("additional_data") or []
            term_id = additional[0] if additional else 0
        return int(term_id) if term_id else 0

    def _obter_ou_criar_tag(self, nome: str) -> int:
        with self._lock:
            if nome in self._cache_tags:
                return self._cache_tags[nome]
        try:
            tags = self._request("GET", "tags", params={"search": nome, "per_page": 5})
            for tag in (tags if isinstance(tags, list) else []):
                if tag["name"].lower() == nome.lower():
                    with self._lock:
                        self._cache_tags[nome] = tag["id"]
                    return tag["id"]
        except WordPressApiError as exc:
            logger.warning("Erro ao buscar tag '%s': %s", nome, exc)
            return 0

        url, _ = self._build_url("tags")
        r = self.session.post(url, json={"name": nome}, timeout=self.timeout)
        if r.status_code in (200, 201):
            tid = r.json()["id"]
        elif r.status_code == 400 and r.json().get("code") == "term_exists":
            tid = self._term_id_from_400(r.json())
        else:
            logger.warning("Erro ao criar tag '%s': %s %s", nome, r.status_code, r.text[:200])
            return 0
        if tid:
            with self._lock:
                self._cache_tags[nome] = tid
        return tid

    def _obter_ou_criar_categoria(self, nome: str) -> int:
        with self._lock:
            if nome in self._cache_categorias:
                return self._cache_categorias[nome]
        try:
            cats = self._request("GET", "categories", params={"search": nome, "per_page": 5})
            for cat in (cats if isinstance(cats, list) else []):
                if cat["name"].lower() == nome.lower():
                    with self._lock:
                        self._cache_categorias[nome] = cat["id"]
                    return cat["id"]
        except WordPressApiError as exc:
            logger.warning("Erro ao buscar categoria '%s': %s", nome, exc)
            return 1

        url, _ = self._build_url("categories")
        r = self.session.post(url, json={"name": nome}, timeout=self.timeout)
        if r.status_code in (200, 201):
            cid = r.json()["id"]
        elif r.status_code == 400 and r.json().get("code") == "term_exists":
            cid = self._term_id_from_400(r.json())
        else:
            logger.warning("Erro ao criar categoria '%s': %s %s", nome, r.status_code, r.text[:200])
            return 1
        if cid:
            with self._lock:
                self._cache_categorias[nome] = cid
        return cid

    # ── Upload de imagens ─────────────────────────────────────────────────────

    def _upload_imagem(self, caminho: str, alt_text: str = "", title: str = "") -> tuple[int | None, str]:
        path = Path(caminho)
        if not path.exists():
            logger.warning("Imagem não encontrada: %s", caminho)
            return None, ""

        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "image/jpeg"
        safe_name = path.name.encode("ascii", "ignore").decode("ascii").strip() or f"image{path.suffix}"
        headers = {
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Content-Type": mime,
        }
        try:
            with open(path, "rb") as f:
                media = self._request("POST", "media", headers=headers, data=f.read())

            media_id  = int(media["id"])
            media_url = media.get("source_url", "")

            meta_midia = {}
            if alt_text:
                meta_midia["alt_text"] = alt_text
            if title:
                meta_midia["title"] = title
            if meta_midia:
                self._request("POST", f"media/{media_id}", json=meta_midia)

            logger.info("Imagem enviada: id=%s | title=%s", media_id, title or alt_text)
            return media_id, media_url
        except WordPressApiError as exc:
            logger.error("Erro no upload da imagem %s: %s", caminho, exc)
            return None, ""

    def _substituir_imagens_no_html(
        self, html: str, imagens_locais: list[str], titulo: str, keyphrase: str = ""
    ) -> tuple[str, int | None]:
        featured_id = None
        nome_modelo = titulo.replace("Modelo 3D ", "").replace(" — Download STL Grátis", "").strip()
        base_seo = keyphrase or nome_modelo
        for i, caminho in enumerate(imagens_locais[:2]):
            if "downloads/afiliados/" in caminho.replace("\\", "/"):
                alt   = f"{nome_modelo} produto indicado para impressao 3D"
                title = f"{base_seo} produto indicado"
            elif i == 0:
                alt   = f"{nome_modelo} STL para impressão 3D — arquivo 3D grátis"
                title = base_seo
            else:
                alt   = f"{nome_modelo} STL — vista adicional para impressão 3D"
                title = f"{base_seo} — vista adicional"
            media_id, media_url = self._upload_imagem(caminho, alt_text=alt, title=title)
            if media_url:
                html = html.replace(caminho, media_url)
                if i == 0:
                    featured_id = media_id
        return html, featured_id

    def _processar_imagens_lista(
        self, html: str, imagens_paths: list[str], titulo: str, keyphrase: str = ""
    ) -> tuple[str, int | None]:
        featured_id = None
        nome_modelo = titulo.replace("Modelo 3D ", "").replace(" — Download STL Grátis", "").strip()
        base_seo = keyphrase or nome_modelo

        for i, caminho in enumerate(imagens_paths):
            path = Path(caminho)
            if not path.exists():
                logger.warning("Imagem não encontrada: %s", caminho)
                html = html.replace(f"<!--IMAGEM_{i+1}-->", "")
                continue

            if i == 0:
                alt = f"{nome_modelo} STL para impressão 3D — arquivo 3D grátis"
                title = base_seo
            else:
                alt = f"{nome_modelo} STL — vista adicional para impressão 3D"
                title = f"{base_seo} — vista {i+1}"

            media_id, media_url = self._upload_imagem(caminho, alt_text=alt, title=title)
            if media_url:
                img_html = f'<figure class="wp-block-image"><img src="{media_url}" alt="{alt}"/></figure>'
                html = html.replace(f"<!--IMAGEM_{i+1}-->", img_html)
                if i == 0:
                    featured_id = media_id
            else:
                html = html.replace(f"<!--IMAGEM_{i+1}-->", "")

        for i in range(len(imagens_paths) + 1, 10):
            html = html.replace(f"<!--IMAGEM_{i}-->", "")

        return html, featured_id

    # ── Publicação ────────────────────────────────────────────────────────────

    def publicar_post(self, post: dict, skip_if_exists: bool = True) -> dict | None:
        titulo = post.get("titulo", "Post sem título")
        slug   = post.get("slug", "")
        logger.info("Publicando: %s", titulo[:60])

        if skip_if_exists and slug:
            existente = self._buscar_post_por_slug(slug)
            if existente:
                logger.info("Post já existe para slug '%s'; pulando.", slug)
                print(f"  ⏭️  Já existe: {titulo[:50]}")
                return {"wp_id": existente["id"], "url": existente.get("link", ""), "slug": slug, "titulo": titulo, "status": "existente"}

        html        = post.get("content", "").replace("\\", "/")
        featured_id = post.get("_featured_media_id")  # ID já resolvido externamente
        keyphrase   = post.get("yoast_keyphrase", "")

        # Imagem local selecionada manualmente (só faz upload se ainda não temos ID)
        if not featured_id:
            img_manual = post.get("featured_image_path", "")
            if img_manual and Path(img_manual).exists():
                media_id, _ = self._upload_imagem(
                    img_manual,
                    alt_text=f"{titulo} para impressão 3D",
                    title=keyphrase or titulo,
                )
                if media_id:
                    featured_id = media_id

        # Processar lista de imagens (nova funcionalidade de múltiplas imagens distribuídas)
        imagens_lista = post.get("imagens_lista", [])
        if imagens_lista:
            html, lista_featured_id = self._processar_imagens_lista(html, imagens_lista, titulo, keyphrase)
            if not featured_id and lista_featured_id:
                featured_id = lista_featured_id

        # Captura caminhos locais com barra Windows ou Unix (fallback para imagens inline)
        imagens_locais = re.findall(r'([^\'"<>\s]+downloads[/\\][^\'"<>\s]+\.(?:jpg|jpeg|png|webp))', html)
        # Normaliza separadores
        imagens_locais = [p.replace("\\", "/") for p in imagens_locais]
        if imagens_locais:
            html, embed_featured = self._substituir_imagens_no_html(html, imagens_locais, titulo, keyphrase)
            if not featured_id and embed_featured:
                featured_id = embed_featured

        tag_ids = [t for t in [self._obter_ou_criar_tag(t) for t in post.get("tags", [])] if t]
        cat_ids = [c for c in [self._obter_ou_criar_categoria(c) for c in post.get("categories", [])] if c]

        payload: dict = {
            "title":      titulo,
            "slug":       slug,
            "content":    html,
            "excerpt":    post.get("excerpt", ""),
            "status":     post.get("status", "draft"),
            "tags":       tag_ids,
            "categories": cat_ids,
        }
        if featured_id:
            payload["featured_media"] = featured_id

        dados = self._request("POST", "posts", json=payload)
        url   = dados.get("link", "")
        wp_id = dados.get("id", 0)

        if not wp_id:
            raise WordPressApiError("WordPress não retornou ID do post criado.")

        # Yoast meta em request separado — mais confiável que no payload inicial
        # ATENÇÃO: requer registro REST no WP (functions.php ou plugin Code Snippets)
        yoast = {k: v for k, v in {
            "_yoast_wpseo_focuskw":  keyphrase,
            "_yoast_wpseo_title":    post.get("yoast_title", ""),
            "_yoast_wpseo_metadesc": post.get("yoast_meta", ""),
        }.items() if v}
        if yoast:
            try:
                self._request("POST", f"posts/{wp_id}", json={"meta": yoast})
                logger.info("Meta Yoast salva: focuskw=%s", keyphrase[:40])
                print(f"  ✅ Yoast meta salvo (focuskw: {keyphrase[:40]})")
            except WordPressApiError as exc:
                logger.warning("Meta Yoast NÃO salva para post %s: %s", wp_id, exc)
                print(f"  ⚠️  Yoast meta NÃO salvo (campos não registrados no WP): {exc}")
                print(f"      → Adicione o snippet PHP no functions.php para corrigir.")

        with self._lock:
            self._slug_cache[slug] = dados
        logger.info("Post criado com sucesso: %s", url)
        print(f"  ✅ Post criado! ID: {wp_id} | {url}")
        result = {"wp_id": wp_id, "url": url, "slug": slug, "titulo": titulo, "status": post.get("status", "draft")}

        status_notificar = {
            item.strip().lower()
            for item in str(self.config.get("telegram_notify_statuses", "publish")).split(",")
            if item.strip()
        }
        if result["status"].lower() in status_notificar:
            try:
                enviado = telegram_notifier.notify_post_from_config(
                    self.config,
                    result,
                    excerpt=post.get("excerpt", ""),
                )
                if enviado:
                    print("  ✅ Aviso enviado para o Telegram.")
            except Exception as exc:
                logger.warning("Telegram NÃO enviado para post %s: %s", wp_id, exc)
                print(f"  ⚠️  Telegram NÃO enviado: {exc}")

        return result

    def upload_media(self, caminho: str, alt_text: str = "") -> tuple[int | None, str]:
        """Envia imagem para a biblioteca de midia do WordPress. Retorna (id, url)."""
        return self._upload_imagem(caminho, alt_text=alt_text)

    # ── Lote ─────────────────────────────────────────────────────────────────

    def publicar_lote(self, posts: list[dict], skip_if_exists: bool = True, workers: int = 3, tentativas: int = 3) -> list[dict]:
        if not self.testar_conexao():
            print("\n❌ Publicação cancelada: falha na autenticação.")
            return []

        total = len(posts)
        publicados = []
        erros = 0
        print(f"\n  📤 Publicando {total} post(s) com {workers} worker(s) em paralelo...\n")

        def _publicar_retry(post: dict) -> dict | None:
            for attempt in range(1, tentativas + 1):
                try:
                    return self.publicar_post(post, skip_if_exists=skip_if_exists)
                except (WordPressApiError, Exception) as exc:
                    if attempt >= tentativas:
                        logger.error("Post '%s' falhou após %d tentativas: %s", post.get("titulo", ""), tentativas, exc)
                        return None
                    wait = min(60, 2 ** attempt)
                    logger.warning("Tentativa %d/%d falhou para '%s': aguardando %ds.", attempt, tentativas, post.get("titulo", ""), wait)
                    time.sleep(wait)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futuros = {executor.submit(_publicar_retry, p): p for p in posts}
            concluidos = 0
            for futuro in as_completed(futuros):
                concluidos += 1
                post = futuros[futuro]
                try:
                    resultado = futuro.result()
                    if resultado:
                        publicados.append(resultado)
                        print(f"  [{concluidos}/{total}] ✅ {post.get('titulo', '')[:50]}")
                    else:
                        erros += 1
                        print(f"  [{concluidos}/{total}] ❌ Falhou: {post.get('titulo', '')[:40]}")
                except Exception as exc:
                    erros += 1
                    logger.error("Falha ao publicar '%s': %s", post.get("titulo", ""), exc)
                    print(f"  [{concluidos}/{total}] ❌ Erro: {exc}")

        print(f"\n  ✅ {len(publicados)} publicado(s) | ❌ {erros} erro(s)")
        return publicados
