"""
atualizar_posts.py — Atualiza o conteúdo dos posts já publicados no WordPress.
Lê os IDs do posts_publicados.json e faz PUT com o novo HTML do posts_gerados.json.
Execute: python atualizar_posts.py
"""

import sys
import json
import base64
import time
from pathlib import Path
import requests

sys.stdout.reconfigure(encoding="utf-8")

CONFIG_FILE          = "config.json"
POSTS_GERADOS_FILE   = Path("posts_gerados.json")
POSTS_PUBLICADOS_FILE = Path("posts_publicados.json")


def carregar_config() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def auth_header(config: dict) -> dict:
    token = base64.b64encode(f"{config['wp_user']}:{config['wp_app_password']}".encode()).decode()
    return {"Authorization": f"Basic {token}", "User-Agent": "Clube3DBrasil-Bot/1.0"}


def main():
    config = carregar_config()
    api    = f"{config['wp_url'].rstrip('/')}/wp-json/wp/v2"
    hdrs   = auth_header(config)

    # Mapa slug → wp_id (usa o ÚLTIMO registro de cada slug para evitar duplicatas)
    with open(POSTS_PUBLICADOS_FILE, encoding="utf-8") as f:
        publicados = json.load(f)

    slug_para_wpid = {}
    for p in publicados:
        slug_para_wpid[p["slug"]] = p["wp_id"]  # sobrescreve, ficando com o último

    # Posts gerados com o novo conteúdo
    with open(POSTS_GERADOS_FILE, encoding="utf-8") as f:
        gerados = json.load(f)

    print()
    print("=" * 60)
    print("  🔄 ATUALIZANDO POSTS NO WORDPRESS")
    print("=" * 60)
    print()

    session = requests.Session()
    session.headers.update(hdrs)

    # Testa conexão
    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print("❌ Falha na autenticação. Verifique config.json.")
        return
    print(f"  ✅ Conectado como: {r.json().get('name', '')}\n")

    atualizados = 0
    erros       = 0

    for post in gerados:
        slug  = post["slug"]
        wp_id = slug_para_wpid.get(slug)

        if not wp_id:
            print(f"  ⚠️  Slug '{slug}' não encontrado em posts_publicados.json — pulando.")
            continue

        print(f"  🔄 [{wp_id}] {post['titulo'][:55]}...")

        payload = {
            "content": post["content"],
            "meta": {
                "_yoast_wpseo_focuskw":  post.get("yoast_keyphrase", ""),
                "_yoast_wpseo_title":    post.get("yoast_title", ""),
                "_yoast_wpseo_metadesc": post.get("yoast_meta", ""),
            },
        }

        try:
            r = session.post(f"{api}/posts/{wp_id}", json=payload, timeout=30)
            if r.ok:
                print(f"    ✅ Atualizado! URL: {r.json().get('link', '')}")
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
    print(f"  ✅ Atualizados: {atualizados} | ❌ Erros: {erros}")
    print("=" * 60)


if __name__ == "__main__":
    main()
