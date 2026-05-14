"""
gerar_posts_manuais.py — Gera 10 posts baseados nos modelos mais populares de impressão 3D.
Execute: python gerar_posts_manuais.py
Depois:  python main.py --so-publicar
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def _carregar_ml_url() -> str:
    try:
        with open("config.json", encoding="utf-8") as f:
            return json.load(f).get("ml_afiliado_url", "COLE_AQUI_SEU_LINK_MERCADOLIVRE")
    except Exception:
        return "COLE_AQUI_SEU_LINK_MERCADOLIVRE"

WP_URL = "https://clube3dbrasil.com"

# ── Afiliados ─────────────────────────────────────────────────────────────────

AFILIADOS = [
    {"nome_produto": "Bambu Lab A1 Mini",         "link": "https://amzn.to/bambu-a1", "tipo": "impressora"},
    {"nome_produto": "Filamento PLA Premium 1kg",  "link": "https://amzn.to/pla-1kg",  "tipo": "filamento"},
    {"nome_produto": "Creality Ender 3 V3",        "link": "https://amzn.to/ender3",   "tipo": "impressora"},
    {"nome_produto": "Filamento PETG Transparente", "link": "https://amzn.to/petg",     "tipo": "filamento"},
]

PARES = [
    (0, 1), (2, 3), (0, 3), (2, 1),
    (1, 2), (3, 0), (0, 1), (2, 3),
    (1, 0), (3, 2),
]

FRASES_AF1 = [
    "Recomendado para imprimir esse modelo:",
    "Para imprimir com qualidade, uso e recomendo:",
    "Equipamento recomendado para esse tipo de peça:",
    "Para quem quer resultado profissional nessa impressão:",
    "A impressora ideal para modelos como esse:",
    "Confira o equipamento que uso para imprimir:",
    "Para resultados incríveis nesse tipo de modelo:",
    "A melhor opção de impressora para esse projeto:",
    "Imprima com precisão usando:",
    "Para garantir a qualidade dessa impressão:",
]

FRASES_AF2 = [
    "Material ideal para esse tipo de modelo:",
    "Para conseguir os melhores detalhes, o material certo é:",
    "Para garantir qualidade na impressão, use:",
    "Especialmente recomendado para modelos dessa categoria:",
    "O filamento certo faz toda a diferença:",
    "Filamento testado e aprovado para esse tipo de peça:",
    "Para imprimir com qualidade superior:",
    "Material recomendado para esse projeto:",
    "Garanta a qualidade do filamento:",
    "O material que uso para imprimir modelos assim:",
]

VARS_INTRO = [
    "é um dos modelos mais procurados para impressão 3D.",
    "tem conquistado fãs de impressão 3D em todo o Brasil.",
    "está entre os modelos mais baixados nas plataformas de impressão 3D.",
    "é uma das escolhas favoritas de quem curte impressão 3D.",
    "vem se destacando como um dos projetos mais populares da comunidade.",
]

VARS_FONTE = [
    "O arquivo está disponível gratuitamente na {plat}, criado por <strong>{criador}</strong>.",
    "Você pode baixar de graça na {plat}, obra do designer <strong>{criador}</strong>.",
    "O download está na {plat} de forma gratuita, com autoria de <strong>{criador}</strong>.",
    "Foi disponibilizado gratuitamente na {plat} pelo criador <strong>{criador}</strong>.",
]

VARS_COMPAT = [
    "O arquivo é compatível com impressoras FDM nos formatos STL e 3MF, funcionando em praticamente qualquer equipamento doméstico.",
    "Compatível com impressoras FDM em STL e 3MF, o modelo funciona em quase todas as impressoras do mercado.",
    "Nos formatos STL e 3MF, é compatível com a grande maioria das impressoras FDM disponíveis.",
    "O modelo vem nos formatos STL e 3MF, compatível com impressoras FDM de todas as marcas e modelos.",
]

VARS_CATEG = [
    "pertence à categoria <strong>{tema}</strong>, sendo ótima opção para colecionadores e entusiastas.",
    "se enquadra na categoria <strong>{tema}</strong> e é perfeito para colecionadores e quem quer vender peças.",
    "faz parte da categoria <strong>{tema}</strong> e se destaca pela qualidade e popularidade.",
    "é classificado como <strong>{tema}</strong> e está entre os mais pedidos pelos fãs de impressão 3D.",
]

VARS_CTA_DL = [
    "Clique no botão abaixo para acessar o arquivo STL de forma gratuita:",
    "Use o botão abaixo para ir direto ao download gratuito:",
    "Acesse o download pelo botão abaixo, sem nenhum custo:",
    "Baixe gratuitamente clicando no botão abaixo:",
]

VARS_PRODUTOS = [
    "Para imprimir com qualidade, confira os produtos que uso e recomendo:",
    "Estes são os produtos que indico para esse tipo de impressão:",
    "Equipamentos e materiais recomendados para imprimir esse modelo:",
    "Confira os melhores produtos para obter um ótimo resultado:",
]

VARS_RODAPE = [
    "Gostou? Confira mais modelos 3D gratuitos aqui no",
    "Quer mais modelos assim? Explore o",
    "Para mais downloads gratuitos de qualidade, visite o",
    "Encontre mais modelos incríveis no",
]

# ── Posts relacionados ────────────────────────────────────────────────────────

RELACIONADOS_BASE = [
    {"titulo": "Chaveiro Mew — Download STL Grátis",       "url": f"{WP_URL}/chaveiro-mew/",         "tema": "Pokémon"},
    {"titulo": "Morcego Articulado — Download STL Grátis", "url": f"{WP_URL}/morcego-articulado/",    "tema": "Animais"},
    {"titulo": "Flexi Mini Corgi — Download STL Grátis",   "url": f"{WP_URL}/flexi-mini-corgi/",      "tema": "Animais"},
    {"titulo": "Bowser — Download STL Grátis",             "url": f"{WP_URL}/bowser/",                "tema": "Super-Heróis"},
    {"titulo": "Flexi Espinossauro — Download STL Grátis", "url": f"{WP_URL}/flexi-espinossauro/",    "tema": "Dinossauros"},
]


# ── Modelos ───────────────────────────────────────────────────────────────────

MODELOS = [
    {
        "nome": "Flexi Dragão Articulado", "criador": "TheFPVSquirrel", "tema": "Fantasia",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/276709-flexi-dragon",
        "descricao": "Dragão articulado print-in-place com excelentes articulações, imprime sem suporte e funciona perfeitamente em PLA.",
        "config": {"camada": "0.2mm", "material": "PLA", "suporte": "Não necessário", "infill": "15%"},
    },
    {
        "nome": "Spider-Man Print-in-Place", "criador": "HeroMaker3D", "tema": "Super-Heróis",
        "plataforma": "MakerWorld", "url_fonte": "https://makerworld.com/en/models/spider-man-print-in-place",
        "descricao": "Homem-Aranha articulado print-in-place, imprime em uma única peça sem necessidade de montagem ou suporte.",
        "config": {"camada": "0.15mm", "material": "PLA", "suporte": "Não necessário", "infill": "20%"},
    },
    {
        "nome": "Organizador de Mesa Modular", "criador": "DesignPro3D", "tema": "Organização",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/modular-desk-organizer",
        "descricao": "Sistema modular de organização de mesa com encaixes magnéticos, personalizável para qualquer configuração.",
        "config": {"camada": "0.2mm", "material": "PLA ou PETG", "suporte": "Não necessário", "infill": "25%"},
    },
    {
        "nome": "Chaveiro Unicórnio Flexi", "criador": "FlexyPrints", "tema": "Fantasia",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/unicorn-flexi-keychain",
        "descricao": "Chaveiro de unicórnio articulado flexi, imprime em uma peça só e fica incrível em qualquer cor de PLA.",
        "config": {"camada": "0.2mm", "material": "PLA", "suporte": "Não necessário", "infill": "15%"},
    },
    {
        "nome": "Fidget Cubo Anti-Stress", "criador": "FidgetWorld3D", "tema": "Fidget",
        "plataforma": "MakerWorld", "url_fonte": "https://makerworld.com/en/models/fidget-cube",
        "descricao": "Cubo fidget com botões, joystick e outros elementos interativos em todos os lados, ótimo para aliviar ansiedade.",
        "config": {"camada": "0.2mm", "material": "PLA", "suporte": "Se necessário", "infill": "20%"},
    },
    {
        "nome": "Vaso Espiral Gyroid", "criador": "VasePrint3D", "tema": "Decoração",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/gyroid-spiral-vase",
        "descricao": "Vaso com estrutura gyroid espiral, impresso em modo vase para máxima eficiência. Resultado translúcido e elegante.",
        "config": {"camada": "0.2mm", "material": "PLA Silk ou PETG", "suporte": "Não necessário", "infill": "0% (modo vaso)"},
    },
    {
        "nome": "T-Rex Articulado Flexi", "criador": "DinoFlex3D", "tema": "Dinossauros",
        "plataforma": "MakerWorld", "url_fonte": "https://makerworld.com/en/models/flexi-t-rex",
        "descricao": "T-Rex articulado print-in-place com mandíbula móvel e corpo completamente flexível, um dos modelos mais baixados do MakerWorld.",
        "config": {"camada": "0.2mm", "material": "PLA", "suporte": "Não necessário", "infill": "15%"},
    },
    {
        "nome": "Suporte para Fone de Ouvido", "criador": "DeskOrganizer3D", "tema": "Organização",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/headphone-stand",
        "descricao": "Suporte elegante para headset com design minimalista, encaixa em qualquer mesa e tem base antiderrapante.",
        "config": {"camada": "0.2mm", "material": "PLA ou PETG", "suporte": "Não necessário", "infill": "30%"},
    },
    {
        "nome": "Polvo Flexi Articulado", "criador": "OctoFlex3D", "tema": "Animais",
        "plataforma": "MakerWorld", "url_fonte": "https://makerworld.com/en/models/flexi-octopus",
        "descricao": "Polvo articulado com 8 tentáculos flexíveis, imprime sem suporte e os tentáculos se mexem de forma realista.",
        "config": {"camada": "0.2mm", "material": "PLA", "suporte": "Não necessário", "infill": "15%"},
    },
    {
        "nome": "Cubo de Rubik Imprimível", "criador": "PuzzlePrint3D", "tema": "Puzzles",
        "plataforma": "Printables", "url_fonte": "https://www.printables.com/model/rubiks-cube",
        "descricao": "Cubo de Rubik completamente funcional e imprimível em 3D, com mecanismo interno suave e peças intercambiáveis.",
        "config": {"camada": "0.15mm", "material": "PLA", "suporte": "Não necessário", "infill": "25%"},
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def gerar_slug(nome: str) -> str:
    import unicodedata, re
    texto = unicodedata.normalize("NFD", nome)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto.lower())
    texto = re.sub(r"[\s_]+", "-", texto.strip())
    return texto[:60]


def relacionados_html(tema: str) -> str:
    por_tema = [r for r in RELACIONADOS_BASE if r.get("tema") == tema]
    itens = por_tema[:3] if por_tema else RELACIONADOS_BASE[:3]
    return "\n  ".join(
        f'<li><a href="{r["url"]}" target="_blank" rel="noopener">{r["titulo"]}</a></li>'
        for r in itens
    )


def gerar_html(modelo: dict, af1: dict, af2: dict, idx: int, ml_url: str = "") -> str:
    nome    = modelo["nome"]
    criador = modelo["criador"]
    tema    = modelo["tema"]
    plat    = modelo["plataforma"]
    url     = modelo["url_fonte"]
    desc    = modelo["descricao"]
    cfg     = modelo["config"]
    slug    = gerar_slug(nome)
    kw      = f"modelo 3D {nome.lower()}"
    titulo_seo = f"Modelo 3D {nome} — Download STL Grátis"[:60]
    meta_desc  = f"Baixe o modelo 3D de {nome} gratuitamente. Arquivo STL para impressão 3D. Perfeito para fãs de {tema}."[:155]
    tags_str   = f"{nome}, {tema}, impressão 3D, modelo 3D, STL, {plat}, download STL, STL grátis, {nome} 3D, {tema} 3D"

    frase_af1  = FRASES_AF1[idx % len(FRASES_AF1)]
    frase_af2  = FRASES_AF2[idx % len(FRASES_AF2)]
    v_intro    = random.choice(VARS_INTRO)
    v_fonte    = random.choice(VARS_FONTE).format(plat=plat, criador=criador)
    v_compat   = random.choice(VARS_COMPAT)
    v_categ    = random.choice(VARS_CATEG).format(tema=tema)
    v_cta_dl   = random.choice(VARS_CTA_DL)
    v_produtos = random.choice(VARS_PRODUTOS)
    v_rodape   = random.choice(VARS_RODAPE)
    rel_html   = relacionados_html(tema)

    return f"""<div style="background:#1800ac;border:2px solid #ffffff;padding:16px;margin:0 0 24px 0;border-radius:6px;color:#ffffff;font-family:monospace;font-size:13px;">
  <strong style="font-size:14px;color:#ffffff;">⚠️ YOAST SEO — PREENCHER ANTES DE PUBLICAR</strong><br><br>
  <strong>Frase-chave de foco:</strong> {kw}<br>
  <strong>Título SEO:</strong> {titulo_seo}<br>
  <strong>Slug:</strong> {slug}<br>
  <strong>Meta descrição:</strong> {meta_desc}<br>
  <strong>Tags:</strong> {tags_str}<br>
  <strong>Imagem SEO:</strong> Inserir imagem principal do modelo (mesma do post)<br>
  <strong>Imagem — Título:</strong> {nome} STL 3D<br>
  <strong>Imagem — Texto alternativo:</strong> {nome} impressão 3D<br>
  <strong>Resumo/Excerpt:</strong> {meta_desc}
