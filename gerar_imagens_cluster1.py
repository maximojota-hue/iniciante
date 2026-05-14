"""
gerar_imagens_cluster1.py — Featured images para os 20 posts do Cluster 1 STL Geek
Usa Pollinations.ai (gratuito, sem API key) + WP REST API para setar featured_media.

Execute: python gerar_imagens_cluster1.py
"""

import base64
import json
import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import quote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ── IDs do Cluster 1 (publicados em 2026-05-06) ───────────────────────────────

CLUSTER1_IDS = [2764, 2766, 2768, 2769, 2772, 2774, 2775, 2778,
                2780, 2782, 2784, 2786, 2788, 2789, 2792, 2794,
                2796, 2797, 2800, 2802]

# ── Prompt por slug ───────────────────────────────────────────────────────────

SLUG_PROMPT = {
    "pokemon-stl-gratis-impressao-3d":
        "colorful 3D printed pokemon style figurines collection on printer bed, PLA filament, maker photography, studio lighting, sharp focus",
    "minecraft-stl-gratis-impressao-3d":
        "green cubic 3D printed blocky game character creeper style, FDM printer bed, studio lighting, maker photography",
    "naruto-stl-gratis-impressao-3d":
        "orange 3D printed anime ninja warrior figurine, PLA orange filament, maker photography, white background",
    "dragon-ball-stl-gratis-impressao-3d":
        "3D printed anime warrior figurine golden hair super sayajin, PLA filament, maker photography, studio lighting",
    "como-imprimir-pikachu-3d":
        "yellow 3D printed electric pokemon pikachu figurine, PLA yellow filament, FDM printer background, macro photography",
    "marvel-stl-gratis-impressao-3d":
        "red blue 3D printed superhero collection figurines, FDM printing, studio lighting, maker photography, sharp focus",
    "one-piece-stl-gratis-impressao-3d":
        "red straw hat 3D printed anime pirate character, PLA filament, maker photography, studio background",
    "akatsuki-impressao-3d-stl-gratis":
        "black 3D printed anime villain figurines dark cloak, dramatic lighting, maker photography, studio",
    "demon-slayer-stl-gratis-impressao-3d":
        "3D printed demon slayer anime figurines colorful, PLA filament, maker photography, studio lighting",
    "como-imprimir-goku-super-sayajin-3d":
        "golden 3D printed anime super sayajin warrior figurine, yellow PLA filament, studio lighting, maker photography",
    "star-wars-stl-gratis-impressao-3d":
        "black 3D printed star wars style helmet collection, PLA filament, dramatic lighting, maker photography",
    "como-imprimir-homem-aranha-3d":
        "red blue 3D printed spider-man style superhero figurine, PLA filament, studio lighting, maker photography",
    "zelda-stl-gratis-impressao-3d":
        "green 3D printed fantasy elf warrior figurine link style, PLA filament, maker photography, studio",
    "chapeu-de-palha-luffy-impressao-3d-stl":
        "red 3D printed straw hat anime style one piece, PLA red filament, maker photography, studio background",
    "como-fazer-funko-pop-impressao-3d-stl-gratis":
        "3D printed funko pop style custom figurines colorful collection, PLA filament, maker photography, studio",
    "como-imprimir-mascara-tanjiro-3d":
        "red white 3D printed demon slayer style mask, PLA filament, maker photography, white background",
    "como-imprimir-creeper-3d-iniciante":
        "green 3D printed minecraft creeper cubic figure, PLA filament, FDM printer background, studio lighting",
    "capacete-darth-vader-impressao-3d-stl-gratis":
        "black 3D printed space villain style helmet, PLA matte black filament, dramatic lighting, maker photography",
    "triforce-zelda-impressao-3d-stl-gratis":
        "gold yellow 3D printed triforce triangle zelda symbol, PLA gold filament, maker photography, studio lighting",
    "eevee-evolucoes-impressao-3d-stl-gratis":
        "brown 3D printed pokemon eevee style figurine, PLA filament, maker photography, white background, sharp focus",
}

# Prompt fallback para slugs nao mapeados
PROMPT_FALLBACK = (
    "3D printed anime geek character figurine, PLA filament, maker photography, studio lighting, sharp focus"
)


# ── Config ────────────────────────────────────────────────────────────────────

def _load_env():
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def _load_config() -> dict:
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)


# ── Session WP (mesmo padrão do publisher.py) ─────────────────────────────────

def _make_session(wp_user: str, wp_pass: str) -> requests.Session:
    token = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Basic {token}",
        "Accept":        "application/json",
        "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    return s


# ── Pollinations.ai ───────────────────────────────────────────────────────────

