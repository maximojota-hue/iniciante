"""
corrigir_meta_posts.py — Adiciona meta description do Yoast em posts que não têm.
Execução única: python corrigir_meta_posts.py
"""

import base64
import json
import os
import requests
from pathlib import Path


def carregar_env():
    env = Path(".env")
    if not env.exists():
        return
    for linha in env.read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.startswith("#"):
            k, _, v = linha.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def gerar_meta_desc(titulo: str, tema: str = "") -> str:
    nome = (titulo
            .replace(" STL para Impressão 3D", "")
            .replace("Modelo 3D ", "")
            .strip(" —-"))
    base = f"Baixe o {nome} STL gratuitamente."
    if tema:
        base += f" Modelo {tema} para impressão 3D em casa."
    base += " Clube 3D Brasil."
    return base[:155]


def main():
    carregar_env()

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    wp_url = config["wp_url"].rstrip("/")
    user   = os.environ.get("WP_USER", "")
    senha  = os.environ.get("WP_PASS", "")

    if not user or not senha:
        print("❌ WP_USER / WP_PASS não encontrados no .env")
        return

    api = f"{wp_url}/wp-json/wp/v2"
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    })

    # Testar conexão
    r = session.get(f"{api}/users/me")
    if r.status_code != 200:
        print(f"❌ Falha na autenticação: {r.status_code}")
        return
    print(f"✅ Conectado como: {r.json().get('name', '')}\n")

    # Buscar todos os posts
    todos = []
    page = 1
    print("📥 Buscando posts...")
    while True:
        r = session.get(f"{api}/posts", params={
            "per_page": 100,
            "page": page,
            "status": "any",
        })
        if r.status_code != 200:
            break
        lote = r.json()
        if not lote:
            break
        todos.extend(lote)
        print(f"   Página {page}: {len(lote)} posts encontrados")
        if len(lote) < 100:
            break
        page += 1

    print(f"\n📊 Total: {len(todos)} posts\n")

    atualizados = 0
    ja_tem = 0
    erros = 0

    for post in todos:
        wp_id  = post["id"]
        titulo = post.get("title", {}).get("rendered", "")
        meta   = post.get("meta", {})

        if meta.get("_yoast_wpseo_metadesc", "").strip():
            ja_tem += 1
            continue

        # Tenta obter tema a partir das categorias (nome)
        cats = post.get("categories", [])
        tema = ""
        if cats:
            r_cat = session.get(f"{api}/categories/{cats[0]}")
            if r_cat.status_code == 200:
                tema = r_cat.json().get("name", "")

        nova_meta = gerar_meta_desc(titulo, tema)

        r_up = session.post(f"{api}/posts/{wp_id}", json={
            "meta": {"_yoast_wpseo_metadesc": nova_meta}
        })

        if r_up.status_code in (200, 201):
            atualizados += 1
            print(f"  ✅ [{wp_id}] {titulo[:55]}")
            print(f"      → {nova_meta}")
        else:
            erros += 1
            print(f"  ❌ [{wp_id}] Erro {r_up.status_code}: {r_up.text[:80]}")

    print(f"""
{'=' * 50}
✅ Atualizados  : {atualizados}
⏭️  Já tinham    : {ja_tem}
❌ Erros        : {erros}
{'=' * 50}
""")


if __name__ == "__main__":
    main()
