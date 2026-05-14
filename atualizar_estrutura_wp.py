"""
atualizar_estrutura_wp.py — Atualiza WP com estrutura do Cluster 1 STL Geek
- Cria categoria "STL Geek"
- Cria tags por fandom + tags comuns
- Aplica categoria + tags nos 20 posts
- Adiciona "STL Geek" ao menu primário (id=64)

Execute: python atualizar_estrutura_wp.py
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Credenciais ───────────────────────────────────────────────────────────────

def _load_env():
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def _session() -> requests.Session:
    user  = os.environ["WP_USER"]
    pwd   = os.environ["WP_PASS"]
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Basic {token}",
        "Accept":        "application/json",
        "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    return s


# ── WP helpers ────────────────────────────────────────────────────────────────

BASE = "https://clube3dbrasil.com/wp-json/wp/v2"
MENU_ID = 64  # menu "categorias" → primary location


def get_or_create_category(session: requests.Session, name: str, slug: str,
                             parent: int = 0, description: str = "") -> int:
    r = session.get(f"{BASE}/categories?slug={slug}")
    if r.ok and r.json():
        cat_id = r.json()[0]["id"]
        print(f"  Categoria já existe: '{name}' (id={cat_id})")
        return cat_id
    r = session.post(f"{BASE}/categories", json={
        "name": name, "slug": slug, "parent": parent,
        "description": description,
    })
    if r.ok:
        cat_id = r.json()["id"]
        print(f"  Categoria criada: '{name}' (id={cat_id})")
        return cat_id
    print(f"  ERRO ao criar categoria '{name}': {r.status_code} {r.text[:100]}")
    return 0


def get_or_create_tag(session: requests.Session, name: str, slug: str) -> int:
    r = session.get(f"{BASE}/tags?slug={slug}")
    if r.ok and r.json():
        return r.json()[0]["id"]
    r = session.post(f"{BASE}/tags", json={"name": name, "slug": slug})
    if r.ok:
        return r.json()["id"]
    print(f"  ERRO ao criar tag '{name}': {r.status_code} {r.text[:80]}")
    return 0


def update_post(session: requests.Session, post_id: int,
                categories: list[int], tags: list[int]) -> bool:
    r = session.get(f"{BASE}/posts/{post_id}", params={"_fields": "categories,tags"})
    if not r.ok:
        return False
    current = r.json()
    new_cats = list(set(current.get("categories", []) + categories))
    new_tags = list(set(current.get("tags", []) + tags))
    r2 = session.post(f"{BASE}/posts/{post_id}",
                      json={"categories": new_cats, "tags": new_tags})
    return r2.ok


def add_menu_item(session: requests.Session, menu_id: int, title: str,
                  url: str, order: int) -> bool:
    # Check if item already exists
    r = session.get(f"{BASE}/menu-items?menus={menu_id}&per_page=100")
    if r.ok:
        for item in r.json():
            if item.get("url", "") == url:
                print(f"  Item de menu já existe: '{title}'")
                return True
    r2 = session.post(f"{BASE}/menu-items", json={
        "title":      title,
        "url":        url,
        "menus":      menu_id,
        "menu_order": order,
        "status":     "publish",
    })
    if r2.ok:
        print(f"  Menu item criado: '{title}' (order={order})")
        return True
    print(f"  ERRO menu item '{title}': {r2.status_code} {r2.text[:100]}")
    return False


# ── Mapeamento fandom por WP ID ───────────────────────────────────────────────

POST_FANDOM = {
    2764: ("Minecraft",    "minecraft"),
    2766: ("Pokémon",      "pokemon"),
    2768: ("Naruto",       "naruto"),
    2769: ("Dragon Ball",  "dragon-ball"),
    2772: ("Marvel",       "marvel"),
    2774: ("Pokémon",      "pokemon"),
    2775: ("One Piece",    "one-piece"),
    2778: ("Naruto",       "naruto"),
    2780: ("Dragon Ball",  "dragon-ball"),
    2782: ("Demon Slayer", "demon-slayer"),
    2784: ("Marvel",       "marvel"),
    2786: ("Zelda",        "zelda"),
    2788: ("One Piece",    "one-piece"),
    2789: ("Star Wars",    "star-wars"),
    2792: ("Funko Pop",    "funko-pop"),
    2794: ("Minecraft",    "minecraft"),
    2796: ("Star Wars",    "star-wars"),
    2797: ("Demon Slayer", "demon-slayer"),
    2800: ("Zelda",        "zelda"),
    2802: ("Pokémon",      "pokemon"),
}

# Tags comuns para todos os posts do cluster
COMMON_TAGS = [
    ("STL Geek",       "stl-geek"),
    ("STL Grátis",     "stl-gratis"),
    ("impressão 3D",   "impressao-3d-tag"),
    ("fandom 3D",      "fandom-3d"),
]

# Tags por fandom
FANDOM_TAGS = {
    "Pokémon":      [("Pokémon", "pokemon-tag"), ("pikachu", "pikachu"), ("anime", "anime")],
    "Minecraft":    [("Minecraft", "minecraft-tag"), ("creeper", "creeper-tag"), ("games 3D", "games-3d")],
    "Naruto":       [("Naruto", "naruto-tag"), ("anime", "anime"), ("Akatsuki", "akatsuki-tag")],
    "Dragon Ball":  [("Dragon Ball", "dragon-ball-tag"), ("Goku", "goku-tag"), ("anime", "anime")],
    "Marvel":       [("Marvel", "marvel-tag"), ("super-herói 3D", "super-heroi-3d"), ("Homem Aranha", "homem-aranha-tag")],
    "One Piece":    [("One Piece", "one-piece-tag"), ("Luffy", "luffy-tag"), ("anime", "anime")],
    "Demon Slayer": [("Demon Slayer", "demon-slayer-tag"), ("Tanjiro", "tanjiro-tag"), ("anime", "anime")],
    "Star Wars":    [("Star Wars", "star-wars-tag"), ("Darth Vader", "darth-vader-tag"), ("sci-fi 3D", "sci-fi-3d")],
    "Zelda":        [("Zelda", "zelda-tag"), ("Link", "link-zelda-tag"), ("games 3D", "games-3d")],
    "Funko Pop":    [("Funko Pop", "funko-pop-tag"), ("colecionável", "colecionavel-3d"), ("personalizado 3D", "personalizado-3d")],
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    _load_env()
    session = _session()

    print()
    print("=" * 65)
    print("  ATUALIZAR ESTRUTURA WP — Cluster 1 STL Geek")
    print("=" * 65)

    # ── 1. Criar categoria STL Geek ──────────────────────────────────────────
    print()
    print("── 1. Categoria STL Geek ──")
    stl_geek_cat_id = get_or_create_category(
        session,
        name="STL Geek",
        slug="stl-geek",
        description="Modelos STL de fandoms — anime, games, filmes e séries para impressão 3D",
    )
    if not stl_geek_cat_id:
        print("ERRO: Falha ao criar categoria. Abortando.")
        sys.exit(1)

    # ── 2. Criar tags comuns ─────────────────────────────────────────────────
    print()
    print("── 2. Tags comuns ──")
    common_tag_ids: list[int] = []
    for name, slug in COMMON_TAGS:
        tid = get_or_create_tag(session, name, slug)
        if tid:
            common_tag_ids.append(tid)
            print(f"  OK: '{name}' (id={tid})")
        time.sleep(0.3)

    # ── 3. Criar tags por fandom ─────────────────────────────────────────────
    print()
    print("── 3. Tags por fandom ──")
    fandom_tag_ids: dict[str, list[int]] = {}
    for fandom, tag_list in FANDOM_TAGS.items():
        ids = []
        for name, slug in tag_list:
            tid = get_or_create_tag(session, name, slug)
            if tid:
                ids.append(tid)
            time.sleep(0.3)
        fandom_tag_ids[fandom] = ids
        print(f"  {fandom}: {len(ids)} tags — {ids}")

    # ── 4. Atualizar 20 posts ────────────────────────────────────────────────
    print()
    print("── 4. Atualizando 20 posts ──")
    ok = 0
    erros = []
    for i, (post_id, (fandom_name, _)) in enumerate(POST_FANDOM.items(), 1):
        all_tags = common_tag_ids + fandom_tag_ids.get(fandom_name, [])
        success = update_post(session, post_id,
                               categories=[stl_geek_cat_id],
                               tags=all_tags)
        if success:
            print(f"  [{i:02d}/20] #{post_id} ({fandom_name}) — OK")
            ok += 1
        else:
            print(f"  [{i:02d}/20] #{post_id} ({fandom_name}) — ERRO")
            erros.append(post_id)
        time.sleep(0.5)

    # ── 5. Atualizar menu ────────────────────────────────────────────────────
    print()
    print("── 5. Menu primário ──")
    menu_ok = add_menu_item(
        session,
        menu_id=MENU_ID,
        title="STL Geek",
        url="https://clube3dbrasil.com/category/stl-geek/",
        order=2,  # depois de Impressão 3D (order=1)
    )

    # ── Resumo ───────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  Categoria STL Geek:  id={stl_geek_cat_id}")
    print(f"  Tags comuns:         {len(common_tag_ids)} criadas")
    print(f"  Tags fandom:         {sum(len(v) for v in fandom_tag_ids.values())} criadas")
    print(f"  Posts atualizados:   {ok}/20")
    if erros:
        print(f"  Erros:               {erros}")
    print(f"  Menu STL Geek:       {'OK' if menu_ok else 'ERRO'}")
    print()


if __name__ == "__main__":
    main()
