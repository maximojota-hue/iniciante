# Resumo Operacional Codex

Este arquivo e a memoria curta do projeto. Use para retomar trabalho sem reler toda a conversa.

## Estado do repositorio

- Repo local: `C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex`
- GitHub: `https://github.com/maximojota-hue/iniciante`
- Branch atual usada ate aqui: `master`
- Identidade Git local: `inicio codex <maximojota@gmail.com>`
- Arquivos sensiveis locais: `.env`, `.env.helio`, `config.json`
- Nao exibir credenciais em respostas, logs ou commits.
- Regra operacional atual:
  - Post gerado no chat: sem uso de API externa de conteudo.
  - Post gerado pelo app local/scripts: usar o provedor selecionado em `llm_provider`.
  - Se `ANTHROPIC_API_KEY` e `OPENAI_API_KEY` estiverem presentes, a escolha ativa fica no `config.json`.
- `code-review-graph` ativo e registrado com alias `clube3d`.
- Ultima ativacao do grafo: 60 arquivos, 528 nos, 6043 arestas, 83 fluxos e 36 comunidades.
- Wiki estrutural gerada em `.code-review-graph/wiki/`, ignorada pelo Git.

## WordPress ja ajustado

Site: `https://clube3dbrasil.com`

Alteracoes feitas via WordPress REST e Code Snippets:

- Autor publico ajustado para `Clube 3D Brasil` com slug `clube-3d-brasil`.
- Slugs duplicados corrigidos:
  - `hub-impressoras-3d`
  - `hub-filamentos-3d`
  - `hub-monetizacao-3d`
  - `hub-modelagem-3d`
- Home visual atualizada no snippet `10`, ativo:
  - Hero principal sobre `Porta-Pipoca do Bowser Jr impresso em 3D`
  - Cards de caminho: Iniciantes, STL Geek, Games & Personagens, Cosplay Maker, Reviews, Ganhar Dinheiro
- Categorias consolidadas:
  - `STL, Modelos e Personagens` slug `stl-geek`
  - `Filamentos` slug `filamentos`
  - `Ganhar Dinheiro com 3D` slug `monetizacao`
  - `Para Iniciantes` slug `iniciantes`
  - `Impressoras e Reviews` slug `reviews`
  - `Modelagem e Projetos` slug `modelagem-3d`
  - `Noticias e Tendencias` slug `impressao-3d`
- Todos os posts publicados foram normalizados para uma categoria principal.
- Categorias vazias antigas redirecionadas no snippet `11`, ativo, com 301.

## Arquivos e fluxos criados

### Planejamento editorial

- `dashboard_30_dias.html`
  - Dashboard local com plano editorial de 30 dias.
  - Inclui checklist com `localStorage`, KPIs, pipeline antes de cada post, mix editorial e calendario.

### YouTube para post SEO

- `.agents/skills/youtube-trend-seo-post/SKILL.md`
  - Pesquisa tendencias no YouTube.
  - Seleciona video, extrai metadados/transcricao, gera post original em PT-BR.
  - Entrega payload WordPress com campos Yoast.

Arquivos existentes aproveitados:

- `gerar_post_youtube.py`
- `seo_writer.py`
- `publisher.py`

### Paginas web BR + US para post SEO

- `gerar_post_web_pesquisa.py`
  - Pesquisa paginas brasileiras e americanas sobre o tema.
  - Extrai conteudo, pontua fontes, monta contexto comparativo.
  - Gera post SEO PT-BR usando `seo_writer.gerar_post_web()`.
  - Pode publicar como rascunho com `--publicar`.

Comando:

```powershell
python gerar_post_web_pesquisa.py "filamento PLA silk" --categoria "Filamentos"
```

Publicar rascunho:

```powershell
python gerar_post_web_pesquisa.py "Bambu Lab A1 review" --categoria "Impressoras e Reviews" --publicar
```

Skill criada:

- `.agents/skills/web-trend-seo-post/SKILL.md`

### Auditoria SEO inspirada no codex-seo

Foi analisado o repo `https://github.com/AgriciDaniel/codex-seo`.

Decisao: nao instalar a suite inteira porque ela e ampla e inclui DataForSEO, Google APIs, Firecrawl, mapas e backlinks. Foi implementado apenas o que tem maior retorno imediato e nao exige credenciais pagas.

Arquivo criado:

- `auditoria_seo_clube3d.py`

Ele verifica:

- robots.txt e sitemap
- title, meta description, H1, H2, canonical
- schema JSON-LD e tipos obsoletos
- imagens sem alt e sem width/height
- links internos e externos
- conteudo fino
- headers de seguranca
- prontidao para AI Overviews/LLMs
- baseline e comparacao futura

Comandos:

```powershell
python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30
python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30 --baseline
```

Primeira auditoria real:

- Score geral: `90/100`
- URLs descobertas no sitemap: `810`
- Amostra analisada: `8`
- Pontos principais: melhorar AI readiness da home e corrigir algumas imagens sem `alt` ou sem dimensoes.

### Playwright

Instalado no projeto:

- `@playwright/test`
- Chromium do Playwright
- `package.json`
- `package-lock.json`

Scripts:

```powershell
npm.cmd run pw:version
npm.cmd run pw:codegen
npm.cmd run pw:screenshot-dashboard
```

Validado:

- Playwright `1.60.0`
- Screenshot gerada para `dashboard_30_dias.html`

## Commits importantes

- `ef9fad9` Initial project import
- `db57f2d` Add project README
- `d8da79a` Add YouTube trend SEO skill
- `4df9abc` Add 30 day editorial dashboard
- `9f1c1d8` Install Playwright tooling
- `13f91a9` Add BR US web research post flow
- `a2315eb` Add Clube3D SEO audit runner

## Protocolo economico para proximas tarefas

1. Ler primeiro este arquivo e `AGENTS.md`.
2. Rodar `git status --short`.
3. Usar `rg` para achar somente o arquivo necessario.
4. Evitar reler `seo_writer.py` inteiro, pois e grande. Buscar por funcao:
   - `rg -n "def gerar_post_web|def gerar_post_seo|def extrair_conteudo_web" seo_writer.py`
5. Para SEO do site, usar primeiro:
   - `python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30`
6. Para novo post por tendencias:
   - YouTube: usar a skill `youtube-trend-seo-post`
   - Web: usar `gerar_post_web_pesquisa.py`
7. Para publicar, manter `status=draft` ate revisar imagens, afiliados e Yoast.

## Proximos passos recomendados

- Criar script para corrigir automaticamente alt text e dimensoes de imagens no WordPress.
- Rodar auditoria SEO com `--limit 100` depois das correcoes.
- Integrar `auditoria_seo_clube3d.py` ao dashboard de 30 dias.
- Criar automacao semanal de auditoria e relatorio.
- Criar fila editorial diaria usando YouTube + Web BR/US antes de cada post.
