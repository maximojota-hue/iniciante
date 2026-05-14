"""
corrigir_meta_helio.py — Preenche hb_seo_desc em todos os posts do HelioBrinquedos
via WP REST API + Claude API (Haiku).

Pré-requisitos:
  1. Tema heliobrinquedos-v4 com hb_register_meta_rest() ativo (functions.php atualizado)
  2. ANTHROPIC_API_KEY no .env
  3. pip install anthropic requests

Uso:
  python corrigir_meta_helio.py              # processa posts sem hb_seo_desc
  python corrigir_meta_helio.py --todos      # sobrescreve mesmo os que já têm
  python corrigir_meta_helio.py --dry-run    # mostra sem salvar
"""

import os
import sys
import io
import json
import re
import argparse
import requests
from pathlib import Path

# força UTF-8 no terminal Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Config ─────────────────────────────────────────────────────────────────

WP_URL  = "https://heliobrinquedos.clube3dbrasil.com"
WP_USER = "HBRAROS"
WP_PASS = "jU4R ZDLf JBcV EH6i ABuh IiVI"

MAX_DESC_CHARS = 155


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_env():
    env = Path(__file__).parent / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def _get_api_key() -> str:
    _load_env()
    return os.environ.get("ANTHROPIC_API_KEY", "")


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def _session() -> requests.Session:
    s = requests.Session()
    s.auth = (WP_USER, WP_PASS)
    s.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    })
    return s


# ── WP API ─────────────────────────────────────────────────────────────────

def fetch_posts(session: requests.Session) -> list[dict]:
    posts = []
    page  = 1
    while True:
        r = session.get(f"{WP_URL}/wp-json/wp/v2/posts",
                        params={"per_page": 100, "page": page, "_fields": "id,title,excerpt,content,meta"})
        if r.status_code == 400:
            break
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        page += 1
    return posts


def update_meta(session: requests.Session, post_id: int, desc: str) -> bool:
    r = session.post(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        data=json.dumps({"meta": {"hb_seo_desc": desc}}),
    )
    return r.status_code in (200, 201)


# ── Claude API ─────────────────────────────────────────────────────────────

def gerar_description(titulo: str, conteudo: str, api_key: str) -> str:
    """Gera meta description de até 155 chars via Claude Haiku."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    conteudo_limpo = _strip_html(conteudo)[:800]

    prompt = (
        f"Produto: {titulo}\n\n"
        f"Descrição do produto: {conteudo_limpo}\n\n"
        "Escreva UMA frase de meta description SEO em português brasileiro para este produto de brinquedo antigo/colecionável. "
        "Máximo 155 caracteres. Inclua o nome do produto, algo sobre raridade ou coleção, e apelo para colecionadores. "
        "Retorne SOMENTE a frase, sem aspas, sem explicações."
    )

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}],
    )
    desc = msg.content[0].text.strip().strip('"').strip("'")
    return desc[:MAX_DESC_CHARS]


def gerar_description_simples(titulo: str, conteudo: str) -> str:
    """Fallback sem Claude: gera description do excerpt/conteúdo."""
    texto = _strip_html(conteudo)
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        return f"{titulo} — brinquedo raro e colecionável disponível na HelioBrinquedos."
    base = f"{titulo}. {texto}"
    return base[:MAX_DESC_CHARS].rsplit(" ", 1)[0] + "."


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--todos",   action="store_true", help="Sobrescreve mesmo quem já tem description")
    parser.add_argument("--dry-run", action="store_true", help="Mostra sem salvar")
    parser.add_argument("--sem-claude", action="store_true", help="Usa fallback sem Claude API")
    args = parser.parse_args()

    api_key = "" if args.sem_claude else _get_api_key()
    if not api_key and not args.sem_claude:
        print("⚠️  ANTHROPIC_API_KEY não encontrada — usando fallback simples (sem Claude).")
        print("    Para usar Claude: adicione ANTHROPIC_API_KEY ao .env")

    session = _session()

    print(f"🔗 Conectando a {WP_URL}...")
    try:
        r = session.get(f"{WP_URL}/wp-json/wp/v2/users/me")
        r.raise_for_status()
        print(f"✅ Autenticado como: {r.json().get('name', WP_USER)}\n")
    except Exception as e:
        print(f"❌ Falha na autenticação: {e}")
        sys.exit(1)

    print("📥 Buscando posts...")
    posts = fetch_posts(session)
    print(f"   {len(posts)} post(s) encontrado(s)\n")

    ok = err = pular = 0

    for post in posts:
        pid    = post["id"]
        titulo = _strip_html(post["title"].get("rendered", ""))
        meta   = post.get("meta", {})
        atual  = (meta.get("hb_seo_desc") or "").strip()

        if atual and not args.todos:
            pular += 1
            print(f"  ⏭️  [{pid}] {titulo[:50]} — já tem description")
            continue

        conteudo = post.get("content", {}).get("rendered", "") or \
                   post.get("excerpt", {}).get("rendered", "")

        print(f"  📝 [{pid}] {titulo[:55]}...")

        try:
            if api_key:
                desc = gerar_description(titulo, conteudo, api_key)
            else:
                desc = gerar_description_simples(titulo, conteudo)

            print(f"       → {desc}")

            if args.dry_run:
                ok += 1
                continue

            if update_meta(session, pid, desc):
                print(f"       ✅ Salvo ({len(desc)} chars)")
                ok += 1
            else:
                print(f"       ❌ Falha ao salvar")
                err += 1

        except Exception as e:
            print(f"       ❌ Erro: {e}")
            err += 1

    print(f"\n{'='*50}")
    print(f"✅ Atualizados : {ok}")
    print(f"⏭️  Pulados     : {pular}")
    print(f"❌ Erros       : {err}")


if __name__ == "__main__":
    main()