def _baixar_imagem(prompt: str, dest: Path, seed: int = 42, tentativas: int = 3) -> bool:
    url = (
        f"https://image.pollinations.ai/prompt/{quote(prompt)}"
        f"?width=1280&height=720&nologo=true&seed={seed}&model=flux"
    )
    for t in range(1, tentativas + 1):
        try:
            resp = requests.get(url, timeout=90)
            if resp.ok and resp.headers.get("content-type", "").startswith("image"):
                dest.write_bytes(resp.content)
                return True
            if resp.status_code == 429:
                wait = 15 * t
                print(f"  Rate limit 429 — aguardando {wait}s (tentativa {t}/{tentativas})...")
                time.sleep(wait)
                continue
            print(f"  AVISO Pollinations status {resp.status_code}")
            return False
        except Exception as e:
            print(f"  ERRO download (tentativa {t}): {e}")
            if t < tentativas:
                time.sleep(10)
    return False


# ── WP Media Upload ───────────────────────────────────────────────────────────

def _upload_wp(caminho: Path, alt: str, wp_url: str, session: requests.Session) -> int | None:
    api = f"{wp_url.rstrip('/')}/wp-json/wp/v2"
    safe_name = caminho.name.encode("ascii", "ignore").decode("ascii").strip() or "image.jpg"
    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}"',
        "Content-Type": "image/jpeg",
    }
    try:
        with open(caminho, "rb") as f:
            resp = session.post(f"{api}/media", headers=headers, data=f.read(), timeout=30)
        if resp.ok:
            media_id = resp.json().get("id")
            session.post(f"{api}/media/{media_id}",
                         json={"alt_text": alt, "title": alt}, timeout=15)
            return media_id
        print(f"  ERRO upload WP {resp.status_code}: {resp.text[:150]}")
        return None
    except Exception as e:
        print(f"  ERRO upload WP: {e}")
        return None


def _set_featured(wp_id: int, media_id: int, wp_url: str, session: requests.Session) -> bool:
    endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts/{wp_id}"
    try:
        resp = session.post(endpoint, json={"featured_media": media_id}, timeout=15)
        return resp.ok
    except Exception as e:
        print(f"  ERRO set featured: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    _load_env()
    config   = _load_config()
    wp_url   = config["wp_url"]
    wp_user  = os.environ.get("WP_USER", "")
    wp_pass  = os.environ.get("WP_PASS", "")
    auth     = (wp_user, wp_pass)

    if not wp_user or not wp_pass:
        print("ERRO: WP_USER ou WP_PASS nao encontrado no .env")
        sys.exit(1)

    session = _make_session(wp_user, wp_pass)

    # Carrega posts publicados para resolver slug por wp_id
    pub_path = Path("posts_publicados.json")
    publicados = json.loads(pub_path.read_text(encoding="utf-8")) if pub_path.exists() else []
    id_to_slug = {p["wp_id"]: p.get("slug", "") for p in publicados}

    img_dir = Path("imagens_cluster1")
    img_dir.mkdir(exist_ok=True)

    print()
    print("=" * 65)
    print("  IMAGENS CLUSTER 1 — STL Geek | 20 posts")
    print("=" * 65)
    print()

    ok, erros = 0, []

    for i, wp_id in enumerate(CLUSTER1_IDS, 1):
        slug   = id_to_slug.get(wp_id, f"post-{wp_id}")
        prompt = SLUG_PROMPT.get(slug, PROMPT_FALLBACK)
        dest   = img_dir / f"{slug}.jpg"
        alt    = slug.replace("-", " ").title() + " — Impressão 3D"

        print(f"[{i:02d}/20] wp_id={wp_id} | {slug[:45]}")

        # 1. Download Pollinations
        if not dest.exists():
            print(f"  Gerando imagem via Pollinations.ai...")
            if not _baixar_imagem(prompt, dest, seed=wp_id):
                erros.append(wp_id)
                time.sleep(5)
                continue
            time.sleep(8)  # evita rate limit 429
        else:
            print(f"  Imagem ja existe localmente, reutilizando.")

        # 2. Upload WP media
        print(f"  Enviando para WP media ({dest.stat().st_size // 1024}KB)...")
        media_id = _upload_wp(dest, alt, wp_url, session)
        if not media_id:
            erros.append(wp_id)
            continue

        # 3. Set featured_media
        if _set_featured(wp_id, media_id, wp_url, session):
            print(f"  OK featured_media={media_id}")
            ok += 1
        else:
            print(f"  ERRO ao setar featured_media")
            erros.append(wp_id)

        time.sleep(2)  # respeita rate limit WP

    print()
    print(f"  {ok}/20 imagens aplicadas com sucesso")
    if erros:
        print(f"  {len(erros)} erros nos IDs: {erros}")
    print()


if __name__ == "__main__":
    main()
