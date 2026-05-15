"""
Cria capa 16:9 para posts de comparacao/guia de filamentos.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _fit_cover(path: str, size: tuple[int, int]) -> Image.Image:
    src = Image.open(path).convert("RGB")
    target_w, target_h = size
    src_ratio = src.width / src.height
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = max(0, (new_w - target_w) // 2)
    top = max(0, (new_h - target_h) // 2)
    return img.crop((left, top, left + target_w, top + target_h))


def criar_capa(image_a: str, image_b: str, output: str, headline: str, subheadline: str) -> Path:
    w, h = 1200, 675
    left = _fit_cover(image_a, (w // 2, h))
    right = _fit_cover(image_b, (w // 2, h))
    bg = Image.new("RGB", (w, h), (8, 12, 18))
    bg.paste(left, (0, 0))
    bg.paste(right, (w // 2, 0))
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.08)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 96))
    draw.rounded_rectangle((52, 52, 1148, 623), radius=22, outline=(76, 222, 48, 210), width=3)
    draw.rectangle((0, 0, 470, h), fill=(0, 0, 0, 112))

    badge_font = _font(28, True)
    title_font = _font(68, True)
    sub_font = _font(32, True)
    small_font = _font(24, False)

    draw.rounded_rectangle((76, 78, 318, 124), radius=12, fill=(0, 111, 255, 235))
    draw.text((96, 86), "GUIA 2026", font=badge_font, fill=(255, 255, 255, 255))

    y = 166
    for line in headline.split("|"):
        draw.text((76, y), line.strip(), font=title_font, fill=(255, 255, 255, 255))
        y += 76
    draw.text((76, y + 14), subheadline, font=sub_font, fill=(76, 222, 48, 255))

    labels = ["PLA branco", "PLA preto", "A1 Mini"]
    x = 76
    for label in labels:
        box = draw.textbbox((0, 0), label, font=small_font)
        draw.rounded_rectangle((x, 520, x + (box[2] - box[0]) + 34, 560), radius=18, fill=(4, 18, 35, 230), outline=(0, 111, 255, 190), width=2)
        draw.text((x + 16, 528), label, font=small_font, fill=(235, 242, 250, 255))
        x += (box[2] - box[0]) + 52

    draw.text((76, 586), "Clube 3D Brasil", font=small_font, fill=(224, 234, 245, 230))
    final = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    final.save(out, quality=92, optimize=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria capa 16:9 para post de filamentos.")
    parser.add_argument("--image-a", required=True)
    parser.add_argument("--image-b", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--headline", default="Melhor filamento|para A1 Mini")
    parser.add_argument("--subheadline", default="PLA branco ou preto?")
    args = parser.parse_args()
    print(criar_capa(args.image_a, args.image_b, args.output, args.headline, args.subheadline))


if __name__ == "__main__":
    main()