</div>

<!-- INTRODUÇÃO — frase-chave obrigatória no 1º parágrafo -->
<p>O <strong>{kw}</strong> {v_intro}
{v_fonte}</p>

<!-- AFILIADO TOPO -->
<div style="background:#1800ac;border-left:4px solid #ffffff;padding:16px;margin:20px 0;border-radius:0 8px 8px 0;color:#ffffff;">
  <p><strong>🛒 {frase_af1}</strong></p>
  <p><a href="{af1['link']}" target="_blank" rel="noopener sponsored">
    <strong>👉 {af1['nome_produto']}</strong></a> — ideal para esse tipo de modelo.</p>
</div>

<!-- SOBRE O MODELO -->
<h2>📌 Sobre o {kw}</h2>
<p>O <strong>{kw}</strong> está disponível na
<a href="{url}" target="_blank" rel="noopener">{plat}</a>,
criado por <strong>{criador}</strong>. {v_compat}</p>

<p>{desc}</p>

<p>O modelo {v_categ}</p>

<!-- TABELA DE INFORMAÇÕES -->
<h2>📦 Informações do Modelo</h2>
<table style="width:100%;border-collapse:collapse;">
  <tr><td style="padding:8px;border:1px solid #ddd;width:35%;"><strong>Nome original</strong></td><td style="padding:8px;border:1px solid #ddd;">{nome}</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;"><strong>Criador</strong></td><td style="padding:8px;border:1px solid #ddd;">{criador}</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;"><strong>Plataforma</strong></td><td style="padding:8px;border:1px solid #ddd;">{plat}</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;"><strong>Tema</strong></td><td style="padding:8px;border:1px solid #ddd;">{tema}</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;"><strong>Formato</strong></td><td style="padding:8px;border:1px solid #ddd;">STL / 3MF</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;"><strong>Download</strong></td><td style="padding:8px;border:1px solid #ddd;">Gratuito</td></tr>
