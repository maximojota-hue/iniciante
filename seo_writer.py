"""
seo_writer.py — Gerador de posts SEO para clube3dbrasil.com
Usa Claude API para criar artigos otimizados no nicho de impressao 3D.
Posts sempre em portugues brasileiro.
"""

import os
import json
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


def _get_api_key() -> str:
    """Lê ANTHROPIC_API_KEY do ambiente ou do .env."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.lstrip("\ufeff")
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key


def traduzir_titulo_para_pt(titulo: str, log_fn=None) -> str:
    """
    Traduz o titulo do video para portugues brasileiro via Claude Haiku.
    Se ja estiver em PT-BR, retorna sem alteracao.
    """
    import anthropic

    def log(msg):
        if log_fn:
            log_fn(msg)

    if not titulo:
        return titulo

    api_key = _get_api_key()
    if not api_key:
        log("  AVISO: ANTHROPIC_API_KEY nao encontrado — titulo nao traduzido.")
        return titulo

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            system=(
                "Voce e um tradutor. Traduza o titulo para portugues brasileiro natural. "
                "Se ja estiver em portugues, retorne exatamente como esta. "
                "Responda APENAS com o titulo traduzido, sem aspas, sem explicacoes."
            ),
            messages=[{"role": "user", "content": titulo}],
        )
        traduzido = msg.content[0].text.strip().strip('"').strip("'")
        if traduzido:
            log(f"  Titulo PT-BR: {traduzido}")
            return traduzido
    except Exception as e:
        log(f"  AVISO: falha na traducao do titulo: {e}")

    return titulo


def _carregar_afiliados() -> list:
    af_path = Path("afiliados.json")
    if not af_path.exists():
        return []
    try:
        with open(af_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _escolher_afiliado(keyword: str, afiliados: list) -> dict | None:
    if not afiliados:
        return None
    kw = keyword.lower()
    MAP = {
        "impressora": ["impressora", "printer", "fdm", "resin", "resina", "ender", "bambu", "prusa"],
        "filamento":  ["filamento", "pla", "petg", "abs", "tpu", "asa", "filament"],
        "acessorio":  ["acessorio", "ferramenta", "tool", "upgrade", "bico", "nozzle", "cama", "bed"],
    }
    best, best_score = None, 0
    for af in afiliados:
        tipo  = (af.get("tipo") or "").lower()
        nome  = (af.get("nome") or af.get("nome_produto") or "").lower()
        palavras = MAP.get(tipo, [tipo, nome])
        score = sum(1 for p in palavras if p and p in kw)
        if score > best_score:
            best_score, best = score, af
    return best or (afiliados[0] if afiliados else None)


def extrair_transcricao_yt(url: str, log_fn=None) -> str:
    """
    Extrai transcricao via yt-dlp.
    Tenta PT/EN primeiro; fallback para qualquer idioma disponivel.
    Claude escreve o post em PT-BR independente do idioma da transcricao.
    """
    def log(msg):
        if log_fn:
            log_fn(msg)

    log("  [yt-dlp] Extraindo transcricao...")

    def _baixar_vtt(sub_langs: str, prefix: str) -> None:
        subprocess.run(
            ["yt-dlp",
             "--write-subs", "--write-auto-subs",
             "--sub-langs", sub_langs,
             "--skip-download",
             "--output", f"{tmpdir}/{prefix}",
             "--sub-format", "vtt",
             url],
            capture_output=True, text=True, timeout=90,
            check=False, encoding="utf-8",
        )

    def _parsear_vtt(vtt_file: Path) -> str:
        txt = vtt_file.read_text(encoding="utf-8", errors="ignore")
        lines, seen = [], set()
        for line in txt.splitlines():
            line = line.strip()
            if not line or "-->" in line or line.startswith("WEBVTT"):
                continue
            if re.match(r"^\d{2}:\d{2}", line):
                continue
            line = re.sub(r"<[^>]+>", "", line).strip()
            if line and line not in seen:
                seen.add(line)
                lines.append(line)
        return " ".join(lines)[:6000]

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Tentativa 1: legendas em PT ou EN (mais rápido, sem necessidade de tradução)
            _baixar_vtt("pt,pt-BR,pt-br,en,en-US,en-orig", "video")
            vtt_files = sorted(Path(tmpdir).glob("*.vtt"))

            # Tentativa 2: qualquer idioma disponivel no vídeo
            if not vtt_files:
                log("  Sem legenda PT/EN — buscando qualquer idioma disponivel...")
                _baixar_vtt("all", "video_any")
                vtt_files = sorted(Path(tmpdir).glob("*.vtt"))

            for vtt_file in vtt_files:
                transcript = _parsear_vtt(vtt_file)
                if transcript:
                    # Extrai codigo do idioma do nome do arquivo (ex: video.zh-Hans.vtt)
                    stem_parts = vtt_file.stem.split(".")
                    lang_code = stem_parts[-1] if len(stem_parts) > 1 else "?"
                    log(f"  OK Transcricao extraida ({len(transcript)} chars) [{lang_code}]")
                    return transcript

        log("  AVISO Nenhuma legenda encontrada para este video.")
    except FileNotFoundError:
        log("  AVISO yt-dlp nao instalado. Instale com: pip install yt-dlp")
    except Exception as e:
        log(f"  ERRO ao extrair transcricao: {e}")
    return ""


# ── Web scraper ────────────────────────────────────────────────────────────────

def _jina_fallback(url: str, log) -> tuple[str, str, str]:
    """Usa Jina AI Reader para extrair conteudo de paginas JS/Cloudflare."""
    import requests as _req
    jina_url = f"https://r.jina.ai/{url}"
    try:
        resp = _req.get(
            jina_url,
            headers={"Accept": "text/plain", "User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        if resp.ok:
            text = resp.text.strip()
            lines = text.splitlines()

            # Jina retorna "Title: ..." e "URL Source: ..." no cabecalho
            titulo = ""
            corpo_inicio = 0
            for i, line in enumerate(lines):
                if line.startswith("Title:"):
                    titulo = line.removeprefix("Title:").strip()
                if line.strip() == "" and titulo:
                    corpo_inicio = i + 1
                    break

            conteudo = "\n".join(lines[corpo_inicio:]).strip()
            conteudo = re.sub(r"\n{3,}", "\n\n", conteudo)[:6000]
            log(f"  OK Jina Reader: {len(conteudo)} chars | titulo: {titulo[:60]}")
            return titulo, "", conteudo
    except Exception as e:
        log(f"  ERRO Jina Reader: {e}")
    return "", "", ""


def extrair_conteudo_web(url: str, log_fn=None) -> dict:
    """
    Extrai titulo e conteudo de uma pagina web via requests+BeautifulSoup.
    Retorna dict com: titulo, descricao, conteudo (ate 6000 chars), url.
    """
    def log(msg):
        if log_fn:
            log_fn(msg)

    log(f"  [web] Acessando: {url}")

    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Titulo
        titulo = ""
        if soup.title:
            titulo = soup.title.get_text(strip=True)
        if not titulo:
            og = soup.find("meta", property="og:title")
            if og:
                titulo = og.get("content", "")

        # Meta descricao
        descricao = ""
        md = soup.find("meta", attrs={"name": "description"})
        if md:
            descricao = md.get("content", "")
        if not descricao:
            og_d = soup.find("meta", property="og:description")
            if og_d:
                descricao = og_d.get("content", "")

        # Remove ruido
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "form", "iframe", "noscript"]):
            tag.decompose()

        # Area de conteudo principal
        main = (
            soup.find("main") or
            soup.find("article") or
            soup.find(id=re.compile(r"content|main|article|post|entry", re.I)) or
            soup.find(class_=re.compile(r"content|main|article|post|entry", re.I)) or
            soup.body
        )

        raw_text = (main or soup).get_text(separator=" ", strip=True)
        conteudo  = re.sub(r"\s{2,}", " ", raw_text).strip()[:6000]

        log(f"  OK Titulo: {titulo[:70]}")
        log(f"  OK Conteudo: {len(conteudo)} chars extraidos")

        # Fallback Jina se conteudo insuficiente (paginas JS/Cloudflare)
        if len(conteudo) < 300:
            log("  Conteudo insuficiente — tentando Jina AI Reader...")
            titulo, descricao, conteudo = _jina_fallback(url, log)

        return {"titulo": titulo, "descricao": descricao, "conteudo": conteudo, "url": url}

    except Exception as e:
        log(f"  ERRO ao acessar pagina: {e} — tentando Jina AI Reader...")
        titulo, descricao, conteudo = _jina_fallback(url, log)
        return {"titulo": titulo, "descricao": descricao, "conteudo": conteudo, "url": url}


# ── Prompts Web (3D printing por categoria) ────────────────────────────────────

_WEB_CAT_ANGULO = {
    "STL Geek": (
        "Este post e uma CURADORIA de modelos STL de fandom (anime, games, filmes, series) para impressao 3D. "
        "Foque em: onde encontrar os melhores STLs gratuitos deste fandom (Printables, Thingiverse, MakerWorld), "
        "quais personagens tem mais downloads e por que, filamento ideal por cor do personagem "
        "(ex: PLA vermelho para Pokeball, PLA laranja para Goku), configuracoes de impressao para figuras com detalhes finos "
        "(layer height 0.1-0.15mm, infill 15-20%), dicas de pintura e acabamento para colecionaveis, "
        "potencial de venda na Shopee e Elo7. "
        "Tom apaixonado pelo fandom + tecnico para makers. Mencione sempre Printables e Thingiverse como fontes."
    ),
    "Personagens": (
        "Este post e sobre PERSONAGENS para impressao 3D (figuras, miniaturas, action figures, bustos). "
        "Foque em: personagens em tendencia (anime, games, filmes), materiais ideais (resina vs PLA), "
        "dicas de pintura e acabamento, onde encontrar STLs gratuitos e pagos."
    ),
    "Chaveiros": (
        "Este post e sobre CHAVEIROS de impressao 3D. "
        "Foque em: designs populares e personalizados, materiais leves (PLA, PETG), "
        "acabamento e pintura, potencial de venda, dicas de impressao para pecas pequenas."
    ),
    "Vasos": (
        "Este post e sobre VASOS impressos em 3D. "
        "Foque em: modo vaso (vase mode / spiralize outer contour), filamentos decorativos "
        "(madeira, marmore, seda, metalico), designs organicos, compatibilidade com plantas reais, "
        "decoracao de interiores."
    ),
    "Flexivel": (
        "Este post e sobre IMPRESSAO FLEXIVEL em 3D com TPU, TPE ou NinjaFlex. "
        "Foque em: configuracoes de impressao para materiais flexiveis (retraction, velocidade, temperatura), "
        "casos de uso praticos (cases, solas, juntas, articulados), dicas de aderencia e acabamento."
    ),
    "Croche": (
        "Este post e sobre IMPRESSAO 3D ESTILO CROCHE (texturas de malha, padroes de croche em FDM). "
        "Foque em: como obter textura de croche com impressao 3D, filamentos recomendados (PLA seda, PLA matte), "
        "projetos de decoracao e moda, STLs com padrao de croche, configuracoes de layer height para textura."
    ),
}


def _build_system_prompt_web(categoria: str) -> str:
    angulo = _WEB_CAT_ANGULO.get(categoria, "")
    base = (
        "Voce e um redator SEO especializado em impressao 3D, escrevendo para clube3dbrasil.com.\n"
        "Escreva SEMPRE em portugues brasileiro.\n"
        "Tom tecnico-amigavel, direto e util para makers brasileiros.\n"
    )
    if angulo:
        base += f"\n{angulo}\n"
    base += "Responda SEMPRE com um JSON valido, sem texto fora do JSON."
    return base


def _build_user_prompt_web(
    keyword: str,
    secondary_kws: list,
    page_title: str,
    page_content: str,
    page_url: str,
    categoria: str,
) -> str:
    secondary = ", ".join(secondary_kws) if secondary_kws else "nenhuma"

    page_block = ""
    if page_title or page_content:
        page_block = (
            f"\n### Conteudo da pagina de referencia ({page_url}):\n"
            f"Titulo: {page_title}\n"
            f"{page_content[:4000]}\n"
        )

    cat_tag = categoria if categoria else "Impressao 3D"
    faq_heading = f"{keyword} - Perguntas Frequentes"

    return f"""Crie um post de blog SEO sobre impressao 3D para clube3dbrasil.com:

