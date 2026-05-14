"""
Pesquisa paginas brasileiras e americanas sobre um tema de impressao 3D,
extrai conteudo, compara os achados e gera um post SEO em PT-BR.

Uso:
  python gerar_post_web_pesquisa.py "filamento PLA silk"
  python gerar_post_web_pesquisa.py "Bambu Lab A1 review" --categoria "Impressoras e Reviews"
  python gerar_post_web_pesquisa.py "STL Pokemon" --publicar
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

import publisher
import seo_writer

sys.stdout.reconfigure(encoding="utf-8")


BUSCA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

DOMINIOS_FRACOS = {
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "tiktok.com",
    "reddit.com",
    "x.com",
    "twitter.com",
}

DOMINIOS_FORTES = {
    "all3dp.com",
    "printables.com",
    "makerworld.com",
    "thingiverse.com",
    "prusa3d.com",
    "bambulab.com",
    "ultimaker.com",
    "creality.com",
    "3dnatives.com",
    "filament2print.com",
    "3dlab.com.br",
    "cliever.com",
    "robocore.net",
    "makerhero.com",
    "blog.render.com.br",
}


@dataclass
class ResultadoBusca:
    mercado: str
    titulo: str
    url: str
    snippet: str
    score: int = 0
    conteudo_chars: int = 0


def carregar_config_wp() -> dict:
    cfg = {}
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() == "WP_USER":
                cfg["wp_user"] = v
            if k.strip() == "WP_PASS":
                cfg["wp_app_password"] = v
            if k.strip() == "WP_URL":
                cfg["wp_url"] = v
    cfg.setdefault("wp_url", "https://clube3dbrasil.com")
    cfg["wp_post_status"] = "draft"
    return cfg


def limpar_url_duckduckgo(url: str) -> str:
    if url.startswith("//"):
        url = "https:" + url
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])
    return url


def dominio(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def dominio_raiz(url: str) -> str:
    host = dominio(url)
    parts = host.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def buscar_duckduckgo(query: str, mercado: str, limite: int) -> list[ResultadoBusca]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    resp = requests.get(url, headers=BUSCA_HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    resultados: list[ResultadoBusca] = []
    vistos = set()
    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        if not link:
            continue
        href = limpar_url_duckduckgo(link.get("href", ""))
        if not href.startswith("http"):
            continue
        root = dominio_raiz(href)
        if root in DOMINIOS_FRACOS or root in vistos:
            continue
        vistos.add(root)
        snippet_el = item.select_one(".result__snippet")
        resultados.append(ResultadoBusca(
            mercado=mercado,
            titulo=link.get_text(" ", strip=True),
            url=href,
            snippet=snippet_el.get_text(" ", strip=True) if snippet_el else "",
        ))
        if len(resultados) >= limite:
            break
    return resultados


def criar_queries(tema: str) -> dict[str, list[str]]:
    base = tema.strip()
    return {
        "br": [
            f"{base} impressao 3D Brasil",
            f"{base} impressora 3D tutorial portugues",
            f"{base} filamento configuracao impressao 3D",
        ],
        "us": [
            f"{base} 3D printing guide",
            f"{base} 3D printer settings",
            f"{base} 3D printing review tutorial",
        ],
    }


def pontuar_resultado(resultado: ResultadoBusca, tema: str, conteudo: str) -> int:
    texto = f"{resultado.titulo} {resultado.snippet} {conteudo[:1200]}".lower()
    termos = [t for t in re.split(r"\W+", tema.lower()) if len(t) >= 3]
    score = 35
    score += min(25, sum(5 for termo in termos if termo in texto))
    score += 15 if "3d" in texto or "impressao" in texto or "printing" in texto else 0
    score += 15 if resultado.mercado == "br" and (".br" in dominio(resultado.url) or "brasil" in texto) else 0
    score += 10 if dominio(resultado.url) in DOMINIOS_FORTES or dominio_raiz(resultado.url) in DOMINIOS_FORTES else 0
    score += 10 if len(conteudo) >= 1500 else 0
    score -= 20 if len(conteudo) < 500 else 0
    return max(0, min(score, 100))


def pesquisar_fontes(tema: str, por_mercado: int = 4, log_fn=print) -> list[dict]:
    queries = criar_queries(tema)
    candidatos: list[ResultadoBusca] = []
    vistos = set()

    for mercado, lista_queries in queries.items():
        for query in lista_queries:
            log_fn(f"  [{mercado.upper()}] buscando: {query}")
            try:
                for item in buscar_duckduckgo(query, mercado, por_mercado):
                    root = dominio_raiz(item.url)
                    chave = (mercado, root)
                    if chave not in vistos:
                        candidatos.append(item)
                        vistos.add(chave)
                time.sleep(1)
            except Exception as exc:
                log_fn(f"  AVISO busca falhou: {exc}")

    fontes = []
    for item in candidatos:
        extraido = seo_writer.extrair_conteudo_web(item.url, log_fn=log_fn)
        conteudo = extraido.get("conteudo", "")
        item.conteudo_chars = len(conteudo)
        item.score = pontuar_resultado(item, tema, conteudo)
        fontes.append({
            **asdict(item),
            "titulo_extraido": extraido.get("titulo", ""),
            "descricao": extraido.get("descricao", ""),
            "conteudo": conteudo,
        })

    fontes.sort(key=lambda f: (f["mercado"], -f["score"]))
    selecionadas = []
    for mercado in ("br", "us"):
        selecionadas.extend([f for f in fontes if f["mercado"] == mercado and f["score"] >= 45][:por_mercado])
    return selecionadas


def carregar_fontes_manuais(urls: list[str], tema: str, log_fn=print) -> list[dict]:
    fontes = []
    for url in urls:
        mercado = "br" if ".br" in dominio(url) or "/pt" in url.lower() else "us"
        item = ResultadoBusca(mercado=mercado, titulo=url, url=url, snippet="")
        extraido = seo_writer.extrair_conteudo_web(url, log_fn=log_fn)
        conteudo = extraido.get("conteudo", "")
        item.conteudo_chars = len(conteudo)
        item.score = pontuar_resultado(item, tema, conteudo)
        fontes.append({
            **asdict(item),
            "titulo_extraido": extraido.get("titulo", ""),
            "descricao": extraido.get("descricao", ""),
            "conteudo": conteudo,
        })
    fontes.sort(key=lambda f: (f["mercado"], -f["score"]))
    return fontes


def montar_contexto_comparativo(tema: str, fontes: list[dict]) -> tuple[str, str]:
    br = [f for f in fontes if f["mercado"] == "br"]
    us = [f for f in fontes if f["mercado"] == "us"]

    blocos = [
        f"Pesquisa comparativa para: {tema}",
        "",
        "Objetivo editorial:",
        "- Comparar o que paginas brasileiras e americanas estao cobrindo.",
        "- Adaptar as melhores ideias para makers brasileiros.",
        "- Criar texto original, sem copiar trechos das fontes.",
        "",
        "Fontes brasileiras:",
    ]

    for idx, fonte in enumerate(br, 1):
        blocos.append(
            f"{idx}. {fonte['titulo_extraido'] or fonte['titulo']} | {fonte['url']} | score {fonte['score']}\n"
            f"Resumo bruto: {fonte['conteudo'][:1200]}"
        )

    blocos.append("\nFontes americanas/internacionais:")
    for idx, fonte in enumerate(us, 1):
        blocos.append(
            f"{idx}. {fonte['titulo_extraido'] or fonte['titulo']} | {fonte['url']} | score {fonte['score']}\n"
            f"Resumo bruto: {fonte['conteudo'][:1200]}"
        )

    titulos = " | ".join((f["titulo_extraido"] or f["titulo"])[:90] for f in fontes[:4])
    urls = ", ".join(f["url"] for f in fontes[:6])
    return titulos, "\n\n".join(blocos)[:9000] + f"\n\nURLs consultadas: {urls}"


def keyword_para_secundarias(keyword: str) -> list[str]:
    base = keyword.strip().lower()
    return [
        f"{base} impressao 3d",
        f"{base} tutorial",
        f"{base} configuracao",
    ]


def copiar_imagem_afiliado(caminho: str, nome_produto: str) -> str:
    origem = Path(caminho)
    if not caminho or not origem.exists():
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", nome_produto.lower()).strip("-") or "produto-afiliado"
    destino_dir = Path("downloads") / "afiliados"
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"{slug}{origem.suffix.lower() or '.jpg'}"
    shutil.copy2(origem, destino)
    return str(destino)


def gerar_post_por_pesquisa_web(
    tema: str,
    categoria: str,
    por_mercado: int = 3,
    publicar: bool = False,
    affiliate_url: str = "",
    affiliate_name: str = "",
    affiliate_image_path: str = "",
    featured_image_path: str = "",
    source_urls: list[str] | None = None,
) -> dict:
    print("\n" + "=" * 70)
    print(f"Pesquisa web comparativa: {tema}")
    print("=" * 70)

    fontes = carregar_fontes_manuais(source_urls, tema, log_fn=print) if source_urls else []
    if not fontes:
        fontes = pesquisar_fontes(tema, por_mercado=por_mercado, log_fn=print)
    if not fontes:
        raise RuntimeError("Nenhuma fonte web util encontrada para o tema.")

    print("\nFontes selecionadas:")
    for fonte in fontes:
        print(f"  [{fonte['mercado'].upper()}] {fonte['score']:>3} | {fonte['titulo'][:72]} | {fonte['url']}")

    page_title, page_content = montar_contexto_comparativo(tema, fontes)
    afiliados_override = None
    if affiliate_url:
        imagem_afiliado = copiar_imagem_afiliado(affiliate_image_path, affiliate_name or tema)
        afiliados_override = [{
            "nome": affiliate_name or tema,
            "tipo": "impressora",
            "link": affiliate_url,
            "imagem": imagem_afiliado,
        }]

    post = seo_writer.gerar_post_web(
        keyword=tema,
        secondary_kws=keyword_para_secundarias(tema),
        page_url=fontes[0]["url"],
        page_title=page_title,
        page_content=page_content,
        categoria=categoria,
        afiliados_override=afiliados_override,
        log_fn=print,
    )
    if featured_image_path:
        post["featured_image_path"] = featured_image_path

    post["origem"] = "pesquisa_web_br_us"
    post["fontes_pesquisa"] = [
        {
            "mercado": f["mercado"],
            "titulo": f["titulo_extraido"] or f["titulo"],
            "url": f["url"],
            "score": f["score"],
        }
        for f in fontes
    ]

    saida_dir = Path("reports")
    saida_dir.mkdir(exist_ok=True)
    slug = post.get("slug") or re.sub(r"[^a-z0-9]+", "-", tema.lower()).strip("-")
    saida = saida_dir / f"pesquisa-web-{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    saida.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRelatorio salvo: {saida}")

    if publicar:
        print("\nPublicando como rascunho no WordPress...")
        cfg = carregar_config_wp()
        pub = publisher.WordPressPublisher(cfg)
        result = pub.publicar_post(post)
        post["wordpress_result"] = result
        print(f"OK: {result}")

    return post


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera post SEO via pesquisa web BR + US.")
    parser.add_argument("tema", nargs="?", help="Tema ou keyword principal do post.")
    parser.add_argument("--categoria", default="Impressao 3D", help="Categoria WordPress/SEO.")
    parser.add_argument("--por-mercado", type=int, default=3, help="Fontes por mercado BR/US.")
    parser.add_argument("--publicar", action="store_true", help="Publica como rascunho no WordPress.")
    parser.add_argument("--affiliate-url", default="", help="Link de afiliado para inserir no post.")
    parser.add_argument("--affiliate-name", default="", help="Nome do produto afiliado.")
    parser.add_argument("--affiliate-image", default="", help="Foto do produto afiliado para aparecer no texto.")
    parser.add_argument("--featured-image", default="", help="Caminho da imagem principal do post.")
    parser.add_argument("--source-url", action="append", default=[], help="URL fonte manual. Pode repetir.")
    args = parser.parse_args()

    tema = args.tema or input("Tema/keyword do post: ").strip()
    if not tema:
        raise SystemExit("Informe um tema.")

    gerar_post_por_pesquisa_web(
        tema=tema,
        categoria=args.categoria,
        por_mercado=max(1, min(args.por_mercado, 5)),
        publicar=args.publicar,
        affiliate_url=args.affiliate_url,
        affiliate_name=args.affiliate_name,
        affiliate_image_path=args.affiliate_image,
        featured_image_path=args.featured_image,
        source_urls=args.source_url,
    )


if __name__ == "__main__":
    main()
