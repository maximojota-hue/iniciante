"""
corrigir_helio_seo.py — Corrige 3 problemas SEO do HelioBrinquedos:
  1. Alt text vazio nas imagens dos posts (content HTML + media library)
  2. Slug com emoji no post Pachinko (ID 72)
  3. sample-page → noindex via Yoast
"""

import sys, io, os, json, re, base64, urllib.request, urllib.error
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WP_URL  = "https://heliobrinquedos.clube3dbrasil.com"
WP_USER = "HBRAROS"
WP_PASS = "jU4R ZDLf JBcV EH6i ABuh IiVI"
UA      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

TOKEN   = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {TOKEN}",
    "Content-Type":  "application/json",
    "User-Agent":    UA,
}


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(path: str, params: dict = None) -> dict | list:
    url = f"{WP_URL}/wp-json/wp/v2/{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def _post(path: str, body: dict) -> dict:
    url = f"{WP_URL}/wp-json/wp/v2/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {body_err}") from e


def _patch_media(media_id: int, alt_text: str) -> bool:
    url = f"{WP_URL}/wp-json/wp/v2/media/{media_id}"
    data = json.dumps({"alt_text": alt_text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status in (200, 201)
    except urllib.error.HTTPError:
        return False


# ── FIX 1 — Alt text em imagens dos posts ────────────────────────────────────

def fix_alt_text():
    print("=" * 56)
    print("FIX 1 — Alt text vazio em imagens dos posts")
    print("=" * 56)

    posts = _get("posts", {"per_page": "20", "context": "edit",
                           "_fields": "id,title,content,slug"})
    print(f"  {len(posts)} post(s) encontrado(s)\n")

    ok = err = pular = 0

    for post in posts:
        pid    = post["id"]
        titulo = re.sub(r"<[^>]+>", "", post["title"]["rendered"]).strip()
        raw    = post["content"]["raw"]

        # Conta alt="" nas tags <img>
        n_vazios = len(re.findall(r'alt=""', raw))
        if n_vazios == 0:
            pular += 1
            print(f"  ⏭️  [{pid}] {titulo[:50]} — sem alt vazios")
            continue

        print(f"  📝 [{pid}] {titulo[:55]}")
        print(f"       {n_vazios} alt vazio(s) encontrado(s)")

        # Corrige alt="" → alt="titulo" na tag <img>
        safe_title = titulo.replace('"', "'")
        new_raw    = re.sub(r'alt=""', f'alt="{safe_title}"', raw)

        # Também injeta "alt" no JSON do bloco Gutenberg, ex:
        # {"id":108,"sizeSlug":"large"} → {"id":108,"alt":"titulo","sizeSlug":"large"}
        def _inject_alt_block(m):
            block_json_str = m.group(1)
            try:
                bj = json.loads(block_json_str)
                bj["alt"] = safe_title
                return f'<!-- wp:image {json.dumps(bj, ensure_ascii=False)} -->'
            except Exception:
                return m.group(0)

        new_raw = re.sub(
            r'<!-- wp:image (\{.*?\}) -->',
            _inject_alt_block,
            new_raw,
        )

        # Extrai IDs das mídias para atualizar alt_text na biblioteca
        media_ids = re.findall(r'"id":(\d+)', raw)
        # Filtra apenas imagens (pegar do bloco wp:image)
        block_media_ids = []
        for block_m in re.finditer(r'<!-- wp:image (\{.*?\}) -->', raw):
            try:
                bj = json.loads(block_m.group(1))
                if "id" in bj:
                    block_media_ids.append(bj["id"])
            except Exception:
                pass

        try:
            _post(f"posts/{pid}", {"content": new_raw})
            print(f"       ✅ Content atualizado")
            ok += 1
        except RuntimeError as e:
            print(f"       ❌ Erro no content: {e}")
            err += 1
            continue

        # Atualiza alt_text na biblioteca de mídia
        for mid in block_media_ids:
            updated = _patch_media(mid, safe_title)
            print(f"       🖼️  media/{mid} alt_text → {'OK' if updated else 'FALHOU'}")

        print()

    print(f"  Resultado: ✅ {ok} | ⏭️ {pular} | ❌ {err}\n")


# ── FIX 2 — Slug com emoji no post Pachinko ───────────────────────────────────

def fix_slug_emoji():
    print("=" * 56)
    print("FIX 2 — Slug com emoji (post Pachinko ID 72)")
    print("=" * 56)

    novo_slug = "jogo-eletronico-casio-pachinko-game-pg-100-vintage-raro-colecionavel"
    try:
        result = _post("posts/72", {"slug": novo_slug})
        slug_atual = result.get("slug", "?")
        link       = result.get("link", "?")
        print(f"  ✅ Slug atualizado: {slug_atual}")
        print(f"  🔗 Nova URL: {link}\n")
    except RuntimeError as e:
        print(f"  ❌ Erro: {e}\n")


# ── FIX 3 — sample-page → noindex ────────────────────────────────────────────

def fix_sample_page():
    print("=" * 56)
    print("FIX 3 — sample-page → noindex via Yoast")
    print("=" * 56)

    pages = _get("pages", {"slug": "sample-page", "_fields": "id,title,slug,status"})
    if not pages:
        print("  ℹ️  sample-page não encontrada.\n")
        return

    page    = pages[0]
    page_id = page["id"]
    title   = re.sub(r"<[^>]+>", "", page["title"]["rendered"]).strip()
    print(f"  Página encontrada: [{page_id}] '{title}' — status: {page['status']}")

    try:
        result = _post(f"pages/{page_id}", {
            "meta": {"_yoast_wpseo_meta-robots-noindex": "1"}
        })
        print(f"  ✅ noindex ativado (Yoast meta salvo)")
    except RuntimeError as e:
        print(f"  ⚠️  Meta Yoast via API falhou: {e}")
        print(f"  ↳ Alternativa: deletar a página manualmente no WP Admin → Páginas")

    print()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n🔧 Iniciando correções SEO — {WP_URL}\n")

    try:
        auth_check = _get("users/me", {"_fields": "name"})
        print(f"  ✅ Autenticado como: {auth_check.get('name', WP_USER)}\n")
    except Exception as e:
        print(f"  ❌ Falha na autenticação: {e}")
        sys.exit(1)

    fix_alt_text()
    fix_slug_emoji()
    fix_sample_page()

    print("=" * 56)
    print("✅ Todas as correções concluídas.")
    print("=" * 56)