**Keyword principal:** {keyword}
**Keywords secundarias:** {secondary}
**Categoria do post:** {cat_tag}
{page_block}
## ESTRUTURA DO post_content (HTML para WordPress - NAO inclua tag H1):

1. `<p>` introducao: 1-2 frases. Keyword em `<strong>` apenas na primeira frase.
2. `<h2><strong>` Primeiro H2: contem a keyword, curto (max. 7 palavras).
3. Conteudo do primeiro H2 (2-3 paragrafos uteis).
4. Mais 3-4 secoes `<h2><strong>` com conteudo tecnico-pratico relacionado ao tema.
5. `<h2><strong>Consideracoes Finais</strong></h2>` - resumo de 2-3 paragrafos.
6. `<h2><strong>{faq_heading}</strong></h2>` - 3-5 perguntas como `<h3><strong>Pergunta?</strong></h3>` + resposta de 40-80 palavras cada.

## REGRAS DE TEXTO:
- Portugues brasileiro, frases curtas (8-15 palavras), max. 4 frases por paragrafo
- 900-1.100 palavras totais no post_content
- Keyword principal: max. 4 ocorrencias
- ZERO emojis, ZERO travessao (-), ZERO ponto e virgula
- Links externos (2-3): fontes confiaveis como Printables, MakerWorld, Thingiverse, Prusa, Bambu Lab — sempre com target="_blank" rel="noopener noreferrer"
- Palavras PROIBIDAS: mergulhar, navegar, robusto, crucial, garantir, alavancar, transformador, revolucionario, "vale a pena notar", "e importante mencionar", "sem mais delongas", "no mundo de hoje", "a verdade e que"

