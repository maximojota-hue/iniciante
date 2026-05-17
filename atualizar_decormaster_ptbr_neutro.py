"""
Corrige rascunhos Decormaster/Cults para:
- termo principal em portugues brasileiro;
- sem promessa de gratis quando a origem nao e MakerWorld.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

from publisher import WordPressPublisher


POSTS = [
    (3137, "Mario Goku", "mario-goku"),
    (3141, "Coiote Urban Vibes (Wile E. Coyote)", "coiote-urban-vibes-wile-e-coyote"),
    (3145, "Sonic Capitao America", "sonic-capitao-america"),
    (3149, "Ghostface de Panico", "ghostface-de-panico"),
    (3153, "Mulher-Maravilha Amy Rose", "mulher-maravilha-amy-rose"),
    (3157, "Homem de Ferro (Iron Man)", "homem-de-ferro-iron-man"),
    (3161, "Leatherface", "leatherface"),
    (3165, "Art, o Palhaco (Art the Clown)", "art-o-palhaco-art-the-clown"),
    (3169, "Kratos", "kratos"),
    (3173, "Busto do Goku", "busto-do-goku"),
]

TEXT_REPLACEMENTS = {
    "3MF Gratis": "3MF",
    "3MF gratis": "3MF",
    "3MF Grátis": "3MF",
    "3MF grátis": "3MF",
    "modelo 3MF gratuito": "modelo 3MF",
    "modelo 3MF gratis": "modelo 3MF",
    "modelo 3MF grátis": "modelo 3MF",
    "3MF gratuito": "3MF",
    "3MF gratuitos": "3MF",
    "3MF grátis": "3MF",
    "3MF gratis": "3MF",
}

NAME_REPLACEMENTS = {
    "Wile E. Coyote urban vibes": "Coiote Urban Vibes (Wile E. Coyote)",
    "Sonic Captain America": "Sonic Capitao America",
    "wonder amy": "Mulher-Maravilha Amy Rose",
    "Wonder Amy": "Mulher-Maravilha Amy Rose",
    "Iron Man": "Homem de Ferro (Iron Man)",
    "Art the Clown": "Art, o Palhaco (Art the Clown)",
    "busto de goku": "Busto do Goku",
}


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def neutralizar_texto(content: str, name: str) -> str:
    updated = content
    for old, new in NAME_REPLACEMENTS.items():
        updated = updated.replace(old, new)
    for old, new in TEXT_REPLACEMENTS.items():
        updated = updated.replace(old, new)
    updated = re.sub(r"\s+([:;,.])", r"\1", updated)
    updated = re.sub(r"P(?:erguntas frequentes sobre )([^<]+?)\s+3MF\s*</h2>", rf"Perguntas frequentes sobre {name} 3MF</h2>", updated)
    return updated


def main() -> None:
    carregar_env()
    pub = WordPressPublisher({
        "wp_url": os.environ.get("WP_URL", "https://clube3dbrasil.com"),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_PASS", ""),
        "wp_timeout": 60,
    })

    for post_id, name, slug_base in POSTS:
        post = pub._request("GET", f"posts/{post_id}", params={"context": "edit"})
        content = post.get("content", {}).get("raw") or post.get("content", {}).get("rendered", "")
        title = f"{name} 3MF: Fan Art para Imprimir em 3D"
        slug = slugify(f"{slug_base} 3MF impressao 3D")
        payload = {
            "title": title,
            "slug": slug,
            "content": neutralizar_texto(content, name),
            "excerpt": f"Veja o modelo 3MF do {name} e confira dicas de PLA, montagem, escala e acabamento.",
            "meta": {
                "_yoast_wpseo_focuskw": f"{name} 3MF",
                "_yoast_wpseo_title": f"{name} 3MF para Impressao 3D",
                "_yoast_wpseo_metadesc": f"Veja o {name} 3MF para imprimir em 3D, com dicas de PLA, montagem, acabamento e link para acessar a pagina no Cults.",
            },
        }
        updated = pub._request("POST", f"posts/{post_id}", json=payload)
        print(post_id, updated.get("status"), updated.get("slug"), title)


if __name__ == "__main__":
    main()
