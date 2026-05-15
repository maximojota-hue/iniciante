# Codex Quick Context

Projeto: automacao editorial e SEO do `clube3dbrasil.com`, nicho de impressao 3D.

Antes de explorar codigo, tente o `code-review-graph`. O repo esta registrado como `clube3d` e o grafo foi ativado. Se alguma estatistica voltar zerada, rode `code-review-graph build --repo "<repo>" --skip-flows` e depois o pos-processamento pelo MCP.

Memoria curta do projeto: leia primeiro `MEMORIA_ATUALIZADA_CODEX.md` antes de retomar tarefas grandes. Se precisar de historico mais antigo, consulte tambem `RESUMO_OPERACIONAL_CODEX.md`.

Regras importantes:
- Nunca exibir credenciais de `.env`, `.env.helio` ou `config.json`.
- Quando gerar post diretamente no chat, nao usar API externa de conteudo. Gerar no proprio chat.
- Quando gerar post pelo app local ou por scripts do projeto, usar o provedor configurado em `llm_provider`.
- Se houver mais de uma API cadastrada, respeitar a escolha atual de `llm_provider` (`anthropic` ou `openai`).
- Antes de gerar qualquer post, perguntar ao usuario o link e a foto do produto/produtos afiliados. Se o usuario nao tiver afiliado para aquele post, confirmar que o rascunho sera criado sem bloco afiliado.
- Preferir rascunho no WordPress ate revisar imagens e afiliados.
- Para tendencias atuais, pesquisar ao vivo antes de gerar posts.
- Para mudancas visuais, validar com Playwright quando possivel.
- Saidas locais ficam fora do Git: `reports/`, `output/`, `downloads/`, logs e caches.

Fluxos principais:
- YouTube para post SEO: `.agents/skills/youtube-trend-seo-post/`
- Web BR + US para post SEO: `gerar_post_web_pesquisa.py`
- Auditoria SEO local: `auditoria_seo_clube3d.py`
- Dashboard editorial: `dashboard_30_dias.html`
