# Memoria Atualizada Codex - Clube 3D Brasil

Use este arquivo como ponto de partida rapido antes de mexer no projeto. Ele resume o estado atual, evita reler conversas longas e reduz gasto de contexto/tokens.

## Projeto

- Site: `https://clube3dbrasil.com`
- Repo local: `C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex`
- GitHub: `https://github.com/maximojota-hue/iniciante`
- Branch usada ate aqui: `master`
- Nicho: impressao 3D no Brasil, com foco em iniciantes, STL geek, filamentos, impressoras, reviews, modelos gratis/baratos, grupos e monetizacao por afiliados/comunidade.
- Arquivos sensiveis: `.env`, `.env.helio`, `config.json`. Nunca exibir credenciais.

## Regras Operacionais

- Antes de explorar codigo, usar `code-review-graph update`.
- Para mudancas visuais, validar com Playwright quando possivel.
- Posts criados aqui no chat: gerar texto pelo proprio Codex/ChatGPT, sem chamar API externa de conteudo.
- Posts criados pelo app local/scripts: usar o provedor configurado em `llm_provider`.
- Se houver `ANTHROPIC_API_KEY` e `OPENAI_API_KEY`, respeitar a escolha ativa no app/config.
- Antes de criar qualquer post, pedir ao usuario:
  - link afiliado do produto ou produtos;
  - foto correspondente de cada produto;
  - nome curto do produto, se houver mais de um.
- Se o usuario nao tiver produto afiliado para aquele post, confirmar explicitamente que o rascunho sera criado sem afiliado.
- Publicacao WordPress deve ir como rascunho ate revisar imagem, afiliados, Yoast e interlinks.
- Para tendencias atuais, pesquisar ao vivo antes de gerar post.

## Estado Atual do Site

- Home visual principal ja foi ajustada via Code Snippets, snippet `10`.
- Categorias principais ja foram consolidadas:
  - `STL, Modelos e Personagens`
  - `Filamentos`
  - `Ganhar Dinheiro com 3D`
  - `Para Iniciantes`
  - `Impressoras e Reviews`
  - `Modelagem e Projetos`
  - `Noticias e Tendencias`
- Categorias vazias antigas foram redirecionadas com 301 no snippet `11`.
- Slugs duplicados ja foram corrigidos.
- Autor publico ajustado para `Clube 3D Brasil`.

## Hub e Bloco Whatsapp Stl

- Objetivo do hub: deixar claro que o usuario pode baixar STL gratis, entrar nos grupos, ver arquivos baratos, participar de vaquinhas e acompanhar testes reais da comunidade.
- Bloco criado/nomeado como: `Bloco Whatsapp Stl`.
- Posicao correta atual: entre os cards de `Publicados recentemente` e a secao `Entre para o maior hub de makers do Brasil`.
- Script da hub atual: `atualizar_hub_atual_stl_grupos.py`.
- Script do snippet visual da home: `atualizar_snippet10_home_comunidade.py`.
- Screenshot de validacao: `output/playwright/home-whatsapp-stl-posicao-rosa.png`.
- Ultimo commit relacionado: `5efd688 Place WhatsApp STL block before community section`.

## Fluxo de Postagem

Sequencia recomendada para cada post:

1. Definir tema prioritario pela estrategia de 30 dias.
2. Pesquisar tendencias atuais no YouTube e/ou paginas web BR + US.
3. Gerar estrutura SEO: titulo, slug, meta title, meta description, H1/H2/H3, FAQ e CTA.
4. Pedir link e foto do produto/produtos afiliados antes de escrever o post.
5. Inserir afiliados quando houver:
   - imagem do produto dentro do texto;
   - hyperlink na imagem;
   - abrir em nova aba;
   - imagem redimensionada para nao quebrar estetica.
6. Criar ou escolher imagem principal chamativa.
7. Publicar como rascunho no WordPress.
8. Revisar Yoast, categoria, interlinks e imagem destacada.
9. Publicar.
10. Apos publicar, acionar divulgacao: Telegram, Pinterest e grupos.

## Geracao de Conteudo

### YouTube

- Skill/fluxo: `.agents/skills/youtube-trend-seo-post/`
- Script relacionado: `gerar_post_youtube.py`
- Objetivo: procurar video sobre o tema, analisar transcricao/metadados, reescrever como post original em PT-BR com SEO.

### Web BR + US

- Script: `gerar_post_web_pesquisa.py`
- Objetivo: pesquisar paginas brasileiras e americanas, comparar fontes e gerar post SEO em PT-BR.
- Foi otimizado para cache, extracao paralela e modo rapido/default.
- Comando exemplo:

```powershell
python gerar_post_web_pesquisa.py "filamento PLA para iniciantes" --categoria "Filamentos"
```

### Escrita SEO

