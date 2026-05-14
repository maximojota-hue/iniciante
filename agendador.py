"""
agendador.py — Módulo 4: Agendador Automático
Roda o pipeline completo uma vez por dia no horário configurado.
Mantém log detalhado de todas as execuções.

Uso:
    python agendador.py           → inicia o agendador (roda em loop)
    python agendador.py --agora   → executa imediatamente (sem esperar o horário)
    python agendador.py --status  → mostra histórico das últimas execuções
"""

import json
import argparse
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

try:
    import schedule
except ImportError:
    print("Instalando dependência 'schedule'...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "schedule", "--break-system-packages", "-q"])
    import schedule

from scraper    import MakerWorldScraper
from gerador    import GeradorPosts
from publisher  import WordPressPublisher

CONFIG_FILE   = "config.json"
LOG_FILE      = Path("logs/execucoes.json")
LOG_TEXT_FILE = Path("logs/agendador.log")


# ── Logger ────────────────────────────────────────────────────────────────────

class Logger:
    def __init__(self):
        LOG_FILE.parent.mkdir(exist_ok=True)
        self.historico = self._carregar()

    def _carregar(self) -> list:
        if LOG_FILE.exists():
            with open(LOG_FILE, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _salvar(self):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.historico[-100:], f, indent=2, ensure_ascii=False)  # mantém só as últimas 100

    def _texto(self, msg: str):
        linha = f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {msg}"
        print(linha)
        with open(LOG_TEXT_FILE, "a", encoding="utf-8") as f:
            f.write(linha + "\n")

    def iniciar_execucao(self) -> dict:
        entrada = {
            "id":        len(self.historico) + 1,
            "inicio":    datetime.now().isoformat(),
            "fim":       None,
            "status":    "rodando",
            "coletados": 0,
            "gerados":   0,
            "publicados": 0,
            "erros":     [],
        }
        self.historico.append(entrada)
        self._salvar()
        self._texto(f"▶ EXECUÇÃO #{entrada['id']} iniciada")
        return entrada

    def finalizar_execucao(self, entrada: dict, coletados: int, gerados: int, publicados: int, erro: str = None):
        entrada.update({
            "fim":        datetime.now().isoformat(),
            "status":     "erro" if erro else "ok",
            "coletados":  coletados,
            "gerados":    gerados,
            "publicados": publicados,
        })
        if erro:
            entrada["erros"].append(erro)

        self._salvar()
        if erro:
            self._texto(f"❌ EXECUÇÃO #{entrada['id']} com erro: {erro}")
        else:
            self._texto(f"✅ EXECUÇÃO #{entrada['id']} concluída — {coletados} coletados | {gerados} gerados | {publicados} publicados")

    def status(self):
        if not self.historico:
            print("Nenhuma execução registrada ainda.")
            return

        print()
        print("=" * 62)
        print("  📋 HISTÓRICO DE EXECUÇÕES — Clube 3D Brasil")
        print("=" * 62)
        for e in reversed(self.historico[-10:]):
            status_icon = "✅" if e["status"] == "ok" else "❌" if e["status"] == "erro" else "⏳"
            inicio = e["inicio"][:16].replace("T", " ")
            print(f"  {status_icon} #{e['id']:03d} | {inicio} | "
                  f"coletados={e['coletados']} gerados={e['gerados']} publicados={e['publicados']}")
            if e.get("erros"):
                for err in e["erros"]:
                    print(f"        ⚠️  {err[:80]}")
        print("=" * 62)
        print()


# ── Pipeline ──────────────────────────────────────────────────────────────────

def carregar_config() -> dict:
    if not Path(CONFIG_FILE).exists():
        print("❌ config.json não encontrado. Execute: python setup.py")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def executar_pipeline(logger: Logger, config: dict):
    """Executa o pipeline completo: coleta → gera → publica."""
    entrada = logger.iniciar_execucao()
    coletados = gerados = publicados = 0
    limite = config.get("posts_por_dia", 10)
    top10  = config.get("top10_habilitado", False)

    try:
        # ── Etapa 1: Scraping ────────────────────────────────────────────────
        logger._texto("  📥 Etapa 1 — Coletando do MakerWorld...")
        scraper = MakerWorldScraper(config)
        modelos = scraper.run(limite=limite)
        coletados = len(modelos)
        logger._texto(f"  → {coletados} modelos coletados")

        if not modelos:
            logger.finalizar_execucao(entrada, 0, 0, 0, "Nenhum modelo coletado")
            return

        # ── Etapa 2: Geração ─────────────────────────────────────────────────
        logger._texto("  📝 Etapa 2 — Gerando posts...")
        gen  = GeradorPosts(config)
        posts = gen.processar_lote(modelos, gerar_top10=top10)
        gerados = len(posts)
        logger._texto(f"  → {gerados} posts gerados")

        if not posts:
            logger.finalizar_execucao(entrada, coletados, 0, 0, "Nenhum post gerado")
            return

        # ── Etapa 3: Publicação ──────────────────────────────────────────────
        logger._texto("  🚀 Etapa 3 — Publicando no WordPress...")
        pub  = WordPressPublisher(config)
        result = pub.publicar_lote(posts)
        publicados = len(result)
        logger._texto(f"  → {publicados} posts publicados")

        logger.finalizar_execucao(entrada, coletados, gerados, publicados)

    except Exception as e:
        erro = traceback.format_exc()
        logger._texto(f"  💥 Exceção: {e}")
        logger.finalizar_execucao(entrada, coletados, gerados, publicados, str(e))


# ── Agendador ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agendador — Clube 3D Brasil")
    parser.add_argument("--agora",   action="store_true", help="Executa imediatamente sem esperar o horário")
    parser.add_argument("--status",  action="store_true", help="Mostra histórico das execuções e sai")
    args = parser.parse_args()

    config = carregar_config()
    logger = Logger()

    if args.status:
        logger.status()
        return

    horario = config.get("horario_execucao", "09:00")

    if args.agora:
        print()
        print("▶  Executando pipeline agora (modo manual)...")
        print()
        executar_pipeline(logger, config)
        return

    # ── Modo agendado ─────────────────────────────────────────────────────────
    print()
    print("=" * 55)
    print("  ⏰ AGENDADOR CLUBE 3D BRASIL — ATIVO")
    print("=" * 55)
    print(f"  Execução diária : {horario}")
    print(f"  Limite diário   : {config.get('posts_por_dia', 10)} posts")
    print(f"  Top 10          : {'✅ habilitado' if config.get('top10_habilitado') else '❌ desabilitado'}")
    print(f"  Logs em         : logs/agendador.log")
    print()
    print("  Pressione Ctrl+C para parar o agendador.")
    print("=" * 55)
    print()

    schedule.every().day.at(horario).do(executar_pipeline, logger=logger, config=config)

    logger._texto(f"Agendador iniciado. Pipeline agendado para {horario} diariamente.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # verifica a cada 30 segundos
    except KeyboardInterrupt:
        logger._texto("Agendador encerrado pelo usuário.")
        print("\nAgendador encerrado.")


if __name__ == "__main__":
    main()