## RESPONDA APENAS COM JSON VALIDO (sem markdown, sem texto fora do JSON):

{{"titulo": "Titulo ate 65 chars com keyword no inicio", "seo_title": "Titulo SEO 55-65 chars", "meta_description": "Meta ate 155 chars com keyword", "slug": "keyword-em-kebab-case", "tags": ["impressao 3d", "{cat_tag.lower()}", "{keyword}"], "categoria": "{cat_tag}", "post_content": "<p>Introducao com <strong>{keyword}</strong>...</p><h2><strong>H2 com keyword</strong></h2>..."}}"""


def gerar_post_web(
    keyword: str,
    secondary_kws: list = None,
    page_url: str = "",
    page_title: str = "",
    page_content: str = "",
    categoria: str = "Impressao 3D",
    afiliados_override: list = None,
    log_fn=None,
) -> dict:
    """
    Gera post SEO a partir de conteudo de pagina web (sem YouTube).
    Sempre em PT-BR, sempre sobre impressao 3D.
    """
    import anthropic

    def log(msg):
        if log_fn:
            log_fn(msg)
        else:
            print(msg)

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY nao encontrado. Adicione no arquivo .env do projeto.")

    if secondary_kws is None:
        secondary_kws = []

    log(f"  Categoria: {categoria}")

    # Afiliados
    if afiliados_override is not None:
        afiliados_para_post = afiliados_override
    else:
        todos = _carregar_afiliados()
        af = _escolher_afiliado(keyword, todos)
        afiliados_para_post = [af] if af else []

    if afiliados_para_post:
        nomes = [a.get("nome") or a.get("nome_produto", "") for a in afiliados_para_post]
        log(f"  Afiliado(s): {', '.join(nomes)}")
    else:
        log("  Sem afiliado para este post.")

    log("  Chamando Claude API (haiku)...")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_user_prompt_web(
        keyword, secondary_kws, page_title, page_content, page_url, categoria,
    )
    raw = ""

    for attempt in range(1, 3):
        user_msg = prompt if attempt == 1 else (
            "O JSON abaixo esta invalido. Retorne APENAS o JSON corrigido e completo, "
            "sem markdown, sem texto adicional:\n\n" + raw
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=_build_system_prompt_web(categoria),
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = _reparar_json(message.content[0].text.strip())
        try:
            data = json.loads(raw)
            break
        except json.JSONDecodeError as e:
            if attempt == 2:
                log(f"  ERRO JSON invalido apos 2 tentativas: {e}")
                raise
            log("  AVISO JSON invalido — solicitando correcao ao modelo...")

    slug_clean = re.sub(r"[^a-z0-9]+", "-", keyword.lower()).strip("-")

    post_content = data.get("post_content", "")
    post_content += _gerar_faq_schema_do_content(post_content)
    post_content = _injetar_blocos_afiliados(post_content, afiliados_para_post)
    contexto_download = f"{keyword} {categoria} {page_title}".lower()
    if any(term in contexto_download for term in ("stl", "download", "modelo", "personagem")):
        post_content = _injetar_download_antes_faq(post_content, page_url, page_title)
    post_content += _bloco_bridge_renda_extra()

    post = {
        "titulo":              data.get("titulo", keyword),
        "slug":                data.get("slug", slug_clean),
        "content":             post_content,
        "excerpt":             data.get("meta_description", ""),
        "status":              "draft",
        "tags":                data.get("tags", ["impressao 3d", keyword]),
        "categories":          [data.get("categoria", categoria)],
        "featured_image_path": "",
        "yoast_keyphrase":     keyword,
        "yoast_title":         data.get("seo_title", ""),
        "yoast_meta":          data.get("meta_description", ""),
        "gerado_em":           datetime.now().isoformat(),
        "origem":              "seo_writer_web",
    }

    log(f"  Post gerado: {post['titulo']}")
    log(f"  Meta ({len(post['yoast_meta'])} chars): {post['yoast_meta']}")
    return post


RENDA_EXTRA_KEYWORDS = [
    "vender", "venda", "renda", "ganhar", "ganho", "lucro", "dinheiro",
    "monetizar", "monetizacao", "faturar", "negocio", "empreender",
    "marketplace", "elo7", "shopee", "mercado livre", "etsy",
    "precificar", "precificacao", "cliente", "encomenda", "loja",
]


_FINANCAS_SLUGS = {
    "financas":              "financas",
    "finanças":              "financas",
    "marketing digital":     "marketing_digital",
    "ganhar dinheiro online": "ganhar_dinheiro_online",
}


def _is_financas(categoria: str) -> bool:
    return categoria.lower().replace("ç", "c").strip() in _FINANCAS_SLUGS or \
           categoria.lower().strip() in _FINANCAS_SLUGS


def _get_financas_subniche(categoria: str) -> str:
    """Retorna a chave interna do sub-nicho: 'financas', 'marketing_digital' ou 'ganhar_dinheiro_online'."""
    cat = categoria.lower().strip()
    for key, slug in _FINANCAS_SLUGS.items():
        if cat == key or cat.replace("ç", "c") == key.replace("ç", "c"):
            return slug
    return "financas"


def _is_renda_extra(keyword: str, categoria: str = "") -> bool:
    if _is_financas(categoria):
        return False
    if "renda extra" in categoria.lower():
        return True
    kw_lower = keyword.lower()
    return any(term in kw_lower for term in RENDA_EXTRA_KEYWORDS)


def _bloco_download_original(url: str, label: str = "") -> str:
    """Bloco CTA com link para a pagina original de download do arquivo de impressao."""
    if not url:
        return ""
    texto = label.strip() if label.strip() else "Baixar arquivo de impressão 3D"
    return (
        '<div style="margin:28px 0;padding:18px 22px;background:#0d1f0d;border:2px solid #27ae60;'
        'border-radius:10px;text-align:center;">'
        f'<p style="margin:0 0 12px 0;font-size:15px;color:#ccffcc;font-weight:600;">'
        '📥 Acesse a página original para baixar o arquivo STL gratuitamente:</p>'
        f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
        'style="display:inline-block;padding:12px 28px;background:#27ae60;color:#ffffff;'
        'font-size:16px;font-weight:700;text-decoration:none;border-radius:6px;'
        'letter-spacing:.5px;">'
        f'⬇️ {texto}'
        '</a>'
        '</div>'
    )


def _injetar_download_apos_intro(content: str, url: str, label: str = "") -> str:
    """Injeta bloco de download logo apos o primeiro paragrafo do post."""
    bloco = _bloco_download_original(url, label)
    if not bloco:
        return content
    idx = content.find("</p>")
    if idx == -1:
        return bloco + content
    return content[: idx + 4] + "\n" + bloco + content[idx + 4 :]


def _injetar_download_antes_faq(content: str, url: str, label: str = "") -> str:
    """Injeta bloco de download logo ANTES da secao FAQ (Perguntas Frequentes)."""
    bloco = _bloco_download_original(url, label)
    if not bloco:
        return content

    faq_marcadores = ["Perguntas Frequentes", "perguntas frequentes", "PERGUNTAS FREQUENTES", "FAQ"]
    faq_pos = -1
    for marcador in faq_marcadores:
        idx = content.find(marcador)
        if idx >= 0:
            h2_start = content.rfind("<h2", 0, idx)
            if h2_start >= 0:
                faq_pos = h2_start
                break

    if faq_pos < 0:
        idx_schema = content.find('<script type="application/ld+json">')
        if idx_schema >= 0:
            faq_pos = idx_schema

    if faq_pos < 0:
        return content + "\n" + bloco

    return content[:faq_pos] + bloco + "\n" + content[faq_pos:]


def _bloco_bridge_renda_extra() -> str:
    """Bloco CTA inserido em posts de impressao 3D comum, apontando para Renda Extra."""
    return (
        '\n<div style="border:2px solid #2ecc71;background:#071a0e;'
        'padding:14px 18px;margin:28px 0;border-radius:6px;font-family:inherit;">'
        '<p style="margin:0 0 8px 0;font-weight:700;font-size:1em;color:#2ecc71;">'
        'Sua impressora pode gerar renda extra</p>'
        '<p style="margin:0;color:#c8e8c8;font-size:0.95em;line-height:1.6;">'
        'Alem de imprimir por hobby, muitos makers brasileiros vendem '
        'pecas, chaveiros e miniaturas online. '
        '<a href="https://clube3dbrasil.com/category/renda-extra/" '
        'rel="noopener noreferrer" '
        'style="color:#2ecc71;font-weight:600;text-decoration:underline;">'
        'Veja como comecar a monetizar sua impressora 3D &#8594;</a></p>'
        '</div>\n'
    )


_FINANCAS_SYSTEM = {
    "financas": (
        "Voce e um redator SEO especializado em financas pessoais e investimentos, "
        "escrevendo para um blog brasileiro.\n"
        "Escreva SEMPRE em portugues brasileiro, mesmo que a transcricao esteja em outro idioma.\n"
        "Tom claro, direto e pratico para leitores brasileiros que querem melhorar sua vida financeira.\n"
        "Responda SEMPRE com um JSON valido, sem texto fora do JSON."
    ),
    "marketing_digital": (
        "Voce e um redator SEO especializado em marketing digital, escrevendo para um blog brasileiro.\n"
        "Escreva SEMPRE em portugues brasileiro, mesmo que a transcricao esteja em outro idioma.\n"
        "Tom pratico e orientado a resultados para empreendedores e profissionais digitais brasileiros.\n"
        "Foque em estrategias aplicaveis: SEO, trafego pago, redes sociais, email marketing, "
        "funis de vendas, copywriting e ferramentas digitais.\n"
        "Responda SEMPRE com um JSON valido, sem texto fora do JSON."
    ),
    "ganhar_dinheiro_online": (
        "Voce e um redator SEO especializado em renda online e negócios digitais, "
        "escrevendo para um blog brasileiro.\n"
        "Escreva SEMPRE em portugues brasileiro, mesmo que a transcricao esteja em outro idioma.\n"
        "Tom motivador e pratico para brasileiros que querem gerar renda extra ou substituir a renda "
        "com trabalho online: freela, afiliados, infoprodutos, dropshipping, servicos digitais.\n"
        "Cite exemplos reais de plataformas e valores possiveis no Brasil.\n"
        "Responda SEMPRE com um JSON valido, sem texto fora do JSON."
    ),
}

_FINANCAS_LINKS = {
    "financas":               "Links externos (2-3): Banco Central, CVM, Tesouro Direto, B3 — sempre com target=\"_blank\" rel=\"noopener noreferrer\"",
    "marketing_digital":      "Links externos (2-3): Google Ads, Meta for Business, RD Station, Semrush, Hotmart — sempre com target=\"_blank\" rel=\"noopener noreferrer\"",
    "ganhar_dinheiro_online":  "Links externos (2-3): Workana, 99Freelas, Hotmart, Monetizze, Shopee, Mercado Livre — sempre com target=\"_blank\" rel=\"noopener noreferrer\"",
}

_FINANCAS_TAGS = {
    "financas":               '["financas", "financas pessoais", "{keyword}"]',
    "marketing_digital":      '["marketing digital", "marketing", "{keyword}"]',
    "ganhar_dinheiro_online":  '["ganhar dinheiro online", "renda online", "{keyword}"]',
}

_FINANCAS_CATEGORIA_LABEL = {
    "financas":               "Financas",
    "marketing_digital":      "Marketing Digital",
    "ganhar_dinheiro_online":  "Ganhar Dinheiro Online",
}

_FINANCAS_TEMA = {
    "financas":               "financas pessoais",
    "marketing_digital":      "marketing digital",
    "ganhar_dinheiro_online":  "como ganhar dinheiro online",
}


def _build_system_prompt_financas(subniche: str = "financas") -> str:
    return _FINANCAS_SYSTEM.get(subniche, _FINANCAS_SYSTEM["financas"])


def _build_user_prompt_financas(
    keyword: str,
    secondary_kws: list,
    transcript: str,
    youtube_url: str,
    yt_description: str = "",
    subniche: str = "financas",
) -> str:
    video_id = ""
    if youtube_url:
        m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", youtube_url)
        if m:
            video_id = m.group(1)

    secondary = ", ".join(secondary_kws) if secondary_kws else "nenhuma"

    description_block = (
        f"\n### Descricao do video no YouTube (use como contexto adicional):\n"
        f"{yt_description[:500]}\n"
        if yt_description else ""
    )

    transcript_block = (
        f"\n### Transcricao do video (pode estar em qualquer idioma — use como referencia "
        f"para entender o conteudo, mas escreva o post SOMENTE em portugues brasileiro):\n"
        f"{transcript[:4000]}\n"
        if transcript else ""
    )

    embed_html = ""
    if video_id:
        embed_html = (
            f'<!-- wp:embed {{"url":"https://www.youtube.com/watch?v={video_id}",'
            f'"type":"video","providerNameSlug":"youtube","responsive":true,'
            f'"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"}} -->\n'
            f'<figure class="wp-block-embed is-type-video is-provider-youtube '
            f'wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">'
            f'<div class="wp-block-embed__wrapper">\n'
            f'https://www.youtube.com/watch?v={video_id}\n'
            f'</div></figure>\n<!-- /wp:embed -->'
        )

    embed_instruction = (
        f"\n4. EMBED DO YOUTUBE - inclua exatamente este bloco apos o primeiro H2:\n{embed_html}\n"
        if embed_html else ""
    )

    faq_heading   = f"{keyword} - Perguntas Frequentes"
    tema_label    = _FINANCAS_TEMA.get(subniche, "financas")
    links_rule    = _FINANCAS_LINKS.get(subniche, _FINANCAS_LINKS["financas"])
    tags_template = _FINANCAS_TAGS.get(subniche, _FINANCAS_TAGS["financas"]).replace("{keyword}", keyword)
    cat_label     = _FINANCAS_CATEGORIA_LABEL.get(subniche, "Financas")

    return f"""Crie um post de blog SEO sobre {tema_label}:

