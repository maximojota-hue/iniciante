---
name: web-trend-seo-post
description: Use before generating a Clube 3D Brasil post from web research when the task needs Brazilian and American page analysis, source comparison, SEO rewriting, and WordPress/Yoast-ready fields.
metadata:
  short-description: BR + US web research to SEO WordPress posts
  project: Clube 3D Brasil
---

# Web Trend SEO Post

Use this skill before creating a Clube 3D Brasil article from web pages,
Google-style research, competing articles, tutorials, product guides, or
international references.

Goal: research Brazilian and American pages for the same 3D printing topic,
compare angles, extract useful context, create an original PT-BR article, and
prepare a WordPress draft payload with Yoast SEO fields.

## Project Tools

Prefer existing project code:

- `gerar_post_web_pesquisa.py` searches BR and US web pages, extracts content,
  scores sources, builds a comparative context, generates a post, and can publish
  a WordPress draft with `--publicar`.
- `seo_writer.py` contains `extrair_conteudo_web()` and `gerar_post_web()`.
- `publisher.py` saves WordPress posts and Yoast meta.

## Workflow

1. Define the target angle.
   - Identify the cluster: `iniciantes`, `filamentos`, `stl-geek`, `reviews`,
     `monetizacao`, `modelagem-3d`, or `impressao-3d`.
   - Turn the topic into Brazilian Portuguese and English queries.
   - Include current intent when useful, for example `2026`, `review`,
     `configuracao`, `settings`, `guide`, `best`, `tutorial`, `STL`.

2. Search both markets.
   - Brazilian pages: add `impressao 3D`, `Brasil`, `portugues`, `configuracao`.
   - American/international pages: add `3D printing`, `guide`, `settings`,
     `review`, `tutorial`.
   - Prefer useful articles, official docs, product pages, trusted maker sites,
     model repositories, and technical guides.

3. Score each source.
   - Relevance to planned post.
   - Practical depth.
   - Fit for Clube 3D Brasil categories.
   - Source authority.
   - Brazilian adaptation value.
   - Avoid pages with thin content, social-only posts, reuploads, and pages that
     do not help a practical article.

4. Build a comparative brief.
   - What Brazilian sources emphasize.
   - What American sources emphasize.
   - Gaps the Clube 3D Brasil post can fill.
   - Terms, products, materials, printers, and settings that should be verified.

5. Rewrite into an original Brazilian article.
   - Do not copy the page text.
   - Use sources as research input only.
   - Add Brazilian maker context: local filament availability, common printers,
     cost, beginner mistakes, safety, maintenance, and marketplace potential.
   - Add FAQ, internal link opportunities, media brief, and affiliate placeholders.

6. Prepare Yoast and WordPress fields.
   - `yoast_keyphrase`: 2 to 6 words, natural search phrase.
   - `yoast_title`: starts with the keyphrase when possible.
   - `yoast_meta`: 140 to 155 characters preferred.
   - `slug`: lowercase, ASCII, kebab-case, no accents.
   - `status`: usually `draft`.

## Command

```bash
python gerar_post_web_pesquisa.py "filamento PLA silk" --categoria "Filamentos"
```

Publish as a WordPress draft:

```bash
python gerar_post_web_pesquisa.py "Bambu Lab A1 review" --categoria "Impressoras e Reviews" --publicar
```

## Output

The script saves a JSON report in `reports/` with:

- selected BR and US sources
- source scores
- generated WordPress post payload
- Yoast title, keyphrase, and meta description

## Quality Rules

- Browse/search live sources because web trends and SERPs change.
- Cite sources only as references, not copied content.
- Do not invent hands-on testing.
- Do not invent exact prices, temperatures, speeds, or compatibility.
- Mark uncertain values as recommendations to verify.
- Keep publishing as draft until images and affiliate blocks are reviewed.
