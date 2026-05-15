# Analise dos arquivos recebidos - SEO YouTube

Arquivos avaliados:

- `SEO Blog Post Writer.md`
- `README.md`
- `mcp-setup.md`

## O que foi aproveitado

- Etapa obrigatoria de analise da transcricao antes da escrita.
- Estrutura SEO com intro curta, primeiro H2 com keyword, H2/H3 limpos, FAQ e Yoast.
- Tom mais direto, pratico e honesto.
- Checklist de qualidade separado da regra principal para economizar contexto.
- Preferencia por ferramentas gratuitas e locais antes de qualquer API paga.
- Regra de nao transformar video em resumo. O post deve virar guia original.

## O que foi descartado

- Blotato, OpenRouter/Nano Banana Pro e qualquer dependencia paga obrigatoria.
- Regras especificas do site `ryandoser.com`.
- CTA fixo de outro projeto.
- Instrucoes de MCP para Claude que nao se aplicam ao fluxo atual do Codex.
- Automacao de Mercado Livre do `README.md`, pois o arquivo nao e sobre criacao de posts.

## Decisao para o Clube 3D Brasil

Posts de YouTube agora seguem este nucleo:

1. Extrair metadados e transcricao com `yt-dlp` quando possivel.
2. Identificar promessa central, fatos uteis, numeros, erros, exemplos e lacunas.
3. Avaliar se a promessa e realista para o publico brasileiro.
4. Escrever guia original em PT-BR com SEO, nao resumo de video.
5. Incluir contexto de custo, produtos baratos/gratis, grupos, iniciantes e riscos.
6. Salvar como rascunho e revisar afiliados, capa, Yoast e interlinks.

## Arquivos atualizados

- `seo_writer.py`
- `.agents/skills/youtube-trend-seo-post/SKILL.md`
- `.agents/skills/youtube-trend-seo-post/references/youtube-post-quality.md`
- `AGENTS.md`
- `MEMORIA_ATUALIZADA_CODEX.md`
- `GUIA_POSTAGEM.md`
