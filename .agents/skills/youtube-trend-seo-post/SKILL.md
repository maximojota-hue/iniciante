---
name: youtube-trend-seo-post
description: Use before generating a Clube 3D Brasil post when the task needs YouTube trend research in the 3D printing niche, video selection, transcript extraction, rewriting into an original PT-BR SEO blog post, and WordPress/Yoast-ready fields.
metadata:
  short-description: YouTube trends to SEO WordPress posts
  project: Clube 3D Brasil
---

# YouTube Trend SEO Post

Use this skill before creating any new Clube 3D Brasil article from a YouTube idea, URL, trend, or topic.

Goal: find the strongest YouTube signal for a 3D printing topic, extract usable context/transcript, create an original Brazilian Portuguese blog post, and return a WordPress draft payload with Yoast SEO fields. The article must read like a practical Clube 3D Brasil guide, not like a video summary.

## When To Use

- User asks to create a post from a YouTube video.
- User asks to analyze YouTube trends before writing a post.
- User provides a post topic and wants the best YouTube source for it.
- User wants a WordPress/Yoast-ready article for `clube3dbrasil.com`.

## Project Tools

Prefer existing project code when available:

- `gerar_post_youtube.py` gets YouTube metadata and can publish a draft.
- `seo_writer.py` contains `extrair_transcricao_yt()` and `gerar_post_seo()`.
- `publisher.py` saves WordPress posts and Yoast meta.
- `cluster.py` detects SEO clusters and creates interlinks.

For manual or agent-only work, still follow the same output schema below.

## Workflow

1. Define the target angle.
   - Identify the cluster: `iniciantes`, `filamentos`, `stl-geek`, `reviews`, `monetizacao`, `modelagem-3d`, or `impressao-3d`.
   - Turn the topic into 3 to 6 YouTube search queries in Portuguese and English.
   - Include year/current intent when useful, for example `2026`, `vale a pena`, `review`, `configuracao`, `tutorial`, `STL`.

2. Research YouTube trend signals.
   - Browse/search live YouTube or web results because trends change.
   - Prefer videos from the last 12 months, unless the topic is evergreen and the older video is clearly authoritative.
   - Score each candidate by relevance, freshness, view velocity, comments, creator authority, usefulness for Brazilian readers, and fit with the site category.
   - Avoid reuploads, low-context Shorts, pure entertainment with little practical detail, and videos that cannot support an article.

3. Select one primary video and optional secondary sources.
   - Use one primary YouTube URL as the anchor.
   - Use 1 to 3 secondary videos only for angle validation, not as copied material.
   - Keep the post original: do not reproduce large transcript passages.

4. Extract metadata and transcript.
   - If using code, call `extrair_metadados_yt()` from `gerar_post_youtube.py`.
   - Extract transcript with `seo_writer.extrair_transcricao_yt(url)`.
   - Prefer free/local tools first: `yt-dlp`, available subtitles, the video description, visible chapters, and public metadata.
   - Do not use paid transcript or paid content APIs when creating the post inside the chat.
   - If no transcript exists, use the video title, description, visible chapters, comments/themes, and ask for manual transcript only if the post would be weak without it.

5. Analyze before writing.
   - Extract the video's central promise.
   - Pull 3 to 5 useful facts, numbers, examples, mistakes, warnings, or practical steps.
   - Decide whether the promise is realistic for a Brazilian beginner or maker trying to save money.
   - Identify what the video does not explain and add safe general context from 3D printing knowledge.
   - Define the article angle in one sentence before drafting.

6. Rewrite into an original blog article.
   - Always write in Brazilian Portuguese.
   - Use the video as research input, not as the final article.
   - Add Brazilian maker context: printers common in Brazil, filaments available locally, beginner mistakes, cost, maintenance, safety, and practical settings.
   - Add original structure, comparisons, checklists, examples, FAQ, and internal-link opportunities.
   - Be honest about limits. Include a section on mistakes, cost, risk, or when the idea is not worth doing.
   - Do not claim Clube 3D Brasil tested the product or method unless the user provided that evidence.
   - Attribute the YouTube source naturally and include an embed block when publishing from the source URL.

7. Prepare Yoast and WordPress fields.
   - `yoast_keyphrase`: 2 to 6 words, natural search phrase.
   - `yoast_title`: starts with the keyphrase when possible, 50 to 60 characters preferred.
   - `yoast_meta`: includes the keyphrase, 140 to 155 characters preferred.
   - `slug`: lowercase, ASCII, kebab-case, no accents.
   - `excerpt`: same intent as meta, can match `yoast_meta`.
   - `status`: usually `draft`.

8. Add monetization and media placeholders, not final ads.
   - Do not invent affiliate links.
   - Mark affiliate opportunities as slots, for example `filamento PLA`, `impressora Bambu`, `bico 0.4mm`, `mesa magnetica`.
   - Provide an image brief and alt text suggestions; final images can be added later.
   - Follow the project rule: ask for affiliate IDs/new product/no affiliate and cover photo before writing a post.

## Article Rules

- Body target: 800 to 1,000 words for YouTube posts unless the user asks for more.
- Intro: 1 to 2 short sentences, keyword bolded once in the first sentence.
- First H2: short, contains the keyphrase, and answers the main search question.
- Use H2/H3 hierarchy only. No body H1 because WordPress renders the title.
- Include one early YouTube embed block when the post is based on a specific URL.
- Include 3 to 5 FAQs using real beginner questions.
- Avoid "Principais aprendizados", "Key Takeaways", generic summaries, hype, and get-rich-quick language.
- Use short paragraphs, direct Brazilian Portuguese, and practical examples.
- Zero emojis in article content.
- Zero semicolons.
- Avoid em dashes. Use commas, periods, or parentheses.

For a stricter review pass, read `references/youtube-post-quality.md`.

## Trend Score

Use a 0 to 100 score:

- Relevance to planned post: 30
- Freshness/current demand: 20
- Engagement/view velocity: 20
- Practical depth: 15
- Fit for Clube 3D Brasil categories: 10
- Monetization potential: 5

Reject candidates under 60 unless the user explicitly wants that topic.

## Output Schema

Return a compact package like this:

```json
{
  "trend": {
    "topic": "string",
    "selected_video_url": "https://www.youtube.com/watch?v=...",
    "selected_video_title": "string",
    "trend_score": 0,
    "why_this_video": ["reason"],
    "rejected_angles": ["reason"]
  },
  "wordpress_post": {
    "titulo": "string",
    "slug": "string",
    "content": "<!-- wp:paragraph -->...",
    "excerpt": "string",
    "status": "draft",
    "tags": ["impressao 3d"],
    "categories": ["Para Iniciantes"],
    "yoast_keyphrase": "string",
    "yoast_title": "string",
    "yoast_meta": "string"
  },
  "publishing_notes": {
    "affiliate_slots": ["slot"],
    "image_brief": ["image idea"],
    "alt_texts": ["alt text"],
    "internal_links": ["suggested URL or anchor"]
  }
}
```

## Quality Rules

- Do not copy the transcript as the article.
- Do not claim hands-on testing unless the project/user provided real evidence.
- Do not invent exact temperatures, speeds, prices, or compatibility; mark uncertain values as recommendations to verify.
- Include a practical FAQ when the topic has beginner questions.
- Prefer draft publishing until images and affiliate blocks are reviewed.
- Keep Yoast fields filled even when the final article still needs media.
- Reject drafts that feel like a transcript recap. The reader should get a useful Brazilian maker guide even without watching the video.
