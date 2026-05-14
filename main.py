"""
main.py — Orquestrador principal do Clube 3D Brasil
Execute este arquivo para iniciar a automação completa.

Uso:
    python main.py                        → pipeline completo (coleta + gera + publica)
    python main.py --limite 5             → processa 5 modelos
    python main.py --top10                → 🏆 habilita geração de posts Top 10
    python main.py --so-coletar           → só coleta do MakerWorld
    python main.py --so-gerar             → só gera posts (dados já coletados)
    python main.py --so-publicar          → só publica posts já gerados
    python main.py --top10 --so-publicar  → publica + Top 10 sem coletar
"""

import csv
import json
import logging
import os
import sys
import argparse
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from scraper   import MakerWorldScraper
from gerador   import GeradorPostsV2 as GeradorPosts
from publisher import WordPressPublisher, WordPressApiError

CONFIG_FILE           = "config.json"
POSTS_GERADOS_FILE    = Path("posts_gerados.json")
POSTS_PUBLICADOS_FILE = Path("posts_publicados.json")
STATUS_FILE           = Path("status.json")
LOG_DIR               = Path("logs")
REPORTS_DIR           = Path("reports")


def _setup_logging(level: str = "INFO") -> None:
    LOG_DIR.mkdir(exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level.upper())
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        fh = RotatingFileHandler(LOG_DIR / "clube3d.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

    if not any(isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stderr for h in root.handlers):
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        root.addHandler(ch)


logger = logging.getLogger(__name__)


# ── Utilitários ───────────────────────────────────────────────────────────────

def _carregar_env():
    env_path = Path(".env")
    if not env_path.exists():
        return
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip())


def carregar_config() -> dict:
    if not Path(CONFIG_FILE).exists():
        print("❌ config.json não encontrado. Execute: python setup.py")
        exit(1)
    _carregar_env()
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)
    config["wp_user"]         = os.environ.get("WP_USER", "")
    config["wp_app_password"] = os.environ.get("WP_PASS", "")
    if not config["wp_user"] or not config["wp_app_password"]:
        print("❌ Credenciais não encontradas. Configure o arquivo .env com WP_USER e WP_PASS.")
        exit(1)
    return config


def carregar_status() -> dict:
    if STATUS_FILE.exists():
        with open(STATUS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_status(updates: dict):
    status = carregar_status()
    status.update(updates)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def carregar_modelos_pendentes(config: dict, limite: int) -> list[dict]:
    """Modelos coletados que ainda não tiveram post gerado."""
    downloads_dir = Path(config.get("downloads_dir", "./downloads"))
    status = carregar_status()
    modelos = []
    for meta_file in sorted(downloads_dir.glob("*/meta.json")):
        slug = meta_file.parent.name
        if status.get(slug) in ("coletado", "erro_geracao"):
            with open(meta_file, encoding="utf-8") as f:
                modelos.append(json.load(f))
        if len(modelos) >= limite:
            break
    return modelos


def carregar_posts_gerados() -> list[dict]:
    """Posts gerados que ainda não foram publicados."""
    if not POSTS_GERADOS_FILE.exists():
        return []
    with open(POSTS_GERADOS_FILE, encoding="utf-8") as f:
        todos = json.load(f)
    status = carregar_status()
    return [p for p in todos if status.get(p.get("slug")) != "publicado"]


def registrar_publicados(publicados: list[dict]):
    """Salva histórico de posts publicados."""
    historico = []
    if POSTS_PUBLICADOS_FILE.exists():
        with open(POSTS_PUBLICADOS_FILE, encoding="utf-8") as f:
            historico = json.load(f)
    historico.extend(publicados)
    with open(POSTS_PUBLICADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)


# ── Relatório CSV ────────────────────────────────────────────────────────────

def _salvar_relatorio_csv(posts: list[dict], publicados: list[dict]) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = REPORTS_DIR / f"resultado_{ts}.csv"
    tmp  = path.with_suffix(".tmp")

    pub_slugs = {p["slug"]: p for p in publicados}

    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "slug", "status", "url", "resultado", "erro"])
        writer.writeheader()
        for post in posts:
            slug = post.get("slug", "")
            pub  = pub_slugs.get(slug)
            writer.writerow({
                "titulo":    post.get("titulo", ""),
                "slug":      slug,
                "status":    post.get("status", ""),
                "url":       pub["url"] if pub else "",
                "resultado": "ok" if pub else "erro",
                "erro":      "" if pub else "falha na publicação",
            })

    tmp.replace(path)
    logger.info("Relatório CSV salvo em %s", path)
    return path


