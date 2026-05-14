"""
corrigir_alt_text.py — Atualiza alt text de imagens sem descrição via WP Media API.
Execute: python corrigir_alt_text.py
"""

import sys
import json
import base64
import time
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CONFIG_FILE = "config.json"

IMAGENS = [
    ("morcegos-chaveiro",      "Chaveiro morcego Cthulhu impresso em 3D nas cores roxo e verde"),
    ("download-1-3",           "Bárbaro do Clash of Clans impresso em 3D — figura STL"),
    ("25bcb4905927985b",       "Anquilossauro impresso em 3D nas cores prata e laranja"),
    ("ChatGPT-Image-20-de-abr","Vasos personalizados impressos em 3D com nomes gravados e luminária coração"),
    ("Capture-decran-2026-04-07", "Chaveiro caveira com cérebro removível impresso em 3D"),
]


def carregar_config() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)
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


def main():
    config  = carregar_config()
    api     = f"{config['wp_url'].rstrip('/')}/wp-json/wp/v2"
    token   = base64.b64encode(f"{config['wp_user']}:{config['wp_app_password']}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "User-Agent": "Clube3DBrasil-Bot/1.0",
    })

    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print("❌ Falha na autenticação.")
        return
    print(f"\n  ✅ Conectado como: {r.json().get('name', '')}\n")
    print("=" * 60)

    atualizados = 0
    nao_encontrados = 0

    for filename, alt_text in IMAGENS:
        print(f"  🔍 Buscando: {filename}...")
        r = session.get(f"{api}/media", params={"search": filename, "per_page": 5}, timeout=15)
        if not r.ok or not r.json():
            print(f"    ⚠️  Não encontrado na biblioteca de mídia.")
            nao_encontrados += 1
            continue

        media = r.json()[0]
        media_id = media["id"]
        atual = media.get("alt_text", "")

        if atual:
            print(f"    ⏭️  Já tem alt text: \"{atual}\"")
            continue

        r2 = session.post(f"{api}/media/{media_id}", json={"alt_text": alt_text}, timeout=15)
        if r2.ok:
            print(f"    ✅ Alt text definido: \"{alt_text}\"")
            atualizados += 1
        else:
            print(f"    ❌ Erro HTTP {r2.status_code}: {r2.text[:100]}")

        time.sleep(1)

    print()
    print("=" * 60)
    print(f"  ✅ Atualizados: {atualizados} | ⚠️  Não encontrados: {nao_encontrados}")
    print("=" * 60)


if __name__ == "__main__":
    main()