</table>

<!-- CONFIG DE IMPRESSÃO -->
<h2>⚙️ Configurações de Impressão</h2>
<p>Para obter o melhor resultado ao imprimir o <strong>{kw}</strong>,
use as configurações abaixo como ponto de partida e ajuste conforme sua impressora:</p>
<ul>
  <li><strong>Altura de camada:</strong> {cfg['camada']}</li>
  <li><strong>Material:</strong> {cfg['material']}</li>
  <li><strong>Suporte:</strong> {cfg['suporte']}</li>
  <li><strong>Infill:</strong> {cfg['infill']}</li>
</ul>

<!-- AFILIADO MEIO -->
<div style="background:#1800ac;border:1px solid #ffffff;padding:16px;margin:20px 0;border-radius:8px;color:#ffffff;">
  <p><strong>🎨 {frase_af2}</strong></p>
  <p><a href="{af2['link']}" target="_blank" rel="noopener sponsored">
    <strong>👉 {af2['nome_produto']}</strong></a> — especialmente recomendado para
    modelos da categoria {tema}.</p>
</div>

<!-- BOTÃO DE DOWNLOAD -->
<h2>🔗 Download do Modelo</h2>
<p>{v_cta_dl}</p>
<p style="text-align:center;">
  <a href="{url}" target="_blank" rel="noopener" class="btn-download-modelo"
     style="background:#0073aa;color:#fff;padding:12px 28px;border-radius:6px;
            text-decoration:none;font-weight:bold;display:inline-block;margin:8px 0;">
    📥 Baixar gratuitamente na {plat}
  </a>
