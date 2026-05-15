# Codex Quick Context

Projeto: automacao editorial e SEO do `clube3dbrasil.com`, nicho de impressao 3D.

Antes de explorar codigo, tente o `code-review-graph`. O repo esta registrado como `clube3d` e o grafo foi ativado. Se alguma estatistica voltar zerada, rode `code-review-graph build --repo "<repo>" --skip-flows` e depois o pos-processamento pelo MCP.

Memoria curta do projeto: leia primeiro `MEMORIA_ATUALIZADA_CODEX.md` antes de retomar tarefas grandes. Se precisar de historico mais antigo, consulte tambem `RESUMO_OPERACIONAL_CODEX.md`.
Controle sequencial dos posts: atualize `CONTROLE_POSTS.md` sempre que criar rascunho, publicar ou enviar chamada ao Telegram.
Controle sequencial dos afiliados: atualize `CONTROLE_AFILIADOS.md` sempre que o usuario enviar nome curto, link e foto de produto.

Regras importantes:
- Nunca exibir credenciais de `.env`, `.env.helio` ou `config.json`.
- Quando gerar post diretamente no chat, nao usar API externa de conteudo. Gerar no proprio chat.
- Quando gerar post pelo app local ou por scripts do projeto, usar o provedor configurado em `llm_provider`.
- Se houver mais de uma API cadastrada, respeitar a escolha atual de `llm_provider` (`anthropic` ou `openai`).
- Antes de gerar qualquer post, dizer claramente sobre o que sera o post.
- Depois de dizer o tema, perguntar se o usuario quer usar um afiliado cadastrado pelo numero em `CONTROLE_AFILIADOS.md`, cadastrar novo produto com nome curto/link/foto, selecionar/enviar mais 1 afiliado, ou criar sem afiliado.
- O maximo e 3 afiliados por post. Antes de criar o post, confirmar se a lista de afiliados do post esta fechada ou se o usuario quer adicionar/selecionar mais um.
- Antes de gerar o post, solicitar uma foto de capa. Se o usuario enviar, criar a arte da capa baseada nessa foto; se nao enviar, criar uma capa nova do zero coerente com o tema.
- Quando o usuario enviar nome curto, link afiliado e foto, registrar em `CONTROLE_AFILIADOS.md` com numeracao sequencial simples.
- Todo post criado deve entrar em `CONTROLE_POSTS.md` com numeracao sequencial simples e status de WordPress/Telegram.
- Preferir rascunho no WordPress ate revisar imagens e afiliados.
- Para tendencias atuais, pesquisar ao vivo antes de gerar posts.
- Para mudancas visuais, validar com Playwright quando possivel.
- Saidas locais ficam fora do Git: `reports/`, `output/`, `downloads/`, logs e caches.

Fluxos principais:
- YouTube para post SEO: `.agents/skills/youtube-trend-seo-post/`
- Web BR + US para post SEO: `gerar_post_web_pesquisa.py`
- Auditoria SEO local: `auditoria_seo_clube3d.py`
- Dashboard editorial: `dashboard_30_dias.html`
