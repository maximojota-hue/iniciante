"""
Cria uma imagem principal 16:9 para posts afiliados a partir de uma arte base.

Uso:
  python criar_capa_afiliado.py --input "foto.png" --output "downloads/capas/capa.jpg" \
    --headline "Bambu Lab A1 Mini" --subheadline "Vale a pena para iniciantes?"
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "capa-afiliado"


def criar_capa(
    input_path: str,
    output_path: str,
    headline: str,
    subheadline: str,
    badge: str,
    cta: str,
) -> Path:
    src = Image.open(input_path).convert("RGB")
    target_w, target_h = 1200, 675
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
    top = max(0, int((new_h - target_h) * 0.36))
    bg = bg.crop((left, top, left + target_w, top + target_h))
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.12)

    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Escurece a esquerda para leitura, mantendo a impressora visivel a direita.
    for x in range(target_w):
        alpha = int(max(0, 210 - x * 0.22))
        draw.line([(x, 0), (x, target_h)], fill=(0, 0, 0, alpha))

    # Vinheta suave.
    vignette = Image.new("L", bg.size, 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, target_w, target_h), fill=0)
    vignette = vignette.filter(ImageFilter.GaussianBlur(60))

    blue = (0, 115, 255, 255)
    green = (74, 222, 48, 255)
    white = (255, 255, 255, 255)
    muted = (218, 232, 246, 255)

    title_font = _font(76, bold=True)
    sub_font = _font(34, bold=True)
    badge_font = _font(26, bold=True)
    small_font = _font(24, bold=False)

    x0, y0 = 64, 58
    draw.rounded_rectangle((x0, y0, x0 + 260, y0 + 48), radius=12, fill=(0, 115, 255, 235))
    draw.text((x0 + 18, y0 + 8), badge.upper(), font=badge_font, fill=white)

    y = y0 + 78
    for line in _wrap(draw, headline, title_font, 610)[:3]:
        draw.text((x0, y), line, font=title_font, fill=white)
        y += 78

    draw.text((x0, y + 8), subheadline, font=sub_font, fill=green)
    y += 64

    bullets = ["Compacta", "Rapida", "Facil para comecar"]
    bx = x0
    for bullet in bullets:
        tw = draw.textbbox((0, 0), bullet, font=small_font)[2]
        draw.rounded_rectangle((bx, y, bx + tw + 44, y + 42), radius=21, fill=(4, 18, 35, 230), outline=blue, width=2)
        draw.text((bx + 18, y + 8), bullet, font=small_font, fill=muted)
        bx += tw + 62

    cta_y = target_h - 104
    draw.rounded_rectangle((x0, cta_y, x0 + 420, cta_y + 56), radius=14, fill=(74, 222, 48, 245))
    draw.text((x0 + 24, cta_y + 13), cta.upper(), font=badge_font, fill=(0, 18, 10, 255))

    draw.text((x0, target_h - 38), "Clube 3D Brasil", font=small_font, fill=(220, 232, 245, 230))

    final = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    out = Path(output_path)
    if out.is_dir():
        out = out / f"{_slug(headline)}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    final.save(out, quality=92, optimize=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria capa afiliada 16:9 para WordPress.")
    parser.add_argument("--input", required=True, help="Imagem base.")
    parser.add_argument("--output", required=True, help="Arquivo de saida ou diretorio.")
    parser.add_argument("--headline", required=True, help="Titulo principal.")
    parser.add_argument("--subheadline", default="Vale a pena para iniciantes?", help="Subtitulo.")
    parser.add_argument("--badge", default="Review 2026", help="Selo superior.")
    parser.add_argument("--cta", default="Ver oferta", help="Texto do botao visual.")
    args = parser.parse_args()

    out = criar_capa(
        input_path=args.input,
        output_path=args.output,
        headline=args.headline,
        subheadline=args.subheadline,
        badge=args.badge,
        cta=args.cta,
    )
    print(out)


if __name__ == "__main__":
    main()
