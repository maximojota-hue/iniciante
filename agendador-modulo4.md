---
title: Agendador Automático — Módulo 4
tags: [agendador, automação, windows, task-scheduler, logs]
data: 2026-04-13
status: concluído
modulo: 4
projeto: "[[clube3d-cerebro]]"
---

# ⏰ Agendador Automático — Módulo 4

## O que faz

Executa o pipeline completo (coleta → gera → publica) automaticamente 1x por dia no horário configurado, sem nenhuma intervenção manual.

## Componentes

| Arquivo | Função |
|---|---|
| `agendador.py` | Loop Python que dispara o pipeline no horário certo |
| `instalar_agendador.py` | Registra no Windows Task Scheduler |
| `iniciar.bat` | Duplo clique para iniciar o agendador |
| `executar_agora.bat` | Duplo clique para rodar o pipeline agora |

## Duas formas de agendar

### Opção A — Windows Task Scheduler (recomendado)
Roda mesmo com o terminal fechado, na inicialização do Windows.
```bash
# Como Administrador:
python instalar_agendador.py
```

### Opção B — Agendador Python (janela aberta)
Precisa manter o terminal aberto, mas mais simples.
```bash
iniciar.bat   # ou: python agendador.py
```

## Sistema de Logs

Cada execução registra:
- Data/hora de início e fim
- Quantidade de modelos coletados, posts gerados e publicados
- Erros (se houver)

```bash
# Ver histórico
python agendador.py --status
```

Arquivos de log:
- `logs/agendador.log` — texto legível
- `logs/execucoes.json` — histórico estruturado (últimas 100)

## Configurações no config.json

| Chave | Padrão | Descrição |
|---|---|---|
| `horario_execucao` | `"09:00"` | Horário diário de execução |
| `posts_por_dia` | `10` | Limite de posts por execução |
| `top10_habilitado` | `false` | Gerar posts Top 10 automaticamente |

## Links internos

[[arquitetura-automacao]] | [[publisher-wordpress]] | [[clube3d-cerebro]]
