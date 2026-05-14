"""
baixar_fotos.py — Baixa fotos dos 10 modelos e salva em downloads/{slug}/
Execute: python baixar_fotos.py
"""

import sys
import json
import time
import re
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

sys.stdout.reconfigure(encoding="utf-8")

DOWNLOADS_DIR = Path("downloads")
MAX_FOTOS     = 5  # máximo de fotos por modelo

MODELOS = [
    {"slug": "flexi-dragao-articulado",     "url": "https://www.printables.com/model/276709-flexi-dragon",                                              "plataforma": "Printables"},
    {"slug": "spider-man-print-in-place",   "url": "https://makerworld.com/en/models/120452-classic-spiderman-flexi-toy",                               "plataforma": "MakerWorld"},
    {"slug": "organizador-de-mesa-modular", "url": "https://www.printables.com/model/247588-modular-desk-organizer",                                    "plataforma": "Printables"},
    {"slug": "chaveiro-unicornio-flexi",    "url": "https://www.printables.com/model/872904-3d-flexi-unicorn-keychain-limited-time-free",               "plataforma": "Printables"},
    {"slug": "fidget-cubo-anti-stress",     "url": "https://makerworld.com/en/models/65426-fidget-cube-toy-angled",                                     "plataforma": "MakerWorld"},
    {"slug": "vaso-espiral-gyroid",         "url": "https://www.printables.com/model/70448-giroid-vase",                                               "plataforma": "Printables"},
    {"slug": "t-rex-articulado-flexi",      "url": "https://makerworld.com/en/models/622438-flexi-t-rex-dinosaur-articulated-trex-no-support",          "plataforma": "MakerWorld"},
    {"slug": "suporte-fone-de-ouvido",      "url": "https://www.printables.com/model/793818-headphone-stand-industrial",                               "plataforma": "Printables"},
    {"slug": "polvo-flexi-articulado",      "url": "https://makerworld.com/en/models/2149457-flexi-octopus-print-in-place-articulated-octopus",         "plataforma": "MakerWorld"},
    {"slug": "cubo-de-rubik-imprimivel",    "url": "https://www.printables.com/model/263468-the-worlds-first-working-print-in-place-rubiks-cub",        "plataforma": "Printables"},
]


def _goto(page, url: str, plataforma: str = ""):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except PlaywrightTimeout:
        pass
    for _ in range(10):
        time.sleep(2)
        content = page.content()
        if "security service" not in content.lower() and "verifying you are" not in content.lower():
            break

    # MakerWorld carrega imagens via JS — rolar a página força o lazy load
    if "makerworld" in url:
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
        except Exception:
            pass


def _extrair_urls_imagens(page, plataforma: str) -> list[str]:
    """Extrai URLs de imagens do modelo conforme a plataforma."""
    urls = []

    if plataforma == "Printables":
        seletores = [
            'img[src*="media.printables.com"]',
            'img[src*="cdn.printables.com"]',
            'img[class*="model"]',
            'img[class*="preview"]',
            'img[class*="photo"]',
        ]
    else:  # MakerWorld
        seletores = [
            'img[src*="media.makerworld.com"]',
            'img[src*="bbl-public"]',
            'img[src*="cdn.makerworld"]',
            'img[class*="model"]',
            'img[class*="preview"]',
            'img[class*="cover"]',
            'img[class*="slide"]',
            'img[class*="photo"]',
        ]

    for sel in seletores:
        try:
            elementos = page.locator(sel).all()
            for el in elementos:
                src = el.get_attribute("src") or ""
                if src and src.startswith("http") and any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    if src not in urls:
                        urls.append(src)
            if urls:
                break
        except Exception:
            pass

    # Fallback: todas as imagens grandes da página
    if not urls:
        try:
            todos = page.locator("img").all()
            for el in todos:
                src = el.get_attribute("src") or ""
                w   = el.get_attribute("width") or "0"
                if src.startswith("http") and int(w or 0) >= 200:
                    if src not in urls:
                        urls.append(src)
        except Exception:
            pass

    return urls[:MAX_FOTOS]


def _baixar_imagem(url: str, caminho: Path) -> bool:
    try:
        r = requests.get(url, timeout=30, stream=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(caminho, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"      ⚠️  Falha: {e}")
        return False


def _ext(url: str) -> str:
    match = re.search(r"\.(jpg|jpeg|png|webp)", url, re.IGNORECASE)
    return match.group(1).lower() if match else "jpg"


def processar(page, modelo: dict) -> int:
    slug = modelo["slug"]
    url  = modelo["url"]
    plat = modelo["plataforma"]

    pasta = DOWNLOADS_DIR / slug
    pasta.mkdir(parents=True, exist_ok=True)

    print(f"\n  🔍 [{plat}] {slug}")
    print(f"     URL: {url}")

    _goto(page, url, plat)

    urls_img = _extrair_urls_imagens(page, plat)

    if not urls_img:
        print("     ⚠️  Nenhuma imagem encontrada nessa página.")
        return 0

    print(f"     📸 {len(urls_img)} imagem(ns) encontrada(s)")
    baixadas = 0
    for i, img_url in enumerate(urls_img, start=1):
        ext  = _ext(img_url)
        dest = pasta / f"imagem-{i}.{ext}"
        ok   = _baixar_imagem(img_url, dest)
        if ok:
            print(f"      ✅ imagem-{i}.{ext}")
            baixadas += 1
        time.sleep(1)

    # Atualiza meta.json com lista de imagens
    meta_path = pasta / "meta.json"
    meta = {}
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    meta["imagens"] = [str(pasta / f"imagem-{i+1}.{_ext(u)}") for i, u in enumerate(urls_img[:baixadas])]
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return baixadas


def main():
    print()
    print("=" * 60)
    print("  📸 BAIXANDO FOTOS DOS 10 MODELOS")
    print("=" * 60)

    total_baixadas = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            for modelo in MODELOS:
                n = processar(page, modelo)
                total_baixadas += n
                time.sleep(2)
        finally:
            browser.close()

    print()
    print("=" * 60)
    print(f"  ✅ Total de fotos baixadas: {total_baixadas}")
    print("=" * 60)


if __name__ == "__main__":
    main()