**Keyword principal:** {keyword}
**Keywords secundarias:** {secondary}
{description_block}{transcript_block}
## ESTRUTURA DO post_content (HTML para WordPress - NAO inclua tag H1):

1. `<p>` introducao: 1-2 frases. Keyword em `<strong>` apenas na primeira frase.
2. `<h2><strong>` Primeiro H2: contem a keyword, curto (max. 7 palavras).
3. Conteudo do primeiro H2 (2-3 paragrafos uteis).
{embed_instruction}
5. Mais 3-4 secoes `<h2><strong>` com conteudo pratico sobre o tema.
6. `<h2><strong>Consideracoes Finais</strong></h2>` - resumo de 2-3 paragrafos.
7. `<h2><strong>{faq_heading}</strong></h2>` - 3-5 perguntas como `<h3><strong>Pergunta?</strong></h3>` + resposta de 40-80 palavras cada.

## REGRAS DE TEXTO:
- Portugues brasileiro, frases curtas (8-15 palavras), max. 4 frases por paragrafo
- 900-1.100 palavras totais no post_content
- Keyword principal: max. 4 ocorrencias
- ZERO emojis, ZERO travessao (-), ZERO ponto e virgula
- {links_rule}
- Palavras PROIBIDAS: mergulhar, navegar, robusto, crucial, garantir, alavancar, transformador, revolucionario, "vale a pena notar", "e importante mencionar", "sem mais delongas", "no mundo de hoje", "a verdade e que"

