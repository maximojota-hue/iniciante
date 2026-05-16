"""
Publica como rascunho o post #5:
"Como Se Destacar Vendendo Impressao 3D na Shopee".

Baseado na analise da transcricao do video:
https://www.youtube.com/watch?v=p-y99A4VADc

Nao chama API externa de conteudo. O texto foi preparado no fluxo do chat e
este script apenas cria capa, envia imagens e publica o rascunho no WordPress.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from publisher import WordPressPublisher

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


TITLE = "Como Se Destacar Vendendo Impressao 3D na Shopee"
SLUG = "como-se-destacar-vendendo-impressao-3d"
KEYPHRASE = "vender impressao 3D"
YOUTUBE_URL = "https://www.youtube.com/watch?v=p-y99A4VADc"
CAPA_ORIGINAL = Path(r"C:\Users\jcarlos\Downloads\Telegram Desktop\Tortank_Multipart_150%_PolyForge3d_t.me_@o3DLab_.jpg")
CAPA_PATH = Path("downloads/capas/como-se-destacar-vendendo-impressao-3d.jpg")

AFFILIATES = [
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para testar produtos de impressao 3D com baixo custo",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para vender impressao 3D em pequena escala",
    },
    {
        "id": 3,
        "name": "PLA Bambu Lab Beige",
        "url": "https://amzn.to/4scbIb1",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 16_01_16.png"),
        "alt": "PLA Bambu Lab Beige para pecas decorativas com acabamento premium",
    },
]


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def fit_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    src = Image.open(path).convert("RGB")
    target_w, target_h = size
    src_ratio = src.width / src.height
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = max(0, (new_w - target_w) // 2)
    top = max(0, (new_h - target_h) // 2)
    return img.crop((left, top, left + target_w, top + target_h))


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=face)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def criar_capa() -> Path:
    if not CAPA_ORIGINAL.exists():
        raise SystemExit(f"Imagem de capa nao encontrada: {CAPA_ORIGINAL}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    bg = fit_cover(CAPA_ORIGINAL, (w, h)).convert("RGBA")
    bg = ImageEnhance.Contrast(bg).enhance(1.12)
    bg = ImageEnhance.Color(bg).enhance(1.18)
    bg = bg.filter(ImageFilter.GaussianBlur(0.25))

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 92))
    draw.rectangle((0, 0, 660, h), fill=(0, 0, 0, 172))
    draw.rounded_rectangle((48, 48, 1152, 627), radius=24, outline=(0, 210, 255, 230), width=3)
    draw.rounded_rectangle((78, 78, 456, 126), radius=12, fill=(84, 230, 66, 245))
    draw.text((99, 88), "VENDA SEM BAIXAR PRECO", font=font(24, True), fill=(0, 13, 9, 255))

    y = 164
    title_face = font(58, True)
    for line in wrap(draw, "Como se destacar na impressao 3D", title_face, 560)[:4]:
        draw.text((78, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 64
    draw.text((80, y + 18), "Foto melhor, nicho certo e anuncio forte", font=font(28, True), fill=(0, 210, 255, 255))

    chip_x = 78
    for chip in ["Shopee", "IA", "Acabamento", "Valor percebido"]:
        box = draw.textbbox((0, 0), chip, font=font(20, True))
        chip_w = box[2] - box[0] + 28
        draw.rounded_rectangle((chip_x, 532, chip_x + chip_w, 574), radius=20, fill=(8, 18, 32, 240), outline=(84, 230, 66, 190), width=2)
        draw.text((chip_x + 14, 541), chip, font=font(20, True), fill=(235, 244, 255, 255))
        chip_x += chip_w + 12

    draw.text((78, 598), "Clube 3D Brasil", font=font(24, False), fill=(218, 230, 245, 235))
    final = Image.alpha_composite(bg, layer).convert("RGB")
    final.save(CAPA_PATH, quality=92, optimize=True)
    return CAPA_PATH


def product_block(item: dict, media_url: str, caption: str) -> str:
    return f"""
<figure class="wp-block-image aligncenter" style="max-width:760px;margin:28px auto;text-align:center;">
  <a href="{item['url']}" target="_blank" rel="noopener noreferrer sponsored">
    <img src="{media_url}" alt="{item['alt']}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" />
  </a>
  <figcaption style="font-size:14px;color:#666;">Produto indicado: {item['name']} - {caption}</figcaption>
</figure>
"""


def youtube_embed() -> str:
    return """
