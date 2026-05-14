"""
gerador.py v2.0 — Gerador de Posts Clube 3D Brasil
"""

import json
import logging
import re
import random
import unicodedata
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================
# 🔥 KEYWORD INTELIGENTE
# =============================

def gerar_variacoes(nome):
    base = nome.lower()
    return [
        f"{base} stl impressão 3d",
        f"{base} arquivo stl download",
        f"{base} modelo 3d para imprimir",
        f"{base} stl grátis download",
        f"download {base} stl 3d",
        f"como imprimir {base} em 3d",
        f"{base} impressão 3d arquivo stl",
    ]


def escolher_keyword(nome):
    variacoes = gerar_variacoes(nome)
    # Prioriza keywords com download ou stl, escolhe aleatoriamente entre as melhores
    prioritarias = [k for k in variacoes if "download" in k or "stl" in k]
    return random.choice(prioritarias) if prioritarias else random.choice(variacoes)


# =============================
# 🔒 CONTROLE DE DENSIDADE
# =============================

def limitar_keyword(texto, keyword, max_ocorrencias=4):
    partes = texto.split(keyword)
    if len(partes) > max_ocorrencias:
        return keyword.join(partes[:max_ocorrencias]) + "".join(partes[max_ocorrencias:])
    return texto


# =============================
# 🧠 SEO BASE
# =============================

def gerar_slug(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto.lower())
    return re.sub(r"\s+", "-", texto).strip("-")[:60]


_VARS_META = [
    "Baixe o arquivo STL de {nome} gratuitamente. Modelo {tema} para impressão 3D — configurações, dicas e link de download.",
    "Imprima o {nome} em 3D! Arquivo STL grátis com dicas de configuração, material recomendado e link direto para download.",
    "Arquivo STL do {nome} para baixar grátis. Veja as melhores configurações de impressão e onde encontrar o modelo original.",
    "Descubra como imprimir o {nome} em 3D. Download do STL gratuito, configurações recomendadas e dicas para iniciantes.",
    "O {nome} é um dos modelos mais populares para impressão 3D. Baixe o STL grátis e confira as dicas de impressão.",
    "Modelo 3D {nome} disponível para download. STL gratuito com guia completo de impressão, material e configurações.",
]

_VARS_SEO_TITLE = [
    "{nome} STL Download Grátis | Clube 3D Brasil",
    "Como Imprimir {nome} em 3D — STL Grátis | Clube 3D Brasil",
    "{nome} — Arquivo STL para Impressão 3D | Clube 3D Brasil",
    "Download {nome} STL Gratuito | Clube 3D Brasil",
    "{nome} para Impressão 3D — Guia e Download | Clube 3D Brasil",
]


def gerar_meta(nome: str, tema: str = "3D") -> str:
    template = random.choice(_VARS_META)
    return template.format(nome=nome, tema=tema)[:155]


def gerar_seo_title(nome: str) -> str:
    template = random.choice(_VARS_SEO_TITLE)
    return template.format(nome=nome)[:65]


# =============================
# 📄 CONTEÚDO OTIMIZADO (500+ palavras)
# =============================

_VARS_INTRO_P1 = [
    "é um dos modelos mais procurados entre os entusiastas de impressão 3D do Brasil.",
    "conquistou espaço entre os criadores que buscam modelos 3D de qualidade para imprimir em casa.",
    "está entre os downloads mais populares nas maiores plataformas de modelos 3D.",
    "tem chamado atenção de quem busca modelos bem elaborados para impressão FDM.",
]

_VARS_INTRO_P2 = [
    "Neste post você encontra tudo o que precisa para baixar, preparar e imprimir este modelo com sucesso.",
    "Aqui você confere onde baixar o arquivo STL, as melhores configurações e dicas para obter resultado profissional.",
    "Reunimos as principais informações: origem, configurações recomendadas e o link de download gratuito.",
    "Veja abaixo o link de download, as configurações ideais e dicas práticas para imprimir sem erros.",
]