# ── Retry por item ────────────────────────────────────────────────────────────

def _publicar_com_retry(publisher: WordPressPublisher, post: dict, tentativas: int = 3) -> dict | None:
    ultimo_erro = None
    for attempt in range(1, tentativas + 1):
        try:
            return publisher.publicar_post(post)
        except (WordPressApiError, Exception) as exc:
            ultimo_erro = exc
            if attempt >= tentativas:
                break
            wait = min(60, 2 ** attempt)
            logger.warning("Tentativa %d/%d falhou para '%s': %s. Aguardando %ds.",
                           attempt, tentativas, post.get("titulo", ""), exc, wait)
            time.sleep(wait)
    logger.error("Post '%s' falhou após %d tentativas: %s", post.get("titulo", ""), tentativas, ultimo_erro)
    return None


# ── Cabeçalho ─────────────────────────────────────────────────────────────────

def imprimir_cabecalho(config: dict, args):
    modo = "Completo"
    if args.so_coletar:  modo = "Só Coletar"
    elif args.so_gerar:  modo = "Só Gerar"
    elif args.so_publicar: modo = "Só Publicar"

    print()
    print("=" * 60)
    print("  🤖 CLUBE 3D BRASIL — AUTOMAÇÃO DE POSTS")
    print("=" * 60)
    print(f"  Blog     : {config['wp_url']}")
    print(f"  Planilha : {config.get('planilha_path', 'não configurada')}")
    print(f"  Limite   : {args.limite or config.get('posts_por_dia', 10)} modelos")
    print(f"  Top 10   : {'✅ HABILITADO' if args.top10 else '❌ desabilitado  (use --top10)'}")
    print(f"  Modo     : {modo}")
    print(f"  Início   : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Clube 3D Brasil — Automação de Posts WordPress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py                     Pipeline completo (coleta + gera + publica)
  python main.py --limite 5          Processa só 5 modelos
  python main.py --top10             Habilita geração de posts Top 10 por tema
  python main.py --so-coletar        Só coleta dados do MakerWorld
  python main.py --so-gerar          Só gera HTML dos dados já coletados
  python main.py --so-publicar       Só publica posts já gerados
  python main.py --top10 --so-gerar  Gera posts + Top 10 sem coletar
        """
    )
    parser.add_argument("--limite",        type=int,            help="Quantos modelos processar")
    parser.add_argument("--top10",         action="store_true", help="🏆 Habilita posts Top 10 por tema")
    parser.add_argument("--so-coletar",    action="store_true", help="Só coleta do MakerWorld")
    parser.add_argument("--so-gerar",      action="store_true", help="Só gera posts (dados já coletados)")
    parser.add_argument("--so-publicar",   action="store_true", help="Só publica posts já gerados")
    parser.add_argument("--skip-existing", action="store_true", help="Pula posts com slug já publicado no WP")
    parser.add_argument("--tentativas",    type=int, default=3, help="Tentativas por post em caso de erro")
    args = parser.parse_args()

    _setup_logging()
    config = carregar_config()
    limite = args.limite or config.get("posts_por_dia", 10)
    args.limite = limite

    imprimir_cabecalho(config, args)

    modelos  = []
    posts    = []

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 1 — Scraping MakerWorld
    # ─────────────────────────────────────────────────────────────────────────
    if not args.so_gerar and not args.so_publicar:
        print("📥 ETAPA 1 — Coletando modelos da planilha...")
        print()

        scraper = MakerWorldScraper(config)
        modelos = scraper.run(limite=limite)

        if not modelos:
            # Tenta aproveitar dados já coletados anteriormente
            modelos = carregar_modelos_pendentes(config, limite)
            if modelos:
                print(f"  ℹ️  Nenhum novo modelo. Usando {len(modelos)} coletado(s) anteriormente.")

        if not modelos:
            print("⚠️  Nenhum modelo disponível. Verifique suas coleções no MakerWorld.")
            return

        print(f"\n✅ {len(modelos)} modelo(s) disponível(is)\n")

        if args.so_coletar:
            print(f"ℹ️  Modo 'só coletar'. Dados em: {config.get('downloads_dir', './downloads')}")
            return
    else:
        print("⏭️  ETAPA 1 — Coleta pulada.\n")

    # ─────────────────────────────────────────────────────────────────────────
    # MODO --so-gerar: apenas gera, sem publicar (URLs estimadas)
    # ─────────────────────────────────────────────────────────────────────────
    if args.so_gerar:
        modelos = modelos or carregar_modelos_pendentes(config, limite)
        if not modelos:
            print("⚠️  Nenhum modelo coletado para gerar posts.")
            return
        print(f"  ℹ️  {len(modelos)} modelo(s) pendente(s) de geração.\n")
        print("📝 ETAPA 2 — Gerando posts (sem publicar)...")
        gerador = GeradorPosts(config)
        posts = gerador.processar_lote(modelos, gerar_top10=args.top10)
        if not posts:
            print("❌ Nenhum post gerado.")
            return
        with open(POSTS_GERADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        salvar_status({m.get("slug", ""): "gerado" for m in modelos})
        print(f"\n✅ {len(posts)} post(s) gerado(s) em {POSTS_GERADOS_FILE}\n")
        return

    # ─────────────────────────────────────────────────────────────────────────
    # MODO --so-publicar: publica posts já gerados (interlinks com URLs reais
    # dos posts anteriores já existentes no WP não são reconstruídos aqui)
    # ─────────────────────────────────────────────────────────────────────────
    if args.so_publicar:
        print("⏭️  ETAPA 2 — Geração pulada.\n")
        posts = carregar_posts_gerados()
        if not posts:
            print("⚠️  Nenhum post gerado encontrado em posts_gerados.json")
            return
        print(f"  ℹ️  {len(posts)} post(s) prontos para publicar.\n")

        publisher = WordPressPublisher(config)
        publicados = publisher.publicar_lote(posts, workers=3, tentativas=args.tentativas)

    # ─────────────────────────────────────────────────────────────────────────
    # PIPELINE COMPLETO: gera + publica em loop — interlinks com URLs reais
    # ─────────────────────────────────────────────────────────────────────────
    else:
        print("📝 ETAPA 2+3 — Gerando e publicando (interlinks com URLs reais)...")
        print()

        publisher = WordPressPublisher(config)
        if not publisher.testar_conexao():
            print("\n❌ Publicação cancelada: falha na autenticação.")
            return

        gerador = GeradorPosts(config)

        posts = gerador.processar_lote(modelos, gerar_top10=args.top10)
        publicados = publisher.publicar_lote(posts, workers=3, tentativas=args.tentativas)

        with open(POSTS_GERADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        salvar_status({m.get("slug", ""): "gerado" for m in modelos})

    if publicados:
        registrar_publicados(publicados)
        salvar_status({p["slug"]: "publicado" for p in publicados})

    relatorio = _salvar_relatorio_csv(posts, publicados)
    print(f"\n  📊 Relatório: {relatorio}")

    # ─────────────────────────────────────────────────────────────────────────
    # RESUMO FINAL
    # ─────────────────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  📊 RESUMO FINAL")
    print("=" * 60)
    print(f"  Modelos coletados  : {len(modelos)}")
    print(f"  Posts gerados      : {len(posts)}")
    print(f"  Posts publicados   : {len(publicados)}")
    print(f"  Erros              : {len(posts) - len(publicados)}")
    print(f"  Término            : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    if publicados:
        print()
        print("  URLs publicadas:")
        for p in publicados[:5]:
            print(f"    • {p['url']}")
        if len(publicados) > 5:
            print(f"    ... e mais {len(publicados) - 5}")
    print("=" * 60)


if __name__ == "__main__":
    main()