<!-- wp:embed {"url":"https://www.youtube.com/watch?v=p-y99A4VADc","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=p-y99A4VADc
</div></figure>
<!-- /wp:embed -->
"""


def build_content(media_urls: dict[int, str]) -> str:
    voolt = product_block(AFFILIATES[0], media_urls[1], "bom para testar produtos, cores e modelos antes de anunciar.")
    a1mini = product_block(AFFILIATES[1], media_urls[2], "impressora compacta para producao pequena e rotina simples.")
    beige = product_block(AFFILIATES[2], media_urls[3], "filamento com visual limpo para fotos, decoracao e pecas premium.")

    return f"""
<p>Para <strong>vender impressao 3D</strong> sem entrar numa guerra de centavos, o produto precisa parecer melhor antes mesmo do cliente perguntar o preco.</p>
<p>O video do canal Primeiras Impressoes 3D mostra uma ideia simples: muita gente vende o mesmo STL, mas poucos trabalham foto, video, titulo, descricao e nicho com cuidado. E e ai que o maker pequeno consegue aparecer.</p>

<h2><strong>Como vender impressao 3D melhor</strong></h2>
<p>A promessa central do video e boa, mas precisa de pe no chao: voce nao se destaca apenas usando inteligencia artificial. Voce se destaca quando usa IA para mostrar melhor um produto que ja tem demanda, acabamento aceitavel e preco coerente.</p>
<p>O erro comum e baixar um STL no MakerWorld, imprimir, tirar foto com fundo baguncado e jogar na Shopee esperando venda. Isso vira concorrencia por preco, porque para o cliente todos os anuncios parecem iguais.</p>

{youtube_embed()}

<div style="border:2px solid #22c55e;background:#07140c;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#22c55e;font-weight:800;text-transform:uppercase;">Ideia principal</p>
  <p style="margin:0;color:#d8ffe5;">Se o produto e parecido com o do concorrente, a diferenca precisa aparecer na foto, no video, na descricao, no nicho e no valor percebido.</p>
</div>

<h2><strong>O cliente compra percepcao</strong></h2>
<p>No video, o exemplo mais forte e a comparacao entre uma foto simples de produto e um anuncio com cena, uso real e apelo visual. O arquivo pode ser o mesmo, mas a percepcao muda.</p>
<p>Isso vale muito para impressao 3D geek, chaveiros, organizadores, suportes, lembrancinhas e pecas decorativas. Uma imagem boa mostra escala, acabamento, cor, contexto e motivo de compra.</p>
<p>Para produto geek, por exemplo, nao basta mostrar a peca em cima da mesa. Mostre o acabamento, a pintura, a textura, o tamanho e o ambiente onde o comprador imagina colocar aquilo.</p>

<h2><strong>Antes da IA vem o acabamento</strong></h2>
<p>Imagem bonita nao salva peca mal impressa. Se a camada esta ruim, se tem rebarba, se a cor nao combina ou se a foto promete mais do que o produto entrega, o cliente percebe quando recebe.</p>
<p>Por isso, separe um PLA barato para testar e um material mais bonito para a versao final. Teste encaixe, escala, suporte e tempo antes de produzir lote.</p>

{voolt}

<h2><strong>Use IA para melhorar anuncio, nao para mentir</strong></h2>
<p>O video mostra o uso de ferramentas para criar imagens, videos, titulos e descricoes. Isso pode ajudar muito, principalmente para quem vende em marketplace e precisa chamar atencao rapido.</p>
<p>Mas existe um limite importante: nao gere uma imagem que muda o produto. Se a IA cria uma versao maior, mais brilhante ou com detalhe que a sua impressora nao entrega, o anuncio pode virar problema.</p>
<p>A melhor estrategia e usar IA para criar cenario, organizar a composicao, sugerir copy e melhorar a apresentacao. O produto precisa continuar fiel ao que o cliente vai receber.</p>

<h2><strong>Nicho ruim derruba anuncio bom</strong></h2>
<p>Outro ponto certeiro do video: um anuncio bonito nao resolve um nicho sem demanda. Se ninguem quer comprar aquele item, foto profissional apenas deixa o fracasso mais elegante.</p>
<p>Comece por nichos com uso claro: pet, escola, eventos, jogos, colecionadores, organizacao, brindes, escritorio e presentes personalizados. Depois valide se as pessoas pagam antes de imprimir dezenas de unidades.</p>

<h2><strong>Equipamento simples ajuda na rotina</strong></h2>
<p>Para vender em pequena escala, consistencia pesa mais que promessa de velocidade. A impressora precisa repetir peca, manter primeira camada boa e dar menos manutencao durante a semana.</p>
<p>Uma maquina compacta e facil pode ser suficiente para validar produtos, montar anuncios e atender encomendas pequenas. O foco inicial deve ser aprender o que vende, nao comprar a maior estrutura possivel.</p>

{a1mini}

<h2><strong>Produto premium precisa parecer premium</strong></h2>
<p>Quando a peca vai para foto, cor e acabamento importam. Filamentos claros ajudam em pecas decorativas, miniaturas, bustos e objetos que vao receber pintura ou aparecer em ambiente limpo.</p>
<p>O cliente compara anuncio em poucos segundos. Se a imagem mostra textura boa, escala clara e acabamento caprichado, voce ganha chance de cobrar melhor.</p>

{beige}

<h2><strong>Checklist para destacar seu anuncio</strong></h2>
<ul>
  <li>fotografe a peca limpa, sem rebarba e com boa luz;</li>
  <li>mostre uma foto de escala com mao, mesa ou objeto conhecido;</li>
  <li>crie uma cena de uso, nao apenas fundo branco;</li>
  <li>escreva titulo com o que o cliente procura;</li>
  <li>inclua medidas, material, prazo e personalizacao;</li>
  <li>teste um video curto mostrando a peca sendo usada;</li>
  <li>evite prometer acabamento que sua impressora nao entrega.</li>
</ul>

<h2><strong>Quando nao vale competir por preco</strong></h2>
<p>Se o mesmo STL tem dezenas de vendedores, baixar R$ 1 pode ate trazer uma venda, mas tambem puxa sua margem para baixo. O caminho melhor e diferenciar pacote, foto, entrega, personalizacao ou nicho.</p>
<p>Vale competir por preco apenas quando voce conhece muito bem seu custo e consegue produzir com margem. Se voce ainda esta aprendendo, preco baixo demais vira curso caro.</p>

<h2><strong>Consideracoes Finais</strong></h2>
<p>O video acerta ao mostrar que vender impressao 3D nao depende apenas de imprimir. O anuncio precisa vender antes do produto chegar na mao do cliente.</p>
<p>Para o Clube 3D Brasil, o caminho pratico e este: escolha um nicho com demanda, teste barato, finalize bonito, fotografe melhor e use IA para melhorar apresentacao sem enganar o comprador.</p>

<h2><strong>Vender impressao 3D - Perguntas Frequentes</strong></h2>
<h3><strong>Como se destacar vendendo o mesmo produto 3D que outras pessoas?</strong></h3>
<p>Melhore a percepcao de valor. Use fotos melhores, video curto, descricao clara, medidas reais, acabamento bem feito e uma oferta mais especifica. Se todos vendem o mesmo modelo, o cliente escolhe quem parece mais profissional e confiavel.</p>

<h3><strong>Vale a pena usar IA para criar imagens de produto 3D?</strong></h3>
<p>Vale, desde que a imagem continue fiel ao produto real. Use IA para criar fundo, contexto, composicao e ideias de anuncio. Nao use para inventar acabamento, tamanho ou detalhe que a peca impressa nao tem.</p>

<h3><strong>Qual o maior erro ao vender impressao 3D na Shopee?</strong></h3>
<p>O maior erro e copiar o padrao dos outros: mesma foto, mesmo titulo, mesma descricao e preco um pouco menor. Isso coloca o vendedor numa disputa fraca, onde a margem cai antes do negocio amadurecer.</p>

<h3><strong>Preciso de uma impressora cara para vender impressao 3D?</strong></h3>
<p>Nao necessariamente. Para comecar, uma impressora confiavel, bem regulada e simples de operar pode ser suficiente. O mais importante e validar produto, custo, nicho e demanda antes de aumentar a estrutura.</p>

<h3><strong>Como saber se um nicho de impressao 3D e bom?</strong></h3>
<p>Um bom nicho tem busca, uso claro e comprador disposto a pagar. Procure problemas reais, personalizacao, datas comemorativas e comunidades apaixonadas. Depois teste poucas unidades antes de produzir estoque.</p>
"""


def main() -> None:
    carregar_env()
    for item in AFFILIATES:
        if not item["image"].exists():
            raise SystemExit(f"Imagem afiliada nao encontrada: {item['image']}")

    capa = criar_capa()
    cfg = {
        "wp_url": os.environ.get("WP_URL", "https://clube3dbrasil.com"),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_PASS", ""),
        "wp_post_status": "draft",
    }
    pub = WordPressPublisher(cfg)

    media_urls: dict[int, str] = {}
    for item in AFFILIATES:
        media_id, media_url = pub.upload_media(str(item["image"]), alt_text=item["alt"])
        if not media_id or not media_url:
            raise SystemExit(f"Falha ao enviar imagem afiliada #{item['id']}")
        media_urls[item["id"]] = media_url

    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": build_content(media_urls),
        "excerpt": "Aprenda como vender impressao 3D sem entrar na guerra de preco usando foto melhor, nicho certo, IA e valor percebido.",
        "status": "draft",
        "tags": ["impressao 3d", "vender impressao 3d", "shopee", "ganhar dinheiro com 3d"],
        "categories": ["Ganhar Dinheiro com 3D"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Vender Impressao 3D: Como Se Destacar na Shopee",
        "yoast_meta": "Vender impressao 3D sem guerra de preco: aprenda a melhorar foto, video, descricao, nicho e valor percebido.",
        "gerado_em": "2026-05-15",
        "origem": "youtube_manual_p-y99A4VADc",
    }

    result = pub.publicar_post(post)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