_VARS_VANTAGENS = [
    ["Arquivo gratuito disponível para download imediato na plataforma original.",
     "Compatível com praticamente todas as impressoras FDM do mercado.",
     "Ideal para coleção, presente ou decoração — agrada fãs de todas as idades.",
     "O formato STL é aceito pelos principais fatiadores: Cura, PrusaSlicer e Bambu Studio."],
    ["Download gratuito sem necessidade de cadastro pago.",
     "Funciona em impressoras de entrada como Ender 3 e em modelos avançados como Bambu Lab.",
     "Pode ser impresso em PLA, PETG ou resina dependendo da finalidade.",
     "Projeto criado pela comunidade e revisado pelo autor original."],
    ["Disponível nos formatos STL e 3MF para máxima compatibilidade.",
     "Perfeito tanto para iniciantes quanto para makers experientes.",
     "Impressão rápida com configurações padrão — sem ajustes complexos.",
     "Comunidade ativa que compartilha fotos e dicas de impressão."],
]

_VARS_CONFIG = [
    ("0.20 mm", "PLA", "200–210 °C", "60 °C", "50 mm/s", "15–20%"),
    ("0.15 mm", "PLA ou PETG", "205–215 °C", "60 °C", "45 mm/s", "20%"),
    ("0.20 mm", "PLA+", "210–220 °C", "65 °C", "55 mm/s", "15%"),
]

_VARS_MATERIAL = [
    "O <strong>PLA</strong> é o material mais indicado para este tipo de modelo. É fácil de imprimir, disponível em muitas cores e tem acabamento suave. Para peças que precisam de mais resistência, o <strong>PETG</strong> é uma boa alternativa — mantém os detalhes e suporta temperaturas mais altas. Evite ABS em modelos com detalhes finos, pois a retração pode causar empenamento.",
    "Para quem está começando, o <strong>PLA</strong> é a escolha certa: fácil de calibrar, não precisa de mesa muito quente e dá ótimos resultados. Se quiser uma peça mais durável, o <strong>PETG</strong> oferece resistência extra sem perder os detalhes. Filamentos metalizados ou com brilho também funcionam muito bem nesse tipo de peça.",
    "O <strong>PLA Premium</strong> entrega o melhor acabamento para modelos decorativos como este. Use temperatura entre 200–215 °C e velocidade moderada para preservar os detalhes finos. Se precisar de resistência ao calor, prefira <strong>PETG</strong> ou <strong>ASA</strong> para uso em ambientes externos.",
]

_VARS_ERROS = [
    "Um erro comum é imprimir em escala errada. Sempre verifique as dimensões no fatiador antes de iniciar. Outro ponto importante é a aderência da primeira camada — use cola em bastão ou superfície PEI para evitar que a peça solte durante a impressão.",
    "Fique atento ao tempo de impressão: modelos com muitos detalhes podem demorar mais do que o esperado. Configure corretamente o resfriamento nas pontes e saliências para evitar fios e deformações. Uma calibração de fluxo precisa também faz grande diferença no resultado final.",
    "Verifique se o arquivo não tem geometrias não-manifold antes de fatiar — use o Meshmixer ou o próprio PrusaSlicer para detectar problemas. Também preste atenção ao sentido de impressão: orientar corretamente o modelo na mesa pode eliminar a necessidade de suporte.",
]

_VARS_CONCLUSAO = [
    "Se você gosta de impressão 3D e está sempre em busca de novos projetos, fique de olho no Clube 3D Brasil. Publicamos novos modelos STL gratuitos toda semana, com dicas de impressão e configurações testadas.",
    "Curtiu o modelo? Compartilhe com a comunidade e ajude outros makers a descobrir novos projetos. Acompanhe o Clube 3D Brasil para não perder nenhum lançamento — publicamos conteúdo novo toda semana.",
    "Continue explorando os modelos disponíveis no Clube 3D Brasil. Temos opções para todos os gostos — de chaveiros a figures articulados, passando por utensílios domésticos e decoração temática.",
]


def gerar_faq_schema(nome: str) -> str:
    faqs = [
        ("O arquivo STL é gratuito?",
         "Sim. O link aponta para a página original do criador. Verifique a licença antes de uso comercial."),
        ("Qual fatiador usar?",
         "Cura, PrusaSlicer e Bambu Studio são compatíveis com STL e 3MF — todos têm versão gratuita."),
        ("Precisa de suporte?",
         "Depende da geometria. Abra no fatiador e ative a pré-visualização de suportes antes de imprimir."),
        ("Quanto filamento consome?",
         "Modelos médios consomem entre 30 g e 150 g dependendo do tamanho e do infill configurado."),
        ("Posso redimensionar o modelo?",
         "Sim. No fatiador você pode escalar livremente sem precisar editar o arquivo STL."),
    ]
    entidades = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faqs
    ]
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entidades}
    return f'\n<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>\n'


