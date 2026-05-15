# Clube 3D Automacao Codex

Repositorio de automacao para publicar conteudo no WordPress e organizar a operacao editorial do nicho de impressao 3D.

Para retomar o projeto rapidamente e economizar contexto, leia primeiro `RESUMO_OPERACIONAL_CODEX.md`.

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
- `dashboard_30_dias.html` - dashboard editorial com roadmap dos proximos 30 dias

### Automacoes e apoio SEO

- `cluster.py` - agrupamento editorial
- `seo_writer.py` - geracao de conteudo SEO
- `auditoria_seo_clube3d.py` - auditoria SEO local inspirada no codex-seo para tecnico, sitemap, schema, imagens, conteudo e AI readiness
- `gerar_post_web_pesquisa.py` - pesquisa paginas brasileiras e americanas, compara fontes e gera post SEO em PT-BR
- `pinterest_automacao.py` - gera artes verticais para Pinterest, lista/cria boards e publica Pins via API oficial
- `monetizacao.py` - blocos e estrutura de afiliados
- `atualizar_interlinks.py` - reforco de links internos
- `corrigir_*.py` - scripts de manutencao e ajuste editorial/SEO

### Skills do agente

- `.agents/skills/youtube-trend-seo-post/` - fluxo antes de cada post: pesquisa tendencia no YouTube, escolhe video, usa transcricao como fonte, gera post original em PT-BR e entrega campos Yoast/WordPress.
- `.agents/skills/web-trend-seo-post/` - fluxo antes de cada post baseado em paginas da web: compara fontes brasileiras e americanas, extrai contexto e gera post original em PT-BR com campos Yoast/WordPress.
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

Para gerar um post a partir de pesquisa web BR + US:

```bash
python gerar_post_web_pesquisa.py "filamento PLA silk" --categoria "Filamentos"
```

Para publicar o resultado como rascunho no WordPress:

```bash
python gerar_post_web_pesquisa.py "Bambu Lab A1 review" --categoria "Impressoras e Reviews" --publicar
```

O fluxo web tambem aceita fontes manuais, link afiliado e imagem principal:

```bash
python gerar_post_web_pesquisa.py "Bambu Lab A1 Mini vale a pena" --categoria "Impressoras e Reviews" --source-url "https://exemplo.com/review" --affiliate-url "https://link-afiliado" --affiliate-name "Bambu Lab A1 Mini" --affiliate-image "foto-produto.png" --featured-image "downloads/capas/capa.jpg" --publicar
```

Para posts com mais de um produto afiliado, use um JSON com nome, link e imagem de cada item:

```json
[
  {
    "nome": "Filamento PLA Branco",
    "link": "https://link-afiliado",
    "imagem": "F:/caminho/foto-pla-branco.png"
  },
  {
    "nome": "Filamento PLA Preto",
    "link": "https://link-afiliado",
    "imagem": "F:/caminho/foto-pla-preto.png"
  }
]
```

```bash
python gerar_post_web_pesquisa.py "melhor filamento para Bambu Lab A1 Mini" --categoria "Filamentos" --affiliates-file "afiliados.json" --featured-image "downloads/capas/capa-filamentos.jpg" --publicar
```

Para criar uma capa 16:9 a partir de uma arte de produto:

```bash
python criar_capa_afiliado.py --input "foto-produto.png" --output "downloads/capas/capa.jpg" --headline "Bambu Lab A1 Mini"
```

Para criar uma capa 16:9 comparando dois filamentos:

```bash
python criar_capa_filamentos.py --image-a "foto-pla-branco.png" --image-b "foto-pla-preto.png" --output "downloads/capas/capa-filamentos.jpg" --headline "Melhor filamento|para A1 Mini"
```

Para gerar um pacote Pinterest de 5 Pins:

```bash
python pinterest_automacao.py generate --title "Bambu Lab A1 Mini vale a pena?" --url "https://clube3dbrasil.com/?p=2991" --image "downloads/capas/bambu-lab-a1-mini-vale-a-pena-2026.jpg"
```

Para conectar a API do Pinterest:

```bash
python pinterest_automacao.py save-token
python pinterest_automacao.py boards
python pinterest_automacao.py create-board "Impressao 3D para Iniciantes"
python pinterest_automacao.py publish --manifest "output/pinterest/bambu-lab-a1-mini-vale-a-pena/pins.json" --board-id "ID_DA_BOARD"
```

Para avisar um grupo do Telegram quando um post for publicado pelo pipeline:

```bash
# No .env
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_ENABLED=true
TELEGRAM_NOTIFY_STATUSES=publish
```

```bash
python telegram_notifier.py
```

Para descobrir o `TELEGRAM_CHAT_ID`, adicione o bot no grupo, envie qualquer mensagem no grupo e rode:

```bash
python telegram_notifier.py updates
```

O aviso automatico pelo Python acontece quando o post sai com status `publish`. Para receber aviso tambem quando publicar manualmente pelo painel do WordPress, instale o snippet `wordpress_snippets/telegram_notify_on_publish.php` no Code Snippets e configure as constantes `CLUBE3D_TELEGRAM_BOT_TOKEN` e `CLUBE3D_TELEGRAM_CHAT_ID` no `wp-config.php`.

Para rodar a auditoria SEO local do Clube 3D:

```bash
python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30
```

Para salvar uma linha de base e comparar mudancas futuras:

```bash
python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30 --baseline
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