## RESPONDA APENAS COM JSON VALIDO (sem markdown, sem texto fora do JSON):

{{"titulo": "Titulo ate 65 chars com keyword no inicio", "seo_title": "Titulo SEO 55-65 chars", "meta_description": "Meta ate 155 chars com keyword", "slug": "keyword-em-kebab-case", "tags": {tags_template}, "categoria": "{cat_label}", "post_content": "<p>Introducao com <strong>{keyword}</strong>...</p><h2><strong>H2 com keyword</strong></h2>..."}}"""


def _build_system_prompt(renda_extra: bool = False, categoria: str = "") -> str:
    base = (
        "Voce e um redator SEO especializado em impressao 3D, escrevendo para clube3dbrasil.com.\n"
        "Escreva SEMPRE em portugues brasileiro, mesmo que a transcricao esteja em outro idioma.\n"
        "Tom tecnico-amigavel, direto e util para makers brasileiros.\n"
        "Responda SEMPRE com um JSON valido, sem texto fora do JSON."
    )
    angulo = _WEB_CAT_ANGULO.get(categoria, "")
    if angulo:
        base += f"\n\n{angulo}"
    if renda_extra:
        base += (
            "\n\nEste post e da categoria RENDA EXTRA. O publico quer usar impressao 3D para "
            "gerar dinheiro — foque no angulo de monetizacao: como vender, quanto cobrar, "
            "quais produtos tem maior demanda, onde vender (Elo7, Shopee, Mercado Livre, Etsy). "
            "Mantenha a base tecnica de impressao 3D, mas sempre conecte ao potencial de renda."
        )
    return base


def _build_user_prompt(
    keyword: str,
    secondary_kws: list,
    transcript: str,
    youtube_url: str,
    yt_description: str = "",
    renda_extra: bool = False,
) -> str:
    video_id = ""
    if youtube_url:
        m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", youtube_url)
        if m:
            video_id = m.group(1)

    secondary = ", ".join(secondary_kws) if secondary_kws else "nenhuma"

    description_block = (
        f"\n### Descricao do video no YouTube (use como contexto adicional):\n"
        f"{yt_description[:500]}\n"
        if yt_description else ""
    )

    transcript_block = (
        f"\n### Transcricao do video (pode estar em qualquer idioma — use como referencia "
        f"para entender o conteudo, mas escreva o post SOMENTE em portugues brasileiro):\n"
        f"{transcript[:4000]}\n"
        if transcript else ""
    )

    embed_html = ""
    if video_id:
        embed_html = (
            f'<!-- wp:embed {{"url":"https://www.youtube.com/watch?v={video_id}",'
            f'"type":"video","providerNameSlug":"youtube","responsive":true,'
            f'"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"}} -->\n'
            f'<figure class="wp-block-embed is-type-video is-provider-youtube '
            f'wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">'
            f'<div class="wp-block-embed__wrapper">\n'
            f'https://www.youtube.com/watch?v={video_id}\n'
            f'</div></figure>\n<!-- /wp:embed -->'
        )

    embed_instruction = (
        f"\n4. EMBED DO YOUTUBE - inclua exatamente este bloco apos o primeiro H2:\n{embed_html}\n"
        if embed_html else ""
    )

    faq_heading = f"{keyword} - Perguntas Frequentes"

    renda_extra_instrucoes = ""
    renda_extra_categoria = ""
    renda_extra_links = ""
    if renda_extra:
        renda_extra_instrucoes = """
