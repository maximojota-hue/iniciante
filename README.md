# Clube 3D Automacao Codex

Repositorio de automacao para publicar conteudo no WordPress e organizar a operacao editorial do nicho de impressao 3D.

O projeto hoje tem duas frentes:

1. `Clube 3D Brasil` - pipeline principal de coleta, geracao e publicacao.
2. `Helio Brinquedos` - app separado para conteudo editorial e comercial de colecionaveis.

## O que mora aqui

### Codigo principal

- `main.py` - pipeline principal
- `scraper.py` - coleta dados do MakerWorld / fontes relacionadas
- `gerador.py` - gera posts HTML
- `publisher.py` - publica no WordPress
- `agendador.py` - controle de execucoes
- `setup.py` - configuracao inicial
- `instalar_agendador.py` - instala/remover tarefa agendada no Windows

### Apps e interfaces

- `app_gui.py` - interface principal do Clube 3D
- `app_helio.py` - interface separada do Helio Brinquedos
- `painel.py` - painel auxiliar
- `dashboard.html` - visualizacao local

### Automacoes e apoio SEO

- `cluster.py` - agrupamento editorial
- `seo_writer.py` - geracao de conteudo SEO
- `monetizacao.py` - blocos e estrutura de afiliados
- `atualizar_interlinks.py` - reforco de links internos
- `corrigir_*.py` - scripts de manutencao e ajuste editorial/SEO

### Skills do agente

- `.agents/skills/youtube-trend-seo-post/` - fluxo antes de cada post: pesquisa tendencia no YouTube, escolhe video, usa transcricao como fonte, gera post original em PT-BR e entrega campos Yoast/WordPress.
- `.agents/skills/yoast-seo/` - apoio para rotinas relacionadas ao Yoast SEO.

### Documentacao

- `LEIAME.md` - guia operacional detalhado
- `HANDOFF.md` - contexto tecnico e de continuidade
- `PLANO_NOVO_SITE_HELIO.md` - direcao editorial do novo site
- `CONTINUAR_HELIO.md` - continuidade do trabalho do Helio

## O que e gerado localmente

Esses arquivos e pastas sao saida de execucao, cache, logs ou dados temporarios:

- `downloads/`
- `logs/`
- `reports/`
- `posts_gerados.json`
- `posts_publicados.json`
- `posts_helio.json`
- `status.json`
- `rodizio_afiliados.json`
- `*.zip`
- `__pycache__/`

## Segredos e configuracao

Arquivos sensiveis devem ficar locais:

- `.env`
- `.env.helio`
- `config.json`

Nunca publique esses arquivos em um repo aberto.

## Como rodar

```bash
pip install -r requirements.txt
python setup.py
python app_gui.py
```

Para rodar o fluxo principal por linha de comando:

```bash
python main.py
```

## Estrutura pratica do projeto

```text
.
├── app_gui.py
├── app_helio.py
├── main.py
├── publisher.py
├── scraper.py
├── gerador.py
├── seo_writer.py
├── monetizacao.py
├── agendador.py
├── setup.py
├── instalar_agendador.py
├── LEIAME.md
├── HANDOFF.md
├── PLANO_NOVO_SITE_HELIO.md
├── downloads/
├── logs/
├── reports/
└── imagens_cluster1/
```

## Regra de manutencao

- codigo fica versionado
- saida gerada nao entra no fluxo de trabalho normal
- segredo fica fora do repo publico
- qualquer ajuste de SEO ou publicacao deve passar primeiro pelo pipeline principal