def gerar_conteudo(meta: dict, keyword: str) -> str:
    nome      = meta["nome"]
    descricao = meta.get("descricao", "")
    link      = meta["url_fonte"]
    tema      = meta.get("tema", "3D")
    criador   = meta.get("criador", "")

    sin        = random.choice(["arquivo STL", "modelo 3D", "download 3D", "projeto STL"])
    intro_p1   = random.choice(_VARS_INTRO_P1)
    intro_p2   = random.choice(_VARS_INTRO_P2)
    vantagens  = random.choice(_VARS_VANTAGENS)
    cfg        = random.choice(_VARS_CONFIG)
    material   = random.choice(_VARS_MATERIAL)
    erro       = random.choice(_VARS_ERROS)
    conclusao  = random.choice(_VARS_CONCLUSAO)

    criador_str = f", criado por <strong>{criador}</strong>" if criador else ""
    desc_html   = f"<p>{descricao}</p>" if descricao else ""
    itens_lista = "".join(f"<li>{v}</li>" for v in vantagens)

    texto = f"""
<h1>{nome} STL para Impressão 3D | Download Grátis</h1>

<p>O <strong>{keyword}</strong> {intro_p1} {intro_p2}</p>

<p>O {sin} está disponível gratuitamente na plataforma original{criador_str}. Clique no botão de download ao final desta página para acessar o arquivo.</p>

<h2>📌 Sobre o modelo {nome}</h2>
{desc_html}
<p>O <strong>{nome}</strong> é uma ótima escolha para quem busca qualidade e facilidade na impressão 3D da categoria <strong>{tema}</strong>. A geometria bem elaborada permite um resultado impressionante mesmo em impressoras de nível básico.</p>

<h2>✅ Por que imprimir este modelo?</h2>
<ul>
{itens_lista}
</ul>

<!--IMAGEM_1-->

<h2>⚙️ Configurações de Impressão Recomendadas</h2>
<p>Para obter o melhor resultado com o <strong>{nome}</strong>, use as configurações abaixo como ponto de partida e ajuste conforme sua impressora:</p>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f0f0f0;"><th style="padding:8px;border:1px solid #ddd;text-align:left;">Parâmetro</th><th style="padding:8px;border:1px solid #ddd;text-align:left;">Valor recomendado</th></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Altura de camada</td><td style="padding:8px;border:1px solid #ddd;">{cfg[0]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Material</td><td style="padding:8px;border:1px solid #ddd;">{cfg[1]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Temperatura do bico</td><td style="padding:8px;border:1px solid #ddd;">{cfg[2]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Mesa aquecida</td><td style="padding:8px;border:1px solid #ddd;">{cfg[3]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Velocidade</td><td style="padding:8px;border:1px solid #ddd;">{cfg[4]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Infill</td><td style="padding:8px;border:1px solid #ddd;">{cfg[5]}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;">Suporte</td><td style="padding:8px;border:1px solid #ddd;">Verificar no fatiador</td></tr>
</table>

<!--IMAGEM_2-->

<h2>🧪 Material recomendado</h2>
<p>{material}</p>

<h2>⚠️ Erros comuns e como evitar</h2>
<p>{erro}</p>

<!--IMAGEM_3-->

<h2>🔗 Download do {nome}</h2>
<p>O arquivo está disponível gratuitamente. Clique no link abaixo para acessar a página original do modelo:</p>
<p style="text-align:center;">
  <a href="{link}" target="_blank" rel="noopener"
     style="background:#0073aa;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;">
    📥 Baixar {nome} gratuitamente
  </a>
</p>

<h2>❓ Perguntas Frequentes sobre {nome}</h2>
<p><strong>O arquivo STL é gratuito?</strong><br>Sim. O link aponta para a página original do criador. Verifique a licença antes de uso comercial.</p>
<p><strong>Qual fatiador usar?</strong><br>Cura, PrusaSlicer e Bambu Studio são compatíveis com STL e 3MF — todos têm versão gratuita.</p>
<p><strong>Precisa de suporte?</strong><br>Depende da geometria. Abra no fatiador e ative a pré-visualização de suportes antes de imprimir.</p>
<p><strong>Quanto filamento consome?</strong><br>Modelos médios consomem entre 30 g e 150 g dependendo do tamanho e do infill configurado.</p>
<p><strong>Posso redimensionar o modelo?</strong><br>Sim. No fatiador você pode escalar livremente sem precisar editar o arquivo STL.</p>

<p>{conclusao}</p>
"""

    texto += gerar_faq_schema(nome)
    return limitar_keyword(texto, keyword)


