"""
Automacao Pinterest para Clube 3D Brasil.

Gera artes verticais para Pinterest e publica Pins via API oficial.

Requisitos no .env:
  PINTEREST_ACCESS_TOKEN=...
  PINTEREST_BOARD_ID=...

Comandos:
  python pinterest_automacao.py save-token
  python pinterest_automacao.py boards
  python pinterest_automacao.py create-board "Impressao 3D para Iniciantes"
  python pinterest_automacao.py generate --title "Bambu Lab A1 Mini vale a pena?" --url "https://clube3dbrasil.com/?p=2991" --image "downloads/capas/capa.jpg"
  python pinterest_automacao.py publish --manifest "output/pinterest/bambu-lab-a1-mini/pins.json"
"""

from __future__ import annotations

import argparse
import base64
import csv
import getpass
import json
import os
import re
import textwrap
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


API_BASE = "https://api.pinterest.com/v5"
DEFAULT_SITE = "Clube 3D Brasil"
DEFAULT_BOARD_NAME = "Impressao 3D"


@dataclass
class PinAsset:
    title: str
    description: str
    alt_text: str
    link: str
    image_path: str


def _slug(text: str) -> str:
    value = text.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pin"


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap_text(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def carregar_env() -> None:
    load_dotenv()


def salvar_env_chave(chave: str, valor: str) -> None:
    env_path = Path(".env")
    linhas = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    novas = []
    gravou = False
    for linha in linhas:
        limpa = linha.lstrip("\ufeff")
        if limpa.startswith(f"{chave}="):
            novas.append(f"{chave}={valor}")
            gravou = True
        else:
            novas.append(linha)
    if not gravou:
        novas.append(f"{chave}={valor}")
    env_path.write_text("\n".join(novas) + "\n", encoding="utf-8")


def obter_token() -> str:
    carregar_env()
    token = os.environ.get("PINTEREST_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("PINTEREST_ACCESS_TOKEN nao encontrado no .env. Rode: python pinterest_automacao.py save-token")
    return token


def pinterest_headers() -> dict:
    return {
        "Authorization": f"Bearer {obter_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def pinterest_request(method: str, path: str, **kwargs) -> dict:
    url = f"{API_BASE}/{path.lstrip('/')}"
    resp = requests.request(method, url, headers=pinterest_headers(), timeout=45, **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(f"Pinterest API {resp.status_code}: {resp.text[:500]}")
    return resp.json() if resp.text.strip() else {}


def listar_boards() -> dict:
    return pinterest_request("GET", "boards")


def criar_board(nome: str, descricao: str = "") -> dict:
    payload = {
        "name": nome,
        "description": descricao or f"Pasta do {DEFAULT_SITE} sobre {nome}.",
        "privacy": "PUBLIC",
    }
    return pinterest_request("POST", "boards", json=payload)


def gerar_variacoes_titulos(title: str) -> list[str]:
    base = title.strip().rstrip("?")
    return [
        f"{base}?",
        f"Antes de comprar: {base}",
        f"{base}: guia para iniciantes",
        f"Vale a pena investir em {base}?",
        f"{base}: pontos fortes e limites",
    ]


def gerar_descricao(title: str, link: str) -> str:
    return (
        f"{title}. Guia do Clube 3D Brasil com dicas praticas para impressao 3D, "
        "configuracoes, cuidados e escolha certa para makers brasileiros. "
        "#impressao3d #3dprinting #maker #stl #clube3dbrasil"
    )[:500]


def criar_pin_image(base_image: str, title: str, output_path: Path, variant: int) -> Path:
    src = Image.open(base_image).convert("RGB")
    target_w, target_h = 1000, 1500
    src_ratio = src.width / src.height
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)

    bg = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = max(0, (new_w - target_w) // 2)
    top = max(0, (new_h - target_h) // 2)
    bg = bg.crop((left, top, left + target_w, top + target_h))
    bg = ImageEnhance.Color(bg).enhance(1.12)
    bg = ImageEnhance.Contrast(bg).enhance(1.1)
    bg = bg.filter(ImageFilter.GaussianBlur(1.2 if variant % 2 else 0.4))

    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, target_w, target_h), fill=(0, 0, 0, 72))
    draw.rounded_rectangle((58, 84, 942, 1320), radius=26, fill=(0, 0, 0, 88), outline=(0, 123, 255, 180), width=3)

    badge_font = _font(42, bold=True)
    title_font = _font(82 if len(title) < 36 else 70, bold=True)
    sub_font = _font(38, bold=True)
    small_font = _font(34, bold=False)

    badge_text = "CLUBE 3D BRASIL"
    draw.rounded_rectangle((92, 122, 520, 188), radius=18, fill=(0, 111, 255, 235))
    draw.text((120, 134), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    wrapped = _wrap_text(title, 16)
    draw.multiline_text((92, 270), wrapped, font=title_font, fill=(255, 255, 255, 255), spacing=14)
    draw.text((92, 980), "Guia rapido para makers brasileiros", font=sub_font, fill=(69, 222, 45, 255))

    bullets = ["Iniciantes", "Reviews", "Impressao 3D"]
    y = 1060
    for bullet in bullets:
        draw.ellipse((92, y + 8, 120, y + 36), fill=(69, 222, 45, 255))
        draw.text((138, y), bullet, font=small_font, fill=(235, 242, 250, 255))
        y += 54

    draw.rounded_rectangle((92, 1240, 650, 1320), radius=22, fill=(69, 222, 45, 245))
    draw.text((128, 1260), "LER NO BLOG", font=badge_font, fill=(0, 18, 10, 255))

    final = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, quality=92, optimize=True)
    return output_path


def gerar_pacote(title: str, link: str, image: str, output: str = "") -> Path:
    slug = _slug(title)
    out_dir = Path(output) if output else Path("output") / "pinterest" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    pins: list[PinAsset] = []
    for idx, pin_title in enumerate(gerar_variacoes_titulos(title), start=1):
        img_path = out_dir / f"pin-{idx:02d}-{_slug(pin_title)}.jpg"
        criar_pin_image(image, pin_title, img_path, idx)
        pins.append(PinAsset(
            title=pin_title[:100],
            description=gerar_descricao(pin_title, link),
            alt_text=f"{pin_title} - arte vertical do Clube 3D Brasil",
            link=link,
            image_path=str(img_path),
        ))

    manifest = out_dir / "pins.json"
    manifest.write_text(json.dumps([asdict(pin) for pin in pins], ensure_ascii=False, indent=2), encoding="utf-8")

    csv_path = out_dir / "pins.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "alt_text", "link", "image_path"])
        writer.writeheader()
        for pin in pins:
            writer.writerow(asdict(pin))

    print(f"Pacote Pinterest gerado: {out_dir}")
    print(f"Manifest: {manifest}")
    print(f"CSV: {csv_path}")
    return manifest


def publicar_pin(pin: PinAsset, board_id: str) -> dict:
    image_bytes = Path(pin.image_path).read_bytes()
    content_type = "image/png" if pin.image_path.lower().endswith(".png") else "image/jpeg"
    payload = {
        "board_id": board_id,
        "title": pin.title,
        "description": pin.description,
        "alt_text": pin.alt_text,
        "link": pin.link,
        "media_source": {
            "source_type": "image_base64",
            "content_type": content_type,
            "data": base64.b64encode(image_bytes).decode("ascii"),
        },
    }
    return pinterest_request("POST", "pins", json=payload)


def publicar_manifest(manifest_path: str, board_id: str = "") -> list[dict]:
    carregar_env()
    board_id = board_id or os.environ.get("PINTEREST_BOARD_ID", "").strip()
    if not board_id:
        raise SystemExit("Informe --board-id ou defina PINTEREST_BOARD_ID no .env.")

    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    resultados = []
    for item in data:
        pin = PinAsset(**item)
        result = publicar_pin(pin, board_id)
        resultados.append({
            "title": pin.title,
            "id": result.get("id"),
            "link": result.get("link"),
            "created_at": result.get("created_at"),
        })
        print(f"Publicado: {pin.title} | ID: {result.get('id')}")
    out = Path(manifest_path).with_name("pins-publicados.json")
    out.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultados


def salvar_token_interativo() -> None:
    token = getpass.getpass("Cole o Pinterest access token (nao sera exibido): ").strip()
    if not token:
        raise SystemExit("Token vazio. Nada foi salvo.")
    salvar_env_chave("PINTEREST_ACCESS_TOKEN", token)
    print("Token salvo no .env como PINTEREST_ACCESS_TOKEN.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Automacao Pinterest do Clube 3D Brasil.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("save-token", help="Salva PINTEREST_ACCESS_TOKEN no .env sem exibir o valor.")
    sub.add_parser("boards", help="Lista boards da conta Pinterest.")

    p_board = sub.add_parser("create-board", help="Cria uma board publica.")
    p_board.add_argument("name")
    p_board.add_argument("--description", default="")

    p_gen = sub.add_parser("generate", help="Gera pacote de 5 Pins verticais.")
    p_gen.add_argument("--title", required=True)
    p_gen.add_argument("--url", required=True)
    p_gen.add_argument("--image", required=True)
    p_gen.add_argument("--output", default="")

    p_pub = sub.add_parser("publish", help="Publica Pins de um manifest JSON.")
    p_pub.add_argument("--manifest", required=True)
    p_pub.add_argument("--board-id", default="")

    args = parser.parse_args()

    if args.cmd == "save-token":
        salvar_token_interativo()
    elif args.cmd == "boards":
        print(json.dumps(listar_boards(), ensure_ascii=False, indent=2))
    elif args.cmd == "create-board":
        result = criar_board(args.name, args.description)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get("id"):
            print(f"Para usar como padrao: PINTEREST_BOARD_ID={result['id']}")
    elif args.cmd == "generate":
        gerar_pacote(args.title, args.url, args.image, args.output)
    elif args.cmd == "publish":
        publicar_manifest(args.manifest, args.board_id)


if __name__ == "__main__":
    main()