## FOCO RENDA EXTRA (OBRIGATORIO neste post):
- Introducao: mencione explicitamente o potencial de ganho com impressao 3D
- Inclua uma secao H2 sobre "quanto da para ganhar" ou "quanto cobrar"
- Cite plataformas de venda: Elo7, Shopee, Mercado Livre, Etsy
- Mencione demanda de mercado: quais produtos vendem mais
- Consideracoes Finais: conecte a tecnica ao resultado financeiro
- FAQ deve incluir perguntas sobre precificacao, lucro e onde vender
"""
        renda_extra_categoria = '"Renda Extra"'
        renda_extra_links = (
            '- Links externos (2-3): Elo7, Shopee, Mercado Livre, Etsy ou fontes sobre precificacao '
            '- sempre com target="_blank" rel="noopener noreferrer"'
        )
    else:
        renda_extra_links = (
            '- Links externos (2-3): fontes confiaveis como Prusa, Bambu Lab, Thingiverse, Printables '
            '- sempre com target="_blank" rel="noopener noreferrer"'
        )
        renda_extra_categoria = '"Impressao 3D"'

    return f"""Crie um post de blog SEO para clube3dbrasil.com:

**Keyword principal:** {keyword}
**Keywords secundarias:** {secondary}
{description_block}{transcript_block}{renda_extra_instrucoes}
## ESTRUTURA DO post_content (HTML para WordPress - NAO inclua tag H1):

1. `<p>` introducao: 1-2 frases. Keyword em `<strong>` apenas na primeira frase.
2. `<h2><strong>` Primeiro H2: contem a keyword, curto (max. 7 palavras).
3. Conteudo do primeiro H2 (2-3 paragrafos uteis).
{embed_instruction}
5. Mais 3-4 secoes `<h2><strong>` com conteudo tecnico-pratico.
6. `<h2><strong>Consideracoes Finais</strong></h2>` - resumo de 2-3 paragrafos.
7. `<h2><strong>{faq_heading}</strong></h2>` - 3-5 perguntas como `<h3><strong>Pergunta?</strong></h3>` + resposta de 40-80 palavras cada.

## REGRAS DE TEXTO:
- Portugues brasileiro, frases curtas (8-15 palavras), max. 4 frases por paragrafo
- 900-1.100 palavras totais no post_content
- Keyword principal: max. 4 ocorrencias
- ZERO emojis, ZERO travessao (-), ZERO ponto e virgula
{renda_extra_links}
- Palavras PROIBIDAS: mergulhar, navegar, robusto, crucial, garantir, alavancar, transformador, revolucionario, "vale a pena notar", "e importante mencionar", "sem mais delongas", "no mundo de hoje", "a verdade e que"

## RESPONDA APENAS COM JSON VALIDO (sem markdown, sem texto fora do JSON):