# =============================
# 🔗 INTERLINK
# =============================

def gerar_interlinks(posts):
    if len(posts) < 2:
        return ""
    links = random.sample(posts, min(3, len(posts)))
    html = "<h2>🔗 Modelos relacionados</h2><ul>"
    for p in links:
        html += f"<li><a href='{p['url']}'>{p['titulo']}</a></li>"
    html += "</ul>"
    return html


def gerar_interlinks_avancado(posts_relacionados, pilar_url=None):
    html = "<h2>🔗 Modelos relacionados</h2><ul>"
    for p in posts_relacionados:
        html += f"<li><a href='{p['url']}'>{p['titulo']}</a></li>"
    html += "</ul>"
    if pilar_url:
        html += f"""
<h3>📚 Ver coleção completa</h3>
<p><a href='{pilar_url}'>Veja todos os modelos deste tema</a></p>
"""
    return html


# =============================
# 🔀 GERADOR V3 (CLUSTER + PILAR)
# =============================

def gerar_post_v3(meta: dict, posts_publicados: list[dict], pilar_url: str | None = None, cluster=None) -> dict:
    nome = meta["nome"]
    tema = meta.get("tema", "3D")

    keyword  = escolher_keyword(nome)
    conteudo = gerar_conteudo(meta, keyword)

    relacionados = cluster.obter_relacionados(tema) if cluster else []
    if relacionados or pilar_url:
        conteudo += gerar_interlinks_avancado(relacionados, pilar_url)
    elif posts_publicados:
        conteudo += gerar_interlinks(posts_publicados)

    _meta = gerar_meta(nome)
    return {
        "titulo":          f"{nome} STL para Impressão 3D",
        "slug":            gerar_slug(nome),
        "content":         conteudo,
        "excerpt":         _meta,
        "yoast_keyphrase": keyword,
        "yoast_title":     gerar_seo_title(nome),
        "yoast_meta":      _meta,
        "tags":            [nome, "STL", "impressão 3D", tema],
        "categories":      [tema],
        "tema":            tema,
        "gerado_em":       datetime.now().isoformat(),
    }


# =============================
# 💰 GERADOR V5 (MONETIZAÇÃO)
# =============================

def gerar_post_v5(meta: dict, posts_publicados: list[dict], afiliados: list[dict], cluster=None, pilar_url: str | None = None) -> dict:
    from monetizacao import Monetizacao

    nome = meta["nome"]
    tema = meta.get("tema", "3D")
    keyword = escolher_keyword(nome)

    monet = Monetizacao(afiliados)
    conteudo = gerar_conteudo(meta, keyword)
    produto = monet.escolher_produto(conteudo)

    if produto:
        # Afiliado encontrado: bloco topo, meio e final
        conteudo = monet.bloco_topo(produto) + conteudo
        partes = conteudo.split("<h2>")
        if len(partes) > 2:
            partes.insert(2, monet.bloco_meio(produto))
        conteudo = "<h2>".join(partes)
    else:
        # Sem match de keyword: usa AdSense no topo
        conteudo = monet.bloco_adsense() + conteudo

    # Interlinks com cluster ou fallback simples
    relacionados = cluster.obter_relacionados(tema) if cluster else []
    if relacionados or pilar_url:
        conteudo += gerar_interlinks_avancado(relacionados, pilar_url)
    elif posts_publicados:
        conteudo += gerar_interlinks(posts_publicados)

    # Bloco final: afiliado ou AdSense
    if produto:
        conteudo += monet.bloco_final(produto)
    else:
        conteudo += monet.bloco_adsense()

    _meta = gerar_meta(nome)
    return {
        "titulo":          f"{nome} STL para Impressão 3D",
        "slug":            gerar_slug(nome),
        "content":         conteudo,
        "excerpt":         _meta,
        "yoast_keyphrase": keyword,
        "yoast_title":     gerar_seo_title(nome),
        "yoast_meta":      _meta,
        "tags":            [nome, "STL", "impressão 3D", tema],
        "categories":      [tema],
        "tema":            tema,
        "gerado_em":       datetime.now().isoformat(),
    }


# =============================
# 🔗 BACKLINK PARA SATÉLITES
# =============================

