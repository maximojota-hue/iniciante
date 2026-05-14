"""
injetar_schema_blogposting.py
Injeta schema JSON-LD completo em todos os posts publicados:
  - BlogPosting  → metadados do artigo (título, data, imagem, autor)
  - FAQPage      → perguntas frequentes (se o post tiver seção FAQ)

Execute: python injetar_schema_blogposting.py
"""

import sys
import json
import base64
import time
import re
import html as html_lib
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WP_URL   = "https://clube3dbrasil.com"
ENV_FILE = Path(".env")

AUTOR    = "Clube 3D"
PUBLISHER = {
    "@type": "Organization",
    "name":  "Clube 3D Brasil",
    "url":   WP_URL,
    "logo": {
        "@type": "ImageObject",
        "url":   f"{WP_URL}/wp-content/uploads/2025/01/logo-clube3d.png",
        "width":  200,
        "height": 60,
    },
}

FAQ_GENERICA_STL = [
    ("O arquivo STL é gratuito?",
     "Sim. O link aponta para a página original do criador na plataforma. Verifique a licença antes de uso comercial."),
    ("Qual fatiador usar?",
     "Cura, PrusaSlicer e Bambu Studio são compatíveis com STL e 3MF — todos têm versão gratuita."),
    ("Precisa de suporte?",
     "Depende da geometria. Abra no fatiador e ative a pré-visualização de suportes antes de imprimir."),
    ("Quanto filamento consome?",
     "Modelos médios consomem entre 30 g e 150 g dependendo do tamanho e do infill configurado."),
    ("Posso redimensionar o modelo?",
     "Sim. No fatiador você pode escalar livremente sem precisar editar o arquivo STL."),
]

FAQ_GENERICA_EDITORIAL = [
    ("Este conteúdo é atualizado regularmente?",
     "Sim. Revisamos e atualizamos nossos guias sempre que surgem novidades relevantes sobre impressão 3D."),
    ("O Clube 3D Brasil tem comunidade?",
     "Sim, temos grupos ativos no WhatsApp com makers de todo o Brasil. Acesse pelo menu do site."),
    ("Posso sugerir um tema para o blog?",
     "Claro! Entre em contato pelo e-mail casalabacate@gmail.com com sua sugestão."),
    ("O conteúdo é adequado para iniciantes?",
     "Sim. Publicamos conteúdo para todos os níveis — do primeiro filamento à impressão avançada."),
    ("As indicações de produtos são pagas?",
     "Alguns links são de afiliados (Amazon). Isso não influencia nossa opinião — só indicamos o que vale a pena."),
]


def carregar_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def criar_sessao(user: str, senha: str) -> requests.Session:
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type":  "application/json",
        "User-Agent":    "Clube3DBrasil-Schema/1.0",
    })
    return s


def buscar_posts(session: requests.Session, api: str) -> list[dict]:
    posts, page = [], 1
    while True:
        r = session.get(f"{api}/posts", params={
            "per_page": 100,
            "page":     page,
            "status":   "publish",
            "_embed":   True,       # traz featured_media embutido
        }, timeout=30)
        if not r.ok:
            break
        lote = r.json()
        if not lote:
            break
        posts.extend(lote)
        total = int(r.headers.get("X-WP-TotalPages", 1))
        print(f"  📄 Página {page}/{total} — {len(lote)} posts")
        if page >= total:
            break
        page += 1
        time.sleep(0.3)
    return posts


def imagem_post(post: dict) -> dict | None:
    """Extrai URL e dimensões da imagem destacada via _embedded."""
    try:
        media = post["_embedded"]["wp:featuredmedia"][0]
        sizes = media.get("media_details", {}).get("sizes", {})
        # Prefere large, senão full, senão qualquer
        for size in ("large", "medium_large", "full"):
            if size in sizes:
                s = sizes[size]
                return {
                    "@type":  "ImageObject",
                    "url":    s["source_url"],
                    "width":  s.get("width", 800),
                    "height": s.get("height", 600),
                }
        src = media.get("source_url", "")
        if src:
            return {"@type": "ImageObject", "url": src}
    except (KeyError, IndexError, TypeError):
        pass
    return None


def extrair_faqs_do_conteudo(content: str) -> list[tuple[str, str]]:
    """Tenta extrair perguntas e respostas de seções FAQ no HTML."""
    faqs = []
    # Padrão: <h3>Pergunta?</h3> seguido de <p>Resposta</p>
    blocos = re.findall(
        r'<h[23][^>]*>(.*?\?)</h[23]>\s*<p[^>]*>(.*?)</p>',
        content, re.IGNORECASE | re.DOTALL
    )
    for pergunta, resposta in blocos[:6]:
        pergunta = re.sub(r"<[^>]+>", "", pergunta).strip()
        resposta = re.sub(r"<[^>]+>", "", resposta).strip()
        if pergunta and resposta and len(resposta) > 20:
            faqs.append((pergunta, resposta))
    return faqs


def eh_post_stl(post: dict) -> bool:
    """Detecta se o post é sobre um modelo STL (vs editorial)."""
    slug  = post.get("slug", "")
    title = post.get("title", {}).get("rendered", "").lower()
    stl_keywords = (
        "stl", "modelo 3d", "figura", "figure", "bowser", "pekka",
        "flexi", "chaveiro", "mew", "drago", "wolverine", "pokebola",
        "hello-kitty", "corgi", "ippo", "piu-piu", "mago", "golem",
        "gigante", "morcego", "anquilossauro", "sonic", "knuckles",
        "popeye", "mickey", "gamer", "geek", "porta-pipoca",
        "luminaria", "escultura", "cranix",
    )
    return any(k in slug or k in title for k in stl_keywords)