</p>

<!-- PRODUTOS RECOMENDADOS -->
<h2>💰 Produtos Recomendados</h2>
<p>{v_produtos}</p>
<ul>
  <li><a href="{af1['link']}" target="_blank" rel="noopener sponsored"><strong>{af1['nome_produto']}</strong></a> — recomendado para esse tipo de impressão</li>
  <li><a href="{af2['link']}" target="_blank" rel="noopener sponsored"><strong>{af2['nome_produto']}</strong></a> — ideal para modelos de {tema}</li>
</ul>

<!-- POSTS RELACIONADOS -->
<h2>📚 Posts Relacionados</h2>
<ul>
  {rel_html}
</ul>

<!-- RODAPÉ -->
<p>{v_rodape} <a href="{WP_URL}/" target="_blank" rel="noopener">
<strong>Clube 3D Brasil</strong></a>!</p>

<script>
(function(){{
  var ML_URL = '{ml_url}';
  if (!ML_URL || ML_URL === 'COLE_AQUI_SEU_LINK_MERCADOLIVRE') return;
  document.querySelectorAll('.btn-download-modelo').forEach(function(btn){{
    btn.addEventListener('click', function(e){{
      e.preventDefault();
      var orig = btn.getAttribute('href');
      window.open(orig, '_blank', 'noopener,noreferrer');
      var af = window.open(ML_URL, '_blank', 'noopener');
      if (af) {{ af.blur(); }}
    }});
  }});
}})();
</script>
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    posts  = []
    ml_url = _carregar_ml_url()

    for i, modelo in enumerate(MODELOS):
        af1  = AFILIADOS[PARES[i][0]]
        af2  = AFILIADOS[PARES[i][1]]
        slug = gerar_slug(modelo["nome"])
        nome = modelo["nome"]
        tema = modelo["tema"]
        plat = modelo["plataforma"]

        html = gerar_html(modelo, af1, af2, i, ml_url)

        post = {
            "slug":            slug,
            "titulo":          f"Modelo 3D {nome} — Download STL Grátis",
            "content":         html,
            "yoast_keyphrase": f"modelo 3D {nome.lower()}",
            "yoast_title":     f"Modelo 3D {nome} — Download STL Grátis"[:60],
            "yoast_meta":      f"Baixe o modelo 3D de {nome} gratuitamente. Arquivo STL para impressão 3D. Perfeito para fãs de {tema}."[:155],
            "tags":            [nome, tema, "impressão 3D", "modelo 3D", "STL", plat, "download STL", "STL grátis", f"{nome} 3D", f"{tema} 3D"],
            "categories":      [tema],
            "status":          "draft",
            "tema":            tema,
            "plataforma":      plat,
            "gerado_em":       datetime.now().isoformat(),
        }

        posts.append(post)

        pasta = Path("downloads") / slug
        pasta.mkdir(parents=True, exist_ok=True)
        seo_txt = f"""YOAST SEO — {nome}
{'=' * 50}
Frase-chave de foco : modelo 3D {nome.lower()}
Título SEO          : {f"Modelo 3D {nome} — Download STL Grátis"[:60]}
Slug                : {slug}
Meta descrição      : Baixe o modelo 3D de {nome} gratuitamente. Arquivo STL para impressão 3D. Perfeito para fãs de {tema}.
Tags                : {nome}, {tema}, impressão 3D, modelo 3D, STL, {plat}, download STL, STL grátis, {nome} 3D, {tema} 3D
Imagem — Título     : {nome} STL 3D
Imagem — Alt text   : {nome} impressão 3D
Resumo/Excerpt      : Baixe o modelo 3D de {nome} gratuitamente. Arquivo STL para impressão 3D. Perfeito para fãs de {tema}.
"""
        with open(pasta / "seo.txt", "w", encoding="utf-8") as f:
            f.write(seo_txt)

        print(f"  ✅ Post {i+1:02d}: {post['titulo'][:55]}...")

    out = Path("posts_gerados.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(posts)} posts salvos em {out}")
    print("➡️  Execute agora: python main.py --so-publicar")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  📝 GERANDO 10 POSTS — MODELOS MAIS POPULARES DE IMPRESSÃO 3D")
    print("=" * 60)
    print()
    main()
    print("=" * 60)
