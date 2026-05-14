"""
setup.py — Configuração inicial do sistema Clube 3D Brasil
Execute este script UMA VEZ antes de usar o sistema.
"""

import json
import getpass
from pathlib import Path

CONFIG_FILE = "config.json"

def setup():
    print("=" * 50)
    print("  CONFIGURAÇÃO — Clube 3D Brasil Automação")
    print("=" * 50)
    print()

    config = {}

    # ── Planilha ────────────────────────────────────
    print("📊 PLANILHA DE MODELOS")
    planilha = input("  Caminho completo da planilha Excel (.xlsx): ").strip().strip('"')
    if not Path(planilha).exists():
        print(f"  ⚠️  Arquivo não encontrado: {planilha}")
        print("     Verifique o caminho e execute novamente.")
        return
    config["planilha_path"] = planilha
    print()

    # ── WordPress ───────────────────────────────────
    print("🌐 WORDPRESS")
    config["wp_url"] = input("  URL do blog (ex: https://clube3dbrasil.com): ").strip().rstrip("/")
    config["wp_user"] = input("  Usuário WordPress: ").strip()
    config["wp_app_password"] = getpass.getpass("  Application Password do WordPress: ")
    print()

    # ── Configurações gerais ────────────────────────
    print("⚙️  CONFIGURAÇÕES GERAIS")
    posts_por_dia = input("  Quantos posts por dia? [padrão: 10]: ").strip()
    config["posts_por_dia"] = int(posts_por_dia) if posts_por_dia else 10

    status_wp = input("  Publicar como rascunho ou publicado? [draft/publish, padrão: draft]: ").strip()
    config["wp_post_status"] = status_wp if status_wp in ["draft", "publish"] else "draft"

    downloads_dir = input("  Pasta para salvar imagens [padrão: ./downloads]: ").strip()
    config["downloads_dir"] = downloads_dir if downloads_dir else "./downloads"
    print()

    # ── Agendador ───────────────────────────────────
    print("⏰ AGENDADOR")
    horario = input("  Horário de execução diária [padrão: 09:00]: ").strip()
    config["horario_execucao"] = horario if horario else "09:00"

    top10 = input("  Habilitar geração de posts Top 10? [s/n, padrão: n]: ").strip().lower()
    config["top10_habilitado"] = top10 in ("s", "sim", "y", "yes")
    print()

    # ── Salvar credenciais no .env ──────────────────
    wp_user = config.pop("wp_user")
    wp_pass = config.pop("wp_app_password")
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"WP_USER={wp_user}\n")
        f.write(f"WP_PASS={wp_pass}\n")
    print("✅ Credenciais salvas em '.env'  ← nunca compartilhe este arquivo")

    # ── Salvar demais configurações no config.json ──
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Configuração salva em '{CONFIG_FILE}'")
    print()
    print("Próximos passos:")
    print("  1. Instalar tarefa automática : python instalar_agendador.py  (como Administrador)")
    print("  2. Testar agora               : executar_agora.bat")
    print("  3. Iniciar agendador manual   : iniciar.bat")

if __name__ == "__main__":
    setup()
