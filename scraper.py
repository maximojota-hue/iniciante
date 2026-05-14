"""
scraper.py — Módulo 1: Scraper multi-plataforma via Planilha
Suporta MakerWorld e Printables. Usa requests + BeautifulSoup (sem browser headless).
Baixa og:image, renomeia com keyword SEO e salva localmente para upload otimizado no WP.
"""

import json
import threading
import time
import re
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def _detectar_plataforma(url: str) -> str:
    if "printables.com" in url:
        return "Printables"
    return "MakerWorld"


def _fetch_page(url: str, timeout: int = 20) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"    ⚠️  Falha ao acessar página: {e}")
        return None


def _extrair_og_image(soup: BeautifulSoup) -> str:
    tag = (soup.find("meta", property="og:image") or
           soup.find("meta", attrs={"name": "og:image"}))
    if tag:
        url = tag.get("content", "").strip()
        if url.startswith("http"):
            return url
    return ""


def _baixar_og_image(url: str, slug: str, output_dir: Path) -> str:
    """Baixa og:image, renomeia com slug SEO e salva localmente. Retorna o caminho local."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        r.raise_for_status()

        content_type = r.headers.get("content-type", "image/jpeg").lower()
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        else:
            ext = ".jpg"

        filename = f"{slug}-stl-impressao-3d{ext}"
        filepath = output_dir / filename

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"    📥 Imagem baixada: {filename}")
        return str(filepath)
    except Exception as e:
        print(f"    ⚠️  Falha ao baixar imagem: {e}")
        return ""


def _extrair_descricao(soup: BeautifulSoup) -> str:
    for prop in ["og:description", "description", "twitter:description"]:
        tag = (soup.find("meta", property=prop) or
               soup.find("meta", attrs={"name": prop}))
        if tag:
            desc = tag.get("content", "").strip()
            if len(desc) > 30:
                return desc[:300]
    return ""


class MakerWorldScraper:

    def __init__(self, config: dict):
        self.planilha_path = Path(config["planilha_path"])
        self.downloads_dir = Path(config.get("downloads_dir", "./downloads"))
        self.status_file   = Path("status.json")
        self.status        = self._load_status()
        self._lock         = threading.Lock()

    def _load_status(self) -> dict:
        if self.status_file.exists():
            with open(self.status_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_status(self):
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False)

    def _carregar_planilha(self) -> list[dict]:
        """Lê a planilha Excel e retorna modelos pendentes."""
        df = pd.read_excel(self.planilha_path)
        df.columns = [c.strip().lower() for c in df.columns]

        modelos = []
        for _, row in df.iterrows():
            status = str(row.get("status", "")).strip().lower()
            if status == "publicado":
                continue

            link = str(row.get("link", "")).strip()
            if not link or link == "nan":
                continue

            slug = self._slug_from_url(link)
            if self.status.get(slug) in ("coletado", "gerado", "publicado"):
                continue

            modelos.append({
                "slug":    slug,
                "nome":    str(row.get("nome", "")).strip(),
                "link":    link,
                "criador": str(row.get("criador", "")).strip(),
                "tema":    str(row.get("tema", "")).strip() or "Geral",
            })

        return modelos

    def _slug_from_url(self, url: str) -> str:
        parts = url.rstrip("/").split("/")
        slug = parts[-1].split("#")[0]
        return re.sub(r"[^\w-]", "-", slug.lower())[:60]

    def _scrape_model(self, modelo: dict) -> dict | None:
        slug       = modelo["slug"]
        output_dir = self.downloads_dir / slug
        output_dir.mkdir(parents=True, exist_ok=True)

        plataforma = _detectar_plataforma(modelo["link"])
        print(f"  🔍 [{plataforma}] Coletando: {modelo['nome']}")

        soup      = _fetch_page(modelo["link"])
        descricao = _extrair_descricao(soup) if soup else ""

        meta = {
            "slug":           slug,
            "nome":           modelo["nome"],
            "criador":        modelo["criador"],
            "tema":           modelo["tema"],
            "descricao":      descricao,
            "plataforma":     plataforma,
            "url_fonte":      modelo["link"],
            "url_makerworld": modelo["link"],
            "og_image":       "",
            "imagem_local":   "",
            "imagens":        [],
            "arquivo_3d":     None,
        }

        with open(output_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print(f"    ✅ Salvo: {output_dir}")
        return meta

    def run(self, limite: int = 10, workers: int = 5) -> list[dict]:
        modelos_pendentes = self._carregar_planilha()

        if not modelos_pendentes:
            print("  ℹ️  Nenhum modelo pendente na planilha.")
            return []

        processar = modelos_pendentes[:limite]
        n_workers = min(workers, len(processar))
        print(f"  📊 {len(modelos_pendentes)} pendente(s) | processando {len(processar)} com {n_workers} worker(s) em paralelo")
        print()

        resultados = []

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futuros = {executor.submit(self._scrape_model, m): m for m in processar}
            for futuro in as_completed(futuros):
                modelo = futuros[futuro]
                slug = modelo["slug"]
                try:
                    meta = futuro.result()
                except Exception as e:
                    meta = None
                    print(f"    ❌ Erro ao coletar {modelo['nome']}: {e}")
                with self._lock:
                    self.status[slug] = "coletado" if meta else "erro"
                    if meta:
                        resultados.append(meta)
                    self._save_status()

        print(f"\n  ✅ {len(resultados)} modelos coletados!")
        return resultados