- Arquivo central: `seo_writer.py`
- Observacao tecnica: ha funcoes antigas e overrides no fim do arquivo para suporte a `anthropic` e `openai`. As definicoes finais sao as usadas pelo Python.
- Possivel melhoria futura: limpar duplicacao interna do `seo_writer.py`.

## APIs e Provedores

- `.env` contem configuracoes locais de WordPress, Telegram e chaves de IA. Nao exibir valores.
- `config.json` contem preferencias operacionais, incluindo `llm_provider`.
- App local/GUI agora permite escolher provedor: `anthropic` ou `openai`.
- `requirements.txt` inclui `openai`.
- Arquivos atualizados para escolha de provedor:
  - `app_gui.py`
  - `instalador_gui.py`
  - `setup.py`
  - `seo_writer.py`
  - `README.md`
  - `AGENTS.md`

## Telegram

- Arquivo: `telegram_notifier.py`.
- `publisher.py` envia aviso ao Telegram quando o status do post bate com `TELEGRAM_NOTIFY_STATUSES`.
- Snippet WordPress para aviso ao publicar: `wordpress_snippets/telegram_notify_on_publish.php`.
- Teste de envio ja funcionou em etapa anterior.
- Pendente importante: configurar `TELEGRAM_INVITE_URL` com o link publico do grupo/canal para aparecer como CTA no hub.

## Pinterest

- Arquivo: `pinterest_automacao.py`.
- Objetivo: automatizar pins/boards para distribuir posts e imagens do blog.
- Pendente: API/token/aprovacao de escrita do Pinterest e definicao dos boards.

## Interface Grafica

- Instalador GUI criado:
  - `instalador_gui.py`
  - `abrir_instalador_gui.bat`
- App GUI principal:
  - `app_gui.py`
- Guia do fluxo:
  - `GUIA_POSTAGEM.md`
- Objetivo da interface: guiar usuario pela sequencia de criar post, configurar APIs, escolher provedor, publicar rascunho e revisar.

## Auditoria SEO

- Script: `auditoria_seo_clube3d.py`.
- Inspirado no repo externo `AgriciDaniel/codex-seo`, mas sem instalar suite pesada.
- Verifica robots, sitemap, title, meta description, H1/H2, canonical, schema, imagens sem alt/dimensoes, links, conteudo fino, headers e AI readiness.
- Comando:

```powershell
python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 30
```

## Playwright

- Playwright instalado e usado para validacoes visuais.
- Artefatos em `output/playwright/`.
- Screenshots importantes:
  - `dashboard_30_dias.png`
  - `home-community-hub.png`
  - `home-whatsapp-stl-position.png`
  - `home-whatsapp-stl-posicao-rosa.png`

## Arquivos Mais Importantes

- `AGENTS.md`: regras do projeto para o Codex.
- `MEMORIA_ATUALIZADA_CODEX.md`: este resumo rapido.
- `RESUMO_OPERACIONAL_CODEX.md`: memoria antiga/expandida.
- `README.md`: instrucoes gerais.
- `dashboard_30_dias.html`: plano editorial visual.
- `gerar_post_web_pesquisa.py`: gerar post por paginas web BR + US.
- `gerar_post_youtube.py`: gerar post por YouTube.
- `seo_writer.py`: geracao SEO e provedor IA.
- `publisher.py`: publicacao WordPress.
- `telegram_notifier.py`: envio Telegram.
- `pinterest_automacao.py`: automacao Pinterest.
- `atualizar_snippet10_home_comunidade.py`: home visual/snippet 10.
- `atualizar_hub_atual_stl_grupos.py`: bloco de grupos/STL na hub.

## Pendencias Prioritarias

1. Configurar `TELEGRAM_INVITE_URL` para exibir CTA publico no hub.
2. Finalizar fluxo Pinterest: token, boards e teste de pin.
3. Criar proximo post prioritario com pesquisa atual e afiliado quando houver.
4. Melhorar GUI para deixar a sequencia de postagem ainda mais intuitiva.
5. Limpar duplicacao em `seo_writer.py` sem alterar comportamento.
6. Rodar nova auditoria SEO apos as proximas alteracoes.
7. Criar rotina para enviar automaticamente post publicado para Telegram e depois Pinterest.

## Comandos Frequentes

```powershell
code-review-graph update
git status --short
python -m py_compile app_gui.py instalador_gui.py setup.py seo_writer.py
python atualizar_snippet10_home_comunidade.py
python atualizar_hub_atual_stl_grupos.py
python gerar_post_web_pesquisa.py "tema do post" --categoria "Categoria"
```

## Ultimos Commits Relevantes

- `5efd688` - Place WhatsApp STL block before community section
- `d44b35d` - Reposition WhatsApp STL hub block
- `d679204` - Add configurable AI provider for local posts
- `2314ae1` - Add posting flow guide to installer
- `82512b9` - Add graphical installer
- `9a280a6` - Add home snippet community block updater
- `326ee0f` - Add current hub STL community update
- `487f364` - Optimize web post generation pipeline
