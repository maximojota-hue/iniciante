# Codex Quick Context

Projeto: automacao editorial e SEO do `clube3dbrasil.com`, nicho de impressao 3D.

Antes de explorar codigo, tente o `code-review-graph`. O repo esta registrado como `clube3d` e o grafo foi ativado. Se alguma estatistica voltar zerada, rode `code-review-graph build --repo "<repo>" --skip-flows` e depois o pos-processamento pelo MCP.

Memoria curta do projeto: leia `RESUMO_OPERACIONAL_CODEX.md` antes de retomar tarefas grandes. Ele evita reanalise cara e resume decisoes, comandos e estado atual.

Regras importantes:
- Nunca exibir credenciais de `.env`, `.env.helio` ou `config.json`.
- Preferir rascunho no WordPress ate revisar imagens e afiliados.
- Para tendencias atuais, pesquisar ao vivo antes de gerar posts.
- Para mudancas visuais, validar com Playwright quando possivel.
- Saidas locais ficam fora do Git: `reports/`, `output/`, `downloads/`, logs e caches.

Fluxos principais:
- YouTube para post SEO: `.agents/skills/youtube-trend-seo-post/`
- Web BR + US para post SEO: `gerar_post_web_pesquisa.py`
- Auditoria SEO local: `auditoria_seo_clube3d.py`
- Dashboard editorial: `dashboard_30_dias.html`