def limpar_texto(texto: str) -> str:
    """Remove tags HTML, decodifica entidades e normaliza espaços."""
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = html_lib.unescape(texto)   # &amp; → &   &#8211; → —   &hellip; → …
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def montar_blogposting(post: dict) -> dict:
    titulo    = limpar_texto(post.get("title",   {}).get("rendered", ""))
    excerpt   = limpar_texto(post.get("excerpt", {}).get("rendered", ""))
    meta_desc = post.get("meta", {}).get("_yoast_wpseo_metadesc", "").strip()
    descricao = limpar_texto(meta_desc) if meta_desc else (excerpt or titulo)
    url       = post.get("link", "")
    data_pub  = post.get("date_gmt",      post.get("date",     ""))[:10]
    data_mod  = post.get("modified_gmt",  post.get("modified", ""))[:10]

    schema = {
        "@context":        "https://schema.org",
        "@type":           "BlogPosting",
        "headline":        titulo[:110],
        "description":     descricao[:200],
        "url":             url,
        "datePublished":   data_pub,
        "dateModified":    data_mod,
        "inLanguage":      "pt-BR",
        "author": {
            "@type": "Person",
            "name":  AUTOR,
            "url":   f"{WP_URL}/sobre-nos/",
        },
        "publisher":       PUBLISHER,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id":   url,
        },
    }

    img = imagem_post(post)
    if img:
        schema["image"] = img

    return schema


def montar_faqpage(faqs: list[tuple[str, str]]) -> dict:
    return {
        "@context":   "https://schema.org",
        "@type":      "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  html_lib.unescape(q),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text":  html_lib.unescape(a),
                },
            }
            for q, a in faqs
        ],
    }


def gerar_bloco_schema(post: dict) -> str:
    content = post.get("content", {}).get("rendered", "")
    is_stl  = eh_post_stl(post)

    blocos = []

    # BlogPosting sempre
    bp = montar_blogposting(post)
    # ensure_ascii=True: escapa não-ASCII como \uXXXX — imune a encoding do WP
    blocos.append(json.dumps(bp, ensure_ascii=True, indent=2))

    # FAQPage: tenta extrair do conteúdo, senão usa genérica
    faqs_extraidas = extrair_faqs_do_conteudo(content)
    if faqs_extraidas:
        faq = montar_faqpage(faqs_extraidas)
    elif is_stl:
        faq = montar_faqpage(FAQ_GENERICA_STL)
    else:
        faq = montar_faqpage(FAQ_GENERICA_EDITORIAL)
    blocos.append(json.dumps(faq, ensure_ascii=True, indent=2))

    return "\n".join(
        f'<script type="application/ld+json">\n{b}\n</script>' for b in blocos
    )


def remover_schema_antigo(content: str) -> str:
    """Remove todos os blocos JSON-LD existentes para reinjetar limpo."""
    return re.sub(
        r'\n?<script type="application/ld\+json">.*?</script>',
        "", content, flags=re.DOTALL
    ).rstrip()


def ja_tem_blogposting(content: str) -> bool:
    return '"BlogPosting"' in content and 'application/ld+json' in content


def main():
    print("\n" + "=" * 65)
    print("  SCHEMA JSON-LD — BlogPosting + FAQPage")
    print("=" * 65 + "\n")

    env = carregar_env()
    user  = env.get("WP_USER", "")
    senha = env.get("WP_PASS", "")
    if not user or not senha:
        print("❌ WP_USER/WP_PASS não encontrados no .env")
        return

    api     = f"{WP_URL}/wp-json/wp/v2"
    session = criar_sessao(user, senha)

    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print(f"❌ Autenticação falhou: {r.status_code}")
        return
    print(f"✅ Conectado como: {r.json().get('name', '')}\n")

    print("🔍 Buscando posts publicados...\n")
    posts = buscar_posts(session, api)
    print(f"\n  Total: {len(posts)} posts publicados\n")
    print("=" * 65)

    ok = ja_tinha = erros = 0

    for post in posts:
        pid     = post["id"]
        slug    = post.get("slug", "")
        titulo  = re.sub(r"<[^>]+>", "", post.get("title", {}).get("rendered", "")).strip()
        content = post.get("content", {}).get("rendered", "")

        tipo = "STL" if eh_post_stl(post) else "editorial"
        print(f"  🔄 [{pid}] ({tipo}) {titulo[:52]}...")

        # Remove schema antigo (se houver) e reinjeta corrigido
        content_limpo = remover_schema_antigo(content)
        schema_html   = gerar_bloco_schema(post)
        novo_content  = content_limpo + "\n" + schema_html

        try:
            r = session.post(
                f"{api}/posts/{pid}",
                json={"content": novo_content},
                timeout=30,
            )
            if r.ok:
                print(f"    ✅ BlogPosting + FAQPage injetados")
                ok += 1
            else:
                print(f"    ❌ HTTP {r.status_code}: {r.text[:100]}")
                erros += 1
        except Exception as e:
            print(f"    ❌ Exceção: {e}")
            erros += 1

        time.sleep(1.2)

    print("\n" + "=" * 65)
    print(f"  ✅ Injetados  : {ok}")
    print(f"  ⏭️  Já tinham  : {ja_tinha}")
    print(f"  ❌ Erros      : {erros}")
    print("=" * 65)
    print("""
  Próximos passos:
  → Validar em: https://search.google.com/test/rich-results
    (cole a URL de um post para verificar o schema)
  → Google Search Console → Inspeção de URL → Solicitar indexação
  → Aguardar 2-7 dias para rich results aparecerem no Google
""")


if __name__ == "__main__":
    main()
