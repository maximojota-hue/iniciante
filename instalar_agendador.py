"""
instalar_agendador.py — Registra o pipeline no Windows Task Scheduler
Execute UMA VEZ como administrador para ativar a execução automática diária.

Uso:
    python instalar_agendador.py           → instala a tarefa agendada
    python instalar_agendador.py --remover → remove a tarefa agendada
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path

NOME_TAREFA = "Clube3DBrasil_Automacao"
CONFIG_FILE = "config.json"


def carregar_config() -> dict:
    if not Path(CONFIG_FILE).exists():
        print("❌ config.json não encontrado. Execute: python setup.py")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def instalar(config: dict):
    horario = config.get("horario_execucao", "09:00")
    hora, minuto = horario.split(":")

    python_exe  = sys.executable
    script_path = Path(__file__).parent.resolve() / "agendador.py"
    pasta       = Path(__file__).parent.resolve()

    print()
    print("=" * 55)
    print("  📅 INSTALANDO TAREFA AGENDADA — WINDOWS")
    print("=" * 55)
    print(f"  Nome     : {NOME_TAREFA}")
    print(f"  Horário  : {horario} (todos os dias)")
    print(f"  Script   : {script_path}")
    print(f"  Python   : {python_exe}")
    print("=" * 55)
    print()

    # Monta o comando XML para o schtasks
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Automação diária de posts para o Clube 3D Brasil</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T{hora}:{minuto}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT4H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>{script_path} --agora</Arguments>
      <WorkingDirectory>{pasta}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    # Salva XML temporário
    xml_path = pasta / "_tarefa_temp.xml"
    xml_path.write_text(xml, encoding="utf-16")

    # Registra no Windows Task Scheduler
    try:
        resultado = subprocess.run(
            ["schtasks", "/Create", "/TN", NOME_TAREFA, "/XML", str(xml_path), "/F"],
            capture_output=True,
            text=True,
        )
        xml_path.unlink(missing_ok=True)  # Remove XML temporário

        if resultado.returncode == 0:
            print(f"✅ Tarefa '{NOME_TAREFA}' instalada com sucesso!")
            print(f"   Execução diária às {horario}.")
            print()
            print("   Para verificar: Agendador de Tarefas do Windows")
            print("   Para executar agora: python agendador.py --agora")
        else:
            print(f"❌ Erro ao instalar tarefa:")
            print(resultado.stderr)
            print()
            print("   Tente executar como Administrador.")

    except FileNotFoundError:
        xml_path.unlink(missing_ok=True)
        print("❌ 'schtasks' não encontrado. Execute no Windows.")


def remover():
    print(f"\nRemovendo tarefa '{NOME_TAREFA}'...")
    resultado = subprocess.run(
        ["schtasks", "/Delete", "/TN", NOME_TAREFA, "/F"],
        capture_output=True, text=True,
    )
    if resultado.returncode == 0:
        print(f"✅ Tarefa '{NOME_TAREFA}' removida.")
    else:
        print(f"❌ Erro: {resultado.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Instalador do agendador — Clube 3D Brasil")
    parser.add_argument("--remover", action="store_true", help="Remove a tarefa agendada")
    args = parser.parse_args()

    if args.remover:
        remover()
    else:
        config = carregar_config()
        instalar(config)


if __name__ == "__main__":
    main()