def gerar_resumo_backlink(nome: str, url: str) -> str:
    return f"""
<h2>{nome} STL para Impressão 3D</h2>
<p>Modelo disponível para download gratuito.</p>
<p><a href='{url}'>Acesse o modelo completo aqui</a></p>
"""


# =============================
# 🚀 CLASSE PRINCIPAL
# =============================

class GeradorPostsV2:

    def __init__(self, config: dict):
        self.config = config
        self.wp_url = config.get("wp_url", "https://clube3dbrasil.com")

    def gerar_post(self, meta: dict, posts_publicados: list[dict] | None = None) -> dict:
        nome = meta["nome"]
        tema = meta.get("tema", "3D")

        keyword  = escolher_keyword(nome)
        slug     = gerar_slug(nome)
        meta_desc = gerar_meta(nome)

        conteudo  = gerar_conteudo(meta, keyword)
        conteudo += gerar_interlinks(posts_publicados or [])

        return {
            "slug":            slug,
            "titulo":          f"{nome} STL para Impressão 3D",
            "content":         conteudo,
            "excerpt":         meta_desc,
            "yoast_keyphrase": keyword,
            "yoast_title":     gerar_seo_title(nome),
            "yoast_meta":      meta_desc,
            "tags":            [nome, "STL", "impressão 3D", tema],
            "categories":      [tema],
            "status":          self.config.get("wp_post_status", "draft"),
            "tema":            tema,
            "gerado_em":       datetime.now().isoformat(),
        }

    def _carregar_afiliados(self) -> list[dict]:
        path = Path(self.config.get("afiliados_file", "afiliados.json"))
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            dados = json.load(f)
        # Normaliza formato antigo (nome_produto/tipo) para novo (nome/keyword)
        _map_tipo = {
            "impressora":  "impressora 3d",
            "filamento":   "filamento pla",
            "acessorio":   "impressora 3d",
            "acessório":   "impressora 3d",
            "ferramenta":  "impressão 3d",
            "curso":       "impressão 3d",
            "outro":       "impressão 3d",
        }
        return [
            {
                "keyword": _map_tipo.get(a.get("tipo", "").lower(), "impressão 3d"),
                "nome":    a.get("nome", a.get("nome_produto", "Produto 3D")),
                "link":    a.get("link", "#"),
            }
            for a in dados
        ]

    def processar_lote(self, modelos: list[dict], gerar_top10: bool = False) -> list[dict]:
        from cluster import ClusterManager
        cluster = ClusterManager()
        afiliados = self._carregar_afiliados()
        usar_monetizacao = bool(afiliados)

        posts = []
        posts_publicados = []
        modo = "monetização + cluster" if usar_monetizacao else "cluster"
        print(f"  📝 Gerando {len(modelos)} post(s) com {modo}...")

        for meta in modelos:
            nome = meta["nome"]
            tema = cluster.detectar_tema(nome, nome)
            meta = {**meta, "tema": tema}
            if usar_monetizacao:
                post = gerar_post_v5(meta, posts_publicados, afiliados, cluster=cluster)
            else:
                post = gerar_post_v3(meta, posts_publicados, cluster=cluster)
            post["status"] = self.config.get("wp_post_status", "draft")
            posts.append(post)

            post_info = {
                "titulo": post["titulo"],
                "url":    f"{self.wp_url}/{post['slug']}/",
                "tema":   tema,
            }
            posts_publicados.append(post_info)
            cluster.adicionar_post(tema, post_info)
            print(f"    ✅ {post['titulo'][:55]}...")

        # Páginas pilares — uma por tema
        for tema in cluster.clusters:
            pilar = cluster.gerar_pilar(tema)
            if pilar:
                _pilar_meta = f"Coleção completa de modelos 3D {tema} para impressão 3D."
                posts.append({
                    "slug":            pilar["slug"],
                    "titulo":          pilar["titulo"],
                    "content":         pilar["conteudo"],
                    "excerpt":         _pilar_meta,
                    "yoast_keyphrase": f"modelos 3D {tema}",
                    "yoast_title":     f"Modelos 3D {tema} | Clube 3D Brasil",
                    "yoast_meta":      _pilar_meta,
                    "tags":            [tema, "STL", "impressão 3D", "modelos 3D"],
                    "categories":      [tema],
                    "status":          self.config.get("wp_post_status", "draft"),
                    "tema":            tema,
                    "tipo":            "pilar",
                    "gerado_em":       datetime.now().isoformat(),
                })
                print(f"    🏛️ Pilar gerado: {tema}")

        return posts