{{"titulo": "Titulo ate 65 chars com keyword no inicio", "seo_title": "Titulo SEO 55-65 chars", "meta_description": "Meta ate 155 chars com keyword", "slug": "keyword-em-kebab-case", "tags": ["impressao 3d", "outra-tag"], "categoria": {renda_extra_categoria}, "post_content": "<p>Introducao com <strong>{keyword}</strong>...</p><h2><strong>H2 com keyword</strong></h2>..."}}"""


def _html_bloco_afiliado(af: dict) -> str:
    nome = af.get("nome") or af.get("nome_produto", "")
    link = af.get("link", "")
    return (
        '\n<div style="border:2px solid #e07b00;background:#1a0e00;'
        'padding:14px 18px;margin:28px 0;border-radius:6px;font-family:inherit;">'
        '<p style="margin:0 0 6px 0;font-size:0.75em;font-weight:700;color:#e07b00;'
        'text-transform:uppercase;letter-spacing:0.08em;">&#9733; Produto Indicado</p>'
        f'<a href="{link}" target="_blank" rel="noopener noreferrer sponsored" '
        f'style="display:block;color:#ffffff;font-size:1.05em;font-weight:600;'
        f'text-decoration:none;line-height:1.4;">{nome} &#8594;</a>'
        '</div>\n'
    )


def _injetar_blocos_afiliados(content: str, afiliados: list) -> str:
    """
    Injeta blocos de afiliado em 3 posicoes fixas do post_content:
      - Topo : apos o primeiro </p>  (intro)
      - Meio : antes de 'Consideracoes Finais'
      - Final: antes do JSON-LD / secao FAQ
    Distribui os produtos selecionados pelas posicoes; repete o mesmo se houver apenas 1.
    """
    if not afiliados:
        return content

    n = len(afiliados)
    bloco_topo  = _html_bloco_afiliado(afiliados[0])
    bloco_meio  = _html_bloco_afiliado(afiliados[n // 2])
    bloco_final = _html_bloco_afiliado(afiliados[-1])

    # ── TOPO: apos o primeiro </p> (paragrafo de introducao) ──────────────────
    pos = content.find("</p>")
    if pos >= 0:
        ins = pos + len("</p>")
        content = content[:ins] + bloco_topo + content[ins:]

    # ── MEIO: antes da secao Consideracoes Finais ──────────────────────────────
    meio_pos = -1
    for variante in ("Considerações Finais", "Consideracoes Finais", "considerações finais",
                     "consideracoes finais"):
        idx = content.find(variante)
        if idx >= 0:
            # recua até o início da tag <h2 que contém essa string
            h2_start = content.rfind("<h2", 0, idx)
            if h2_start >= 0:
                meio_pos = h2_start
            break

    if meio_pos < 0:
        # fallback: antes do 5º <h2>
        idx, count = 0, 0
        while count < 4:
            idx = content.find("<h2", idx + 1)
            if idx < 0:
                break
            count += 1
        if idx > 0:
            meio_pos = idx

    if meio_pos >= 0:
        content = content[:meio_pos] + bloco_meio + content[meio_pos:]

    # ── FINAL: antes do JSON-LD ou antes da secao FAQ ─────────────────────────
    final_pos = -1
    for marcador in ('<script type="application/ld+json">', "Perguntas Frequentes", "FAQ"):
        idx = content.find(marcador)
        if idx >= 0:
            # recua ate o <h2 ou <script mais proximo
            h2_start = content.rfind("<h2", 0, idx)
            sc_start = content.rfind("<script", 0, idx)
            final_pos = max(h2_start, sc_start, idx)
            # usa o ponto exato do marcador para nao perder o elemento
            final_pos = idx
            break

    if final_pos >= 0:
        content = content[:final_pos] + bloco_final + content[final_pos:]
    else:
        content += bloco_final

    return content


def inserir_imagens_no_content(content: str, imagens: list) -> str:
    """
    Insere blocos de imagem Gutenberg em posicoes estrategicas do post.

    imagens: lista de dicts {"url": str, "id": int, "alt": str}

    Regras:
    - Foto 1: logo APOS o primeiro bloco de afiliado (Produto Indicado).
              Se nao houver afiliado, fallback para apos o 1o H2.
    - Foto 2: apos 3o H2 (meio do post)
    - Foto 3: antes de Consideracoes Finais
    - Imagens extras alem das 3 primeiras sao ignoradas.
    """
    if not imagens:
        return content

    def _bloco(img: dict) -> str:
        url = img.get("url", "")
        mid = img.get("id", 0)
        alt = img.get("alt", "").replace('"', "&quot;")
        mid_attr = f'"id":{mid},' if mid else ""
        cls      = f" wp-image-{mid}" if mid else ""
        return (
            f'\n<!-- wp:image {{{mid_attr}"sizeSlug":"large","linkDestination":"none"}} -->\n'
            f'<figure class="wp-block-image size-large">'
            f'<img src="{url}" alt="{alt}" class="wp-image{cls}"/>'
            f'</figure>\n<!-- /wp:image -->\n'
        )

    h2_pos = [m.start() for m in re.finditer(r"<h2", content)]

    def _pos_apos_primeiro_afiliado() -> int:
        """Retorna a posicao logo APOS o primeiro bloco de afiliado, ou apos o 1o H2 como fallback."""
        idx_af = content.find("Produto Indicado")
        if idx_af >= 0:
            div_end = content.find("</div>", idx_af)
            if div_end >= 0:
                return div_end + len("</div>")
        if len(h2_pos) > 1:
            return h2_pos[1]
        return len(content) // 3

    def _pos_apos_h2(n_h2: int) -> int:
        if len(h2_pos) > n_h2:
            return h2_pos[n_h2]
        return len(content) * 2 // 3

    def _pos_consideracoes() -> int:
        for variante in ("Considerações Finais", "Consideracoes Finais",
                         "considerações finais", "consideracoes finais"):
            idx = content.find(variante)
            if idx >= 0:
                h2s = content.rfind("<h2", 0, idx)
                return h2s if h2s >= 0 else idx
        return h2_pos[-2] if len(h2_pos) >= 2 else len(content)

    n = len(imagens)

    if n == 1:
        p1 = _pos_apos_primeiro_afiliado()
        content = content[:p1] + _bloco(imagens[0]) + content[p1:]

    elif n == 2:
        p2 = _pos_consideracoes()
        p1 = _pos_apos_primeiro_afiliado()
        content = content[:p2] + _bloco(imagens[1]) + content[p2:]
        content = content[:p1] + _bloco(imagens[0]) + content[p1:]

    else:  # 3+
        p3 = _pos_consideracoes()
        p2 = _pos_apos_h2(3)
        p1 = _pos_apos_primeiro_afiliado()
        content = content[:p3] + _bloco(imagens[2]) + content[p3:]
        content = content[:p2] + _bloco(imagens[1]) + content[p2:]
        content = content[:p1] + _bloco(imagens[0]) + content[p1:]

    return content


def _reparar_json(raw: str) -> str:
    """Repara problemas comuns no JSON gerado pelo modelo."""
    # Remove markdown code fences
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE).strip()
    # Trim ao primeiro { e último }
    start = raw.find("{")
    end   = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start:end + 1]
    # Remove vírgulas antes de } ou ]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw


def _gerar_faq_schema_do_content(content: str) -> str:
    """Extrai perguntas H3 do conteudo gerado pelo Claude e cria FAQPage JSON-LD."""
    perguntas = re.findall(
        r'<h3[^>]*><strong>([^<]+)</strong></h3>\s*<p>([^<]+(?:<[^/][^>]*>[^<]*</[^>]+>[^<]*)*)</p>',
        content,
    )
    if not perguntas:
        return ""
    entidades = []
    for pergunta, resposta in perguntas[:5]:
        resp_limpa = re.sub(r"<[^>]+>", "", resposta).strip()
        if pergunta.strip() and resp_limpa:
            entidades.append({
                "@type": "Question",
                "name": pergunta.strip(),
                "acceptedAnswer": {"@type": "Answer", "text": resp_limpa},
            })
    if not entidades:
        return ""
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entidades}
    return f'\n<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>\n'


def gerar_post_seo(
    keyword: str,
    secondary_kws: list = None,
    transcript: str = "",
    youtube_url: str = "",
    yt_description: str = "",
    afiliados_override: list = None,
    log_fn=None,
    lang: str = "pt-BR",  # mantido por compatibilidade
    categoria: str = "",
) -> dict:
    """
    Gera post SEO via Claude API em portugues brasileiro.
    afiliados_override: None = auto-selecao, [] = sem afiliado, [...] = lista especifica.
    categoria: "Renda Extra" ativa angulo de monetizacao; auto-detectado via keyword se omitido.
    """
    import anthropic

    def log(msg):
        if log_fn:
            log_fn(msg)
        else:
            print(msg)

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY nao encontrado. Adicione no arquivo .env do projeto.")

    if secondary_kws is None:
        secondary_kws = []

    financas    = _is_financas(categoria)
    subniche    = _get_financas_subniche(categoria) if financas else ""
    renda_extra = _is_renda_extra(keyword, categoria)

    if financas:
        log(f"  Modo: {_FINANCAS_CATEGORIA_LABEL.get(subniche, 'Financas')} (sem relacao com impressao 3D)")
    elif renda_extra:
        log("  Modo: Renda Extra (angulo de monetizacao ativado)")

    # Resolve quais afiliados usar para este post
    if financas:
        afiliados_para_post = []  # sem afiliados de 3D em posts de finanças
    elif afiliados_override is not None:
        afiliados_para_post = afiliados_override
    else:
        todos = _carregar_afiliados()
        af = _escolher_afiliado(keyword, todos)
        afiliados_para_post = [af] if af else []

    if afiliados_para_post:
        nomes = [af.get("nome") or af.get("nome_produto", "") for af in afiliados_para_post]
        log(f"  Afiliado(s): {', '.join(nomes)}")
    else:
        log("  Sem afiliado para este post.")

    log("  Chamando Claude API (haiku)...")

    client = anthropic.Anthropic(api_key=api_key)

    if financas:
        system_prompt  = _build_system_prompt_financas(subniche)
        prompt_principal = _build_user_prompt_financas(
            keyword, secondary_kws, transcript, youtube_url, yt_description, subniche,
        )
    else:
        system_prompt  = _build_system_prompt(renda_extra=renda_extra, categoria=categoria)
        prompt_principal = _build_user_prompt(
            keyword, secondary_kws, transcript, youtube_url, yt_description,
            renda_extra=renda_extra,
        )

    raw = ""

    for attempt in range(1, 3):
        if attempt == 1:
            user_msg = prompt_principal
        else:
            user_msg = (
                "O JSON abaixo esta invalido. Retorne APENAS o JSON corrigido e completo, "
                "sem markdown, sem texto adicional:\n\n" + raw
            )

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )

        raw = _reparar_json(message.content[0].text.strip())

        try:
            data = json.loads(raw)
            break
        except json.JSONDecodeError as e:
            if attempt == 2:
                log(f"  ERRO JSON invalido apos 2 tentativas: {e}")
                raise
            log("  AVISO JSON invalido — solicitando correcao ao modelo...")

    slug_clean = re.sub(r"[^a-z0-9]+", "-", keyword.lower()).strip("-")

    post_content = data.get("post_content", "")
    post_content += _gerar_faq_schema_do_content(post_content)
    post_content = _injetar_blocos_afiliados(post_content, afiliados_para_post)

    # Bridge para Renda Extra apenas em posts de 3D puro (não em Finanças)
    if not renda_extra and not financas:
        post_content += _bloco_bridge_renda_extra()

    if financas:
        categoria_final = _FINANCAS_CATEGORIA_LABEL.get(subniche, "Financas")
    elif renda_extra:
        categoria_final = "Renda Extra"
    else:
        categoria_final = data.get("categoria", "Impressao 3D")

    post = {
        "titulo":              data.get("titulo", keyword),
        "slug":                data.get("slug", slug_clean),
        "content":             post_content,
        "excerpt":             data.get("meta_description", ""),
        "status":              "draft",
        "tags":                data.get("tags", ([_FINANCAS_TEMA.get(subniche, "financas"), keyword] if financas else ["impressao 3d", keyword])),
        "categories":          [categoria_final],
        "featured_image_path": "",
        "yoast_keyphrase":     keyword,
        "yoast_title":         data.get("seo_title", ""),
        "yoast_meta":          data.get("meta_description", ""),
        "gerado_em":           datetime.now().isoformat(),
        "origem":              "seo_writer",
    }

    log(f"  Post gerado: {post['titulo']}")
    log(f"  Categoria: {categoria_final}")
    log(f"  Meta ({len(post['yoast_meta'])} chars): {post['yoast_meta']}")
    return post
