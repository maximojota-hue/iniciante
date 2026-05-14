"""
injetar_faq_schema.py — Injeta FAQPage JSON-LD em todos os posts existentes.
Busca todos os posts publicados/rascunhos, verifica se já têm o schema e
adiciona nos que não têm.
Execute: python injetar_faq_schema.py
"""

import sys
import json
import base64
import time
import re
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CONFIG_FILE = "config.json"


def carregar_config() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)
    # Carrega credenciais do .env
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key == "WP_USER":
                config["wp_user"] = value
            elif key == "WP_PASS":
                config["wp_app_password"] = value
    return config


def auth_header(config: dict) -> dict:
    token = base64.b64encode(f"{config['wp_user']}:{config['wp_app_password']}".encode()).decode()
    return {"Authorization": f"Basic {token}", "User-Agent": "Clube3DBrasil-Bot/1.0"}


def gerar_faq_schema() -> str:
    faqs = [
        ("O arquivo STL é gratuito?",
         "Sim. O link aponta para a página original do criador. Verifique a licença antes de uso comercial."),
        ("Qual fatiador usar?",
         "Cura, PrusaSlicer e Bambu Studio são compatíveis com STL e 3MF — todos têm versão gratuita."),
        ("Precisa de suporte?",
         "Depende da geometria. Abra no fatiador e ative a pré-visualização de suportes antes de imprimir."),
        ("Quanto filamento consome?",
         "Modelos médios consomem entre 30 g e 150 g dependendo do tamanho e do infill configurado."),
        ("Posso redimensionar o modelo?",
         "Sim. No fatiador você pode escalar livremente sem precisar editar o arquivo STL."),
    ]
    entidades = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faqs
    ]
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entidades}
    return f'\n<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>\n'


def buscar_todos_posts(session: requests.Session, api: str) -> list[dict]:
    posts = []
    page = 1
    while True:
        r = session.get(
            f"{api}/posts",
            params={"per_page": 100, "page": page, "status": "publish,draft"},
            timeout=30,
        )
        if not r.ok:
            break
        lote = r.json()
        if not lote:
            break
        posts.extend(lote)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        print(f"  📄 Página {page}/{total_pages} — {len(lote)} posts carregados")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.5)
    return posts


def ja_tem_schema(content: str) -> bool:
    return "FAQPage" in content and "application/ld+json" in content


def main():
    config  = carregar_config()
    api     = f"{config['wp_url'].rstrip('/')}/wp-json/wp/v2"
    session = requests.Session()
    session.headers.update(auth_header(config))

    # Testa conexão
    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print("❌ Falha na autenticação. Verifique config.json.")
        return
    print(f"\n  ✅ Conectado como: {r.json().get('name', '')}\n")

    print("  🔍 Buscando todos os posts...\n")
    posts = buscar_todos_posts(session, api)
    print(f"\n  Total encontrado: {len(posts)} posts\n")
    print("=" * 60)

    schema_html  = gerar_faq_schema()
    atualizados  = 0
    ja_tinham    = 0
    erros        = 0

    for post in posts:
        wp_id   = post["id"]
        titulo  = post.get("title", {}).get("rendered", f"Post {wp_id}")
        content = post.get("content", {}).get("rendered", "")

        if ja_tem_schema(content):
            ja_tinham += 1
            print(f"  ⏭️  Já tem schema: [{wp_id}] {titulo[:50]}")
            continue

        novo_content = content + schema_html
        print(f"  🔄 [{wp_id}] {titulo[:55]}...")

        try:
            r = session.post(
                f"{api}/posts/{wp_id}",
                json={"content": novo_content},
                timeout=30,
            )
            if r.ok:
                print(f"    ✅ Schema injetado!")
                atualizados += 1
            else:
                print(f"    ❌ Erro HTTP {r.status_code}: {r.text[:150]}")
                erros += 1
        except Exception as e:
            print(f"    ❌ Exceção: {e}")
            erros += 1

        time.sleep(1.5)

    print()
    print("=" * 60)
    print(f"  ✅ Injetados: {atualizados} | ⏭️  Já tinham: {ja_tinham} | ❌ Erros: {erros}")
    print("=" * 60)


if __name__ == "__main__":
    main()
