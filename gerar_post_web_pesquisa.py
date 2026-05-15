"""
Pesquisa paginas brasileiras e americanas sobre um tema de impressao 3D,
extrai conteudo, compara os achados e gera um post SEO em PT-BR.

Uso:
  python gerar_post_web_pesquisa.py "filamento PLA silk"
  python gerar_post_web_pesquisa.py "Bambu Lab A1 review" --categoria "Impressoras e Reviews"
  python gerar_post_web_pesquisa.py "STL Pokemon" --publicar
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

import publisher
import seo_writer

sys.stdout.reconfigure(encoding="utf-8")


BUSCA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

DOMINIOS_FRACOS = {
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "tiktok.com",
    "reddit.com",
    "x.com",
    "twitter.com",
}

DOMINIOS_FORTES = {
    "all3dp.com",
    "printables.com",
    "makerworld.com",
    "thingiverse.com",
    "prusa3d.com",
    "bambulab.com",
    "ultimaker.com",
    "creality.com",
    "3dnatives.com",
    "filament2print.com",
    "3dlab.com.br",
    "cliever.com",
    "robocore.net",
    "makerhero.com",
    "blog.render.com.br",
}


@dataclass
class ResultadoBusca:
    mercado: str
    titulo: str
    url: str
    snippet: str
    score: int = 0
    conteudo_chars: int = 0


def carregar_config_wp() -> dict:
    cfg = {}
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() == "WP_USER":
                cfg["wp_user"] = v
            if k.strip() == "WP_PASS":
                cfg["wp_app_password"] = v
            if k.strip() == "WP_URL":
                cfg["wp_url"] = v
            if k.strip() == "TELEGRAM_BOT_TOKEN":
                cfg["telegram_bot_token"] = v
            if k.strip() == "TELEGRAM_CHAT_ID":
                cfg["telegram_chat_id"] = v
            if k.strip() == "TELEGRAM_ENABLED":
                cfg["telegram_enabled"] = v
            if k.strip() == "TELEGRAM_NOTIFY_STATUSES":
                cfg["telegram_notify_statuses"] = v
            if k.strip() == "TELEGRAM_TIMEOUT":
                cfg["telegram_timeout"] = v
    cfg.setdefault("wp_url", "https://clube3dbrasil.com")
    cfg["wp_post_status"] = "draft"
    return cfg


def limpar_url_duckduckgo(url: str) -> str:
    if url.startswith("//"):
        url = "https:" + url
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])
    return url


def dominio(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def dominio_raiz(url: str) -> str:
    host = dominio(url)
    parts = host.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def buscar_duckduckgo(query: str, mercado: str, limite: int) -> list[ResultadoBusca]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    resp = requests.get(url, headers=BUSCA_HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    resultados: list[ResultadoBusca] = []
    vistos = set()
    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        if not link:
            continue
        href = limpar_url_duckduckgo(link.get("href", ""))
        if not href.startswith("http"):
            continue
        root = dominio_raiz(href)
        if root in DOMINIOS_FRACOS or root in vistos:
            continue
        vistos.add(root)
        snippet_el = item.select_one(".result__snippet")
        resultados.append(ResultadoBusca(
            mercado=mercado,
            titulo=link.get_text(" ", strip=True),
            url=href,
            snippet=snippet_el.get_text(" ", strip=True) if snippet_el else "",
        ))
        if len(resultados) >= limite:
            break
    return resultados


def criar_queries(tema: str) -> dict[str, list[str]]:
    base = tema.strip()
    return {
        "br": [
            f"{base} impressao 3D Brasil",
            f"{base} impressora 3D tutorial portugues",
            f"{base} filamento configuracao impressao 3D",
        ],
        "us": [
            f"{base} 3D printing guide",
            f"{base} 3D printer settings",
            f"{base} 3D printing review tutorial",
        ],
    }


def pontuar_resultado(resultado: ResultadoBusca, tema: str, conteudo: str) -> int:
    texto = f"{resultado.titulo} {resultado.snippet} {conteudo[:1200]}".lower()
    termos = [t for t in re.split(r"\W+", tema.lower()) if len(t) >= 3]
    score = 35
    score += min(25, sum(5 for termo in termos if termo in texto))
    score += 15 if "3d" in texto or "impressao" in texto or "printing" in texto else 0
    score += 15 if resultado.mercado == "br" and (".br" in dominio(resultado.url) or "brasil" in texto) else 0
    score += 10 if dominio(resultado.url) in DOMINIOS_FORTES or dominio_raiz(resultado.url) in DOMINIOS_FORTES else 0
    score += 10 if len(conteudo) >= 1500 else 0
    score -= 20 if len(conteudo) < 500 else 0
    return max(0, min(score, 100))


def _cache_path_url(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return Path("reports") / "web_cache" / f"{digest}.json"


def extrair_conteudo_web_cache(url: str, log_fn=print, usar_cache: bool = True) -> dict:
    cache_path = _cache_path_url(url)
    if usar_cache and cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            log_fn(f"  [cache] {url}")
            return data
        except Exception:
            pass

    data = seo_writer.extrair_conteudo_web(url, log_fn=log_fn)
    if usar_cache and data.get("conteudo"):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def _extrair_e_pontuar(item: ResultadoBusca, tema: str, log_fn=print, usar_cache: bool = True) -> dict:
    extraido = extrair_conteudo_web_cache(item.url, log_fn=log_fn, usar_cache=usar_cache)
    conteudo = extraido.get("conteudo", "")
    item.conteudo_chars = len(conteudo)
    item.score = pontuar_resultado(item, tema, conteudo)
    return {
        **asdict(item),
        "titulo_extraido": extraido.get("titulo", ""),
        "descricao": extraido.get("descricao", ""),
        "conteudo": conteudo,
    }


def pesquisar_fontes(
    tema: str,
    por_mercado: int = 2,
    log_fn=print,
    max_candidatos_mercado: int | None = None,
    workers_extracao: int = 4,
    usar_cache: bool = True,
    pausa_busca: float = 0.2,
) -> list[dict]:
    queries = criar_queries(tema)
    candidatos: list[ResultadoBusca] = []
    vistos = set()
    max_candidatos_mercado = max_candidatos_mercado or max(3, por_mercado * 2)

    for mercado, lista_queries in queries.items():
        for query in lista_queries:
            if sum(1 for item in candidatos if item.mercado == mercado) >= max_candidatos_mercado:
                break
            log_fn(f"  [{mercado.upper()}] buscando: {query}")
            try:
                for item in buscar_duckduckgo(query, mercado, por_mercado):
                    root = dominio_raiz(item.url)
                    chave = (mercado, root)
                    if chave not in vistos:
                        candidatos.append(item)
                        vistos.add(chave)
                        if sum(1 for atual in candidatos if atual.mercado == mercado) >= max_candidatos_mercado:
                            break
                time.sleep(pausa_busca)
            except Exception as exc:
                log_fn(f"  AVISO busca falhou: {exc}")

    fontes = []
    with ThreadPoolExecutor(max_workers=max(1, workers_extracao)) as executor:
        futuros = {
            executor.submit(_extrair_e_pontuar, item, tema, log_fn, usar_cache): item
            for item in candidatos
        }
        for futuro in as_completed(futuros):
            try:
                fontes.append(futuro.result())
            except Exception as exc:
                log_fn(f"  AVISO extracao falhou: {exc}")

    fontes.sort(key=lambda f: (f["mercado"], -f["score"]))
    selecionadas = []
    for mercado in ("br", "us"):
        selecionadas.extend([f for f in fontes if f["mercado"] == mercado and f["score"] >= 45][:por_mercado])
    return selecionadas


def carregar_fontes_manuais(urls: list[str], tema: str, log_fn=print, usar_cache: bool = True) -> list[dict]:
    fontes = []
    for url in urls:
        mercado = "br" if ".br" in dominio(url) or "/pt" in url.lower() else "us"
        item = ResultadoBusca(mercado=mercado, titulo=url, url=url, snippet="")
        fontes.append(_extrair_e_pontuar(item, tema, log_fn=log_fn, usar_cache=usar_cache))
    fontes.sort(key=lambda f: (f["mercado"], -f["score"]))
    return fontes


def montar_contexto_comparativo(
    tema: str,
    fontes: list[dict],
    chars_por_fonte: int = 700,
    contexto_total_max: int = 4500,
) -> tuple[str, str]:
    br = [f for f in fontes if f["mercado"] == "br"]
    us = [f for f in fontes if f["mercado"] == "us"]

    blocos = [
        f"Pesquisa comparativa para: {tema}",
        "",
        "Objetivo editorial:",
        "- Comparar o que paginas brasileiras e americanas estao cobrindo.",
        "- Adaptar as melhores ideias para makers brasileiros.",
        "- Criar texto original, sem copiar trechos das fontes.",
        "",
        "Fontes brasileiras:",
    ]

    for idx, fonte in enumerate(br, 1):
        blocos.append(
            f"{idx}. {fonte['titulo_extraido'] or fonte['titulo']} | {fonte['url']} | score {fonte['score']}\n"
            f"Resumo bruto: {fonte['conteudo'][:chars_por_fonte]}"
        )

    blocos.append("\nFontes americanas/internacionais:")
    for idx, fonte in enumerate(us, 1):
        blocos.append(
            f"{idx}. {fonte['titulo_extraido'] or fonte['titulo']} | {fonte['url']} | score {fonte['score']}\n"
            f"Resumo bruto: {fonte['conteudo'][:chars_por_fonte]}"
        )

    titulos = " | ".join((f["titulo_extraido"] or f["titulo"])[:90] for f in fontes[:4])
    urls = ", ".join(f["url"] for f in fontes[:6])
    return titulos, "\n\n".join(blocos)[:contexto_total_max] + f"\n\nURLs consultadas: {urls}"


def keyword_para_secundarias(keyword: str) -> list[str]:
    base = keyword.strip().lower()
    return [
        f"{base} impressao 3d",
        f"{base} tutorial",
        f"{base} configuracao",
    ]


def copiar_imagem_afiliado(caminho: str, nome_produto: str) -> str:
    origem = Path(caminho)
    if not caminho or not origem.exists():
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", nome_produto.lower()).strip("-") or "produto-afiliado"
    destino_dir = Path("downloads") / "afiliados"
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"{slug}{origem.suffix.lower() or '.jpg'}"
    shutil.copy2(origem, destino)
    return str(destino)


def gerar_post_por_pesquisa_web(
    tema: str,
    categoria: str,
    por_mercado: int = 2,
    publicar: bool = False,
    affiliate_url: str = "",
    affiliate_name: str = "",
    affiliate_image_path: str = "",
    featured_image_path: str = "",
    source_urls: list[str] | None = None,
    affiliates_json: str = "",
    affiliates_file: str = "",
    modo_completo: bool = False,
    usar_cache: bool = True,
    workers_extracao: int = 4,
) -> dict:
    print("\n" + "=" * 70)
    print(f"Pesquisa web comparativa: {tema}")
    print("=" * 70)

    if modo_completo:
        chars_por_fonte = 1200
        contexto_total_max = 9000
        contexto_modelo_max = 4000
        max_tokens_modelo = 4096
        faixa_palavras = "900-1.100"
        max_candidatos_mercado = max(6, por_mercado * 3)
        pausa_busca = 1.0
    else:
        chars_por_fonte = 700
        contexto_total_max = 4500
        contexto_modelo_max = 3000
        max_tokens_modelo = 3072
        faixa_palavras = "700-850"
        max_candidatos_mercado = max(3, por_mercado * 2)
        pausa_busca = 0.2

    fontes = carregar_fontes_manuais(source_urls, tema, log_fn=print, usar_cache=usar_cache) if source_urls else []
    if not fontes:
        fontes = pesquisar_fontes(
            tema,
            por_mercado=por_mercado,
            log_fn=print,
            max_candidatos_mercado=max_candidatos_mercado,
            workers_extracao=workers_extracao,
            usar_cache=usar_cache,
            pausa_busca=pausa_busca,
        )
    if not fontes:
        raise RuntimeError("Nenhuma fonte web util encontrada para o tema.")

    print("\nFontes selecionadas:")
    for fonte in fontes:
        print(f"  [{fonte['mercado'].upper()}] {fonte['score']:>3} | {fonte['titulo'][:72]} | {fonte['url']}")

    page_title, page_content = montar_contexto_comparativo(
        tema,
        fontes,
        chars_por_fonte=chars_por_fonte,
        contexto_total_max=contexto_total_max,
    )
    print(
        "\nModo de geracao: "
        f"{'completo' if modo_completo else 'rapido'} | "
        f"contexto={len(page_content)} chars | "
        f"saida={faixa_palavras} palavras | "
        f"cache={'on' if usar_cache else 'off'}"
    )
    afiliados_override = None
    if affiliates_file:
        afiliados_data = json.loads(Path(affiliates_file).read_text(encoding="utf-8"))
        afiliados_override = []
        for item in afiliados_data:
            nome = item.get("nome") or item.get("name") or tema
            imagem = copiar_imagem_afiliado(item.get("imagem") or item.get("image") or "", nome)
            afiliados_override.append({
                "nome": nome,
                "tipo": item.get("tipo", "filamento"),
                "link": item.get("link", ""),
                "imagem": imagem,
            })
    elif affiliates_json:
        afiliados_override = []
        for item in json.loads(affiliates_json):
            nome = item.get("nome") or item.get("name") or tema
            imagem = copiar_imagem_afiliado(item.get("imagem") or item.get("image") or "", nome)
            afiliados_override.append({
                "nome": nome,
                "tipo": item.get("tipo", "filamento"),
                "link": item.get("link", ""),
                "imagem": imagem,
            })
    elif affiliate_url:
        imagem_afiliado = copiar_imagem_afiliado(affiliate_image_path, affiliate_name or tema)
        afiliados_override = [{
            "nome": affiliate_name or tema,
            "tipo": "impressora",
            "link": affiliate_url,
            "imagem": imagem_afiliado,
        }]

    post = seo_writer.gerar_post_web(
        keyword=tema,
        secondary_kws=keyword_para_secundarias(tema),
        page_url=fontes[0]["url"],
        page_title=page_title,
        page_content=page_content,
        categoria=categoria,
        afiliados_override=afiliados_override,
        log_fn=print,
        contexto_max_chars=contexto_modelo_max,
        max_tokens=max_tokens_modelo,
        faixa_palavras=faixa_palavras,
    )
    if featured_image_path:
        post["featured_image_path"] = featured_image_path

    post["origem"] = "pesquisa_web_br_us"
    post["fontes_pesquisa"] = [
        {
            "mercado": f["mercado"],
            "titulo": f["titulo_extraido"] or f["titulo"],
            "url": f["url"],
            "score": f["score"],
        }
        for f in fontes
    ]

    saida_dir = Path("reports")
    saida_dir.mkdir(exist_ok=True)
    slug = post.get("slug") or re.sub(r"[^a-z0-9]+", "-", tema.lower()).strip("-")
    saida = saida_dir / f"pesquisa-web-{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    saida.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRelatorio salvo: {saida}")

    if publicar:
        print("\nPublicando como rascunho no WordPress...")
        cfg = carregar_config_wp()
        pub = publisher.WordPressPublisher(cfg)
        result = pub.publicar_post(post)
        post["wordpress_result"] = result
        print(f"OK: {result}")

    return post


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera post SEO via pesquisa web BR + US.")
    parser.add_argument("tema", nargs="?", help="Tema ou keyword principal do post.")
    parser.add_argument("--categoria", default="Impressao 3D", help="Categoria WordPress/SEO.")
    parser.add_argument("--por-mercado", type=int, default=2, help="Fontes por mercado BR/US.")
    parser.add_argument("--publicar", action="store_true", help="Publica como rascunho no WordPress.")
    parser.add_argument("--completo", action="store_true", help="Usa pesquisa/contexto maiores e post mais longo.")
    parser.add_argument("--sem-cache", action="store_true", help="Ignora cache local de paginas web.")
    parser.add_argument("--workers-extracao", type=int, default=4, help="Downloads paralelos de paginas fonte.")
    parser.add_argument("--affiliate-url", default="", help="Link de afiliado para inserir no post.")
    parser.add_argument("--affiliate-name", default="", help="Nome do produto afiliado.")
    parser.add_argument("--affiliate-image", default="", help="Foto do produto afiliado para aparecer no texto.")
    parser.add_argument("--featured-image", default="", help="Caminho da imagem principal do post.")
    parser.add_argument("--source-url", action="append", default=[], help="URL fonte manual. Pode repetir.")
    parser.add_argument("--affiliates-json", default="", help="Lista JSON de afiliados com nome/link/imagem.")
    parser.add_argument("--affiliates-file", default="", help="Arquivo JSON com lista de afiliados.")
    args = parser.parse_args()

    tema = args.tema or input("Tema/keyword do post: ").strip()
    if not tema:
        raise SystemExit("Informe um tema.")

    gerar_post_por_pesquisa_web(
        tema=tema,
        categoria=args.categoria,
        por_mercado=max(1, min(args.por_mercado, 5)),
        publicar=args.publicar,
        affiliate_url=args.affiliate_url,
        affiliate_name=args.affiliate_name,
        affiliate_image_path=args.affiliate_image,
        featured_image_path=args.featured_image,
        source_urls=args.source_url,
        affiliates_json=args.affiliates_json,
        affiliates_file=args.affiliates_file,
        modo_completo=args.completo,
        usar_cache=not args.sem_cache,
        workers_extracao=max(1, min(args.workers_extracao, 8)),
    )


if __name__ == "__main__":
    main()
