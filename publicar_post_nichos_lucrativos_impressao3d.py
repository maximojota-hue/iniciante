"""
Publica como rascunho o post #8:
"Como Ganhar Dinheiro com Impressao 3D".

Baseado no pacote leve CRIAR_POST_CLUBE3D_COM_PACOTE:
- YouTube: https://www.youtube.com/watch?v=tB7LFuwK2p0
- Canal: STLFLIX BR - Impressao 3D

Nao chama API externa de conteudo.
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


TITLE = "Como Ganhar Dinheiro com Impressao 3D: Nichos Mais Promissores"
SLUG = "como-ganhar-dinheiro-com-impressao-3d-nichos"
KEYPHRASE = "ganhar dinheiro com impressao 3D"
VIDEO_URL = "https://www.youtube.com/watch?v=tB7LFuwK2p0"
CAPA_PATH = Path("downloads/capas/como-ganhar-dinheiro-com-impressao-3d-nichos.jpg")

CONTENT_IMAGES = [
    {
        "path": Path(r"C:\Users\jcarlos\Downloads\Telegram Desktop\MultiColor+Print+Profile+-+hamster.jpg"),
        "alt": "modelo 3D colorido para vender arquivos e produtos impressos",
        "caption": "Modelos chamativos ajudam a vender a ideia, mas o lucro vem de produto com demanda clara.",
    },
    {
        "path": Path(r"C:\Users\jcarlos\Downloads\Telegram Desktop\41_Axolt.jpg"),
        "alt": "personagem impresso em 3D para nichos geek e decoracao",
        "caption": "Itens geek atraem atencao, mas precisam de cuidado com licenca e concorrencia por preco.",
    },
    {
        "path": Path(r"C:\Users\jcarlos\Downloads\Telegram Desktop\_t.me_@o3Dlab_The+Offering+of+the+Broken+Heart.jpg"),
        "alt": "modelo artistico impresso em 3D com alto valor percebido",
        "caption": "Pecas autorais e decorativas podem ter valor percebido maior que produtos copiados da internet.",
    },
]

AFFILIATES = [
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para testar produtos impressos em 3D com menor custo",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para comecar negocio de impressao 3D",
    },
    {
        "id": 3,
        "name": "PLA Bambu Lab Beige",
        "url": "https://amzn.to/4scbIb1",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 16_01_16.png"),
        "alt": "PLA Bambu Lab Beige para produtos decorativos e acabamento premium",
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
    for image in CONTENT_IMAGES:
        if not image["path"].exists():
            raise SystemExit(f"Imagem do pacote nao encontrada: {image['path']}")
    for affiliate in AFFILIATES:
        if not affiliate["image"].exists():
            raise SystemExit(f"Imagem afiliada nao encontrada: {affiliate['image']}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    bg = fit_cover(CONTENT_IMAGES[0]["path"], (w, h)).convert("RGBA")
    bg = ImageEnhance.Contrast(bg).enhance(1.12)
    bg = ImageEnhance.Color(bg).enhance(1.08)
    bg = bg.filter(ImageFilter.GaussianBlur(0.35))

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 86))
    draw.rectangle((0, 0, 705, h), fill=(0, 0, 0, 190))
    draw.rounded_rectangle((46, 46, 1154, 629), radius=24, outline=(255, 106, 19, 230), width=3)
    draw.rounded_rectangle((78, 78, 426, 126), radius=12, fill=(255, 106, 19, 245))
    draw.text((101, 88), "RENDA COM 3D", font=font(25, True), fill=(8, 8, 8, 255))

    y = 158
    title_face = font(55, True)
    for line in wrap(draw, "Nichos lucrativos na impressao 3D", title_face, 600)[:3]:
        draw.text((78, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 62
    draw.text((80, y + 20), "luminarias, decoracao e produtos funcionais", font=font(26, True), fill=(0, 210, 255, 255))

    chip_x = 78
    for chip in ["alto valor", "menos disputa", "demanda real", "produto proprio"]:
        box = draw.textbbox((0, 0), chip, font=font(18, True))
        chip_w = box[2] - box[0] + 26
        draw.rounded_rectangle((chip_x, 532, chip_x + chip_w, 574), radius=20, fill=(8, 18, 32, 240), outline=(255, 106, 19, 210), width=2)
        draw.text((chip_x + 13, 543), chip, font=font(18, True), fill=(235, 244, 255, 255))
        chip_x += chip_w + 10

    draw.text((78, 598), "Clube 3D Brasil", font=font(24, False), fill=(218, 230, 245, 235))
    final = Image.alpha_composite(bg, layer).convert("RGB")
    final.save(CAPA_PATH, quality=92, optimize=True)
    return CAPA_PATH


def youtube_embed(url: str) -> str:
    return f"""
<!-- wp:embed {{"url":"{url}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"}} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
{url}
</div></figure>
<!-- /wp:embed -->
"""


def image_block(media: dict, media_url: str) -> str:
    return f"""
<figure class="wp-block-image aligncenter" style="max-width:820px;margin:28px auto;text-align:center;">
  <img src="{media_url}" alt="{media['alt']}" style="width:100%;max-width:820px;height:auto;border-radius:8px;" />
  <figcaption style="font-size:14px;color:#666;">{media['caption']}</figcaption>
</figure>
"""


def product_block(item: dict, media_url: str, caption: str) -> str:
    return f"""
<figure class="wp-block-image aligncenter" style="max-width:760px;margin:28px auto;text-align:center;">
  <a href="{item['url']}" target="_blank" rel="noopener noreferrer sponsored">
    <img src="{media_url}" alt="{item['alt']}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" />
  </a>
  <figcaption style="font-size:14px;color:#666;">Produto indicado: {item['name']} - {caption}</figcaption>
</figure>
"""


def build_content(media_urls: dict[str, str]) -> str:
    foto1 = image_block(CONTENT_IMAGES[0], media_urls["foto1"])
    foto2 = image_block(CONTENT_IMAGES[1], media_urls["foto2"])
    foto3 = image_block(CONTENT_IMAGES[2], media_urls["foto3"])
    pla_barato = product_block(AFFILIATES[0], media_urls["af_1"], "ideal para prototipar produto vendavel antes de gastar filamento premium.")
    impressora = product_block(AFFILIATES[1], media_urls["af_2"], "opcao de entrada para validar nichos pequenos e pedidos sob demanda.")
    pla_bege = product_block(AFFILIATES[2], media_urls["af_3"], "bom para decoracao, bustos, miniaturas e produtos que precisam de acabamento limpo.")
    return f"""
<p><strong>Ganhar dinheiro com impressao 3D</strong> e possivel, mas o erro mais comum e tentar vender qualquer arquivo bonito baixado da internet. O dinheiro costuma aparecer quando voce escolhe um nicho com demanda real, resolve um problema claro e foge da guerra de preco.</p>
<p>Este artigo foi criado a partir do video da STLFLIX BR sobre os nichos mais promissores para impressao 3D, com participacao de uma empresa que trabalha com muitas impressoras rodando todos os dias. A ideia aqui e traduzir essa conversa para um plano pratico para makers brasileiros.</p>

{youtube_embed(VIDEO_URL)}

<div style="border:2px solid #f97316;background:#160b05;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#fb923c;font-weight:800;text-transform:uppercase;">Resumo direto</p>
  <p style="margin:0;color:#ffe7d1;">Os melhores nichos nao sao os mais populares. Sao os que combinam demanda, personalizacao, valor percebido e menos concorrencia por preco.</p>
</div>

<h2><strong>O melhor nicho nao e o mais obvio</strong></h2>
<p>O video comeca com uma provocacao: quais nichos realmente dao dinheiro com impressao 3D? A resposta importante nao e copiar produto viral. O ponto forte e entender que produto personalizado e solucao especifica valem mais do que imprimir algo que todo mundo ja vende.</p>
<p>Quando voce pega um arquivo da internet e vende igual a dezenas de pessoas, a disputa vira preco. Quando voce cria uma solucao propria, com acabamento, contexto e utilidade, o cliente compara menos pelo quilo do PLA e mais pelo resultado.</p>

{foto1}

<h2><strong>1. Luminarias personalizadas</strong></h2>
<p>O nicho mais forte citado no pacote e o de <strong>luminarias</strong>. A razao e simples: luz tem apelo emocional, decorativo e funcional. Uma luminaria nao e apenas plastico impresso; ela pode virar presente, decoracao, item geek, produto infantil ou peca autoral.</p>
<p>A conversa cita exemplos de luminarias com alto valor percebido, inclusive pecas vendidas por valores altos quando existe historia, acabamento e proposta. O caminho nao e imprimir uma luminaria generica. E criar um modelo com identidade, sistema de iluminacao e apresentacao pronta para o cliente.</p>

<h2><strong>2. Decoracao com assinatura propria</strong></h2>
<p>Decoracao pode funcionar muito bem, mas so quando foge do basico. Vasos, esculturas, suportes, luminarias, placas e objetos de mesa precisam ter estilo reconhecivel. Se o cliente sente que esta comprando algo autoral, o preco deixa de ser comparado diretamente com uma peca comum.</p>
<p>Esse tipo de nicho combina com redes sociais, Pinterest, marketplaces e venda local. Uma foto boa, um ambiente bem montado e um produto com proposta clara ajudam mais do que anunciar apenas "impresso em 3D".</p>

{pla_bege}

<h2><strong>3. Produtos funcionais e pecas de reposicao</strong></h2>
<p>Outro caminho promissor e resolver problema real: suporte quebrado, adaptador, peca de reposicao, organizador, gabarito, suporte tecnico ou acessorio especifico. Esses produtos podem parecer menos chamativos que personagens, mas muitas vezes vendem melhor porque o cliente precisa da solucao.</p>
<p>Esse nicho exige medir, testar e ajustar. A vantagem e que a concorrencia costuma ser menor, principalmente quando voce atende uma necessidade local ou um equipamento especifico.</p>

{impressora}

<h2><strong>4. Personalizacao sob demanda</strong></h2>
<p>Personalizacao aumenta valor porque transforma a impressao em um produto do cliente. Nome, medida, cor, encaixe, logo, tema de festa, decoracao de quarto, suporte para equipamento ou brinde corporativo sao exemplos de pedidos que nao cabem em produto generico.</p>
<p>O segredo e criar limites. Personalizar tudo sem processo vira dor de cabeca. O melhor e ter modelos base, poucas opcoes bem definidas e preco claro para modificacoes.</p>

<h2><strong>5. Geek e personagens: cuidado com licenca</strong></h2>
<p>O nicho geek chama muita atencao e pode gerar pedidos, mas tem risco. O proprio pacote destaca o alerta sobre produtos nao licenciados. Vender personagem famoso sem autorizacao pode gerar problema, principalmente em marketplaces e anuncios pagos.</p>
<p>Para trabalhar com esse publico de forma mais segura, uma alternativa e vender suportes, bases, organizadores, displays, itens inspirados em temas gerais ou produtos autorais que conversem com o universo geek sem copiar marca protegida.</p>

{foto2}

<h2><strong>Como escolher um nicho para comecar</strong></h2>
<p>Antes de comprar mais impressora ou gastar filamento, escolha um recorte pequeno. Por exemplo: luminarias infantis personalizadas, decoracao geek autoral, organizadores para setup gamer, suportes para ferramentas, brindes para barbearia ou pecas funcionais para um equipamento local.</p>
<p>Um nicho bom precisa passar por quatro perguntas:</p>
<ul>
  <li>existe alguem procurando ou pagando por isso?</li>
  <li>consigo produzir com qualidade repetivel?</li>
  <li>tenho margem depois de filamento, energia, embalagem e tempo?</li>
  <li>consigo diferenciar sem copiar arquivo protegido?</li>
</ul>

<h2><strong>Comece com filamento barato antes do produto final</strong></h2>
<p>Para ganhar dinheiro com impressao 3D, teste barato. Prototipo, encaixe, suporte, tolerancia e acabamento quase sempre exigem ajustes. Usar filamento caro nos primeiros testes diminui margem antes mesmo de vender.</p>
<p>Depois que o produto estiver validado, ai sim faz sentido usar material melhor, cor final, embalagem e fotografia de venda.</p>

{pla_barato}

<h2><strong>Produto que vende precisa de foto e contexto</strong></h2>
<p>Uma peca solta em cima da mesa parece barata. A mesma peca em uso, com luz, escala, ambiente e legenda certa pode parecer produto premium. Isso vale para luminarias, decoracao, organizadores, miniaturas e brindes.</p>
<p>O cliente nao compra "gramas de PLA". Ele compra uma solucao, uma sensacao ou uma melhoria no espaco dele.</p>

{foto3}

<h2><strong>Plano simples para validar um nicho em 7 dias</strong></h2>
<ol>
  <li>Escolha um nicho pequeno e um publico claro.</li>
  <li>Crie ou adapte um modelo base sem infringir marca protegida.</li>
  <li>Imprima uma versao simples para teste.</li>
  <li>Fotografe o produto em contexto real.</li>
  <li>Publique em grupo, WhatsApp, Instagram, marketplace ou comunidade local.</li>
  <li>Anote perguntas, objecoes e pedidos de personalizacao.</li>
  <li>Ajuste preco, acabamento e oferta antes de produzir em quantidade.</li>
</ol>

<h2><strong>Erros que matam o lucro</strong></h2>
<ul>
  <li>vender so pelo preco mais baixo;</li>
  <li>copiar arquivo popular sem diferenciar;</li>
  <li>ignorar tempo de impressao e pos-processamento;</li>
  <li>usar material caro em prototipo;</li>
  <li>nao calcular embalagem, taxa, frete e falhas;</li>
  <li>apostar em personagem licenciado sem entender o risco.</li>
</ul>

<h2><strong>Vale a pena ganhar dinheiro com impressao 3D?</strong></h2>
<p>Vale, desde que voce trate como negocio e nao como botao magico de renda extra. A impressora e so a ferramenta. O lucro vem de escolher bem o nicho, criar uma oferta clara, reduzir falhas e vender algo que o cliente realmente entende.</p>
<p>Para o maker brasileiro, os caminhos mais interessantes neste momento sao luminarias, decoracao autoral, produtos funcionais, personalizacao e pequenas solucoes locais. O melhor produto nao e necessariamente o mais bonito; e o que alguem paga para resolver agora.</p>

<h2><strong>Perguntas Frequentes</strong></h2>
<h3><strong>Qual nicho da impressao 3D da mais dinheiro?</strong></h3>
<p>Nao existe um unico melhor nicho. Luminarias, decoracao autoral, pecas funcionais e personalizacao tendem a ter bom potencial porque permitem valor percebido maior e menos comparacao por preco.</p>

<h3><strong>Vale vender personagens impressos em 3D?</strong></h3>
<p>Existe demanda, mas tambem existe risco de licenca. Para vender com mais seguranca, prefira produtos autorais, acessorios, suportes, bases e itens inspirados em temas gerais sem copiar marcas protegidas.</p>

<h3><strong>Quanto cobrar por uma peca impressa em 3D?</strong></h3>
<p>Calcule filamento, energia, tempo de maquina, tempo manual, falhas, embalagem, taxa e lucro. Em produto autoral, o preco nao deve ser apenas o peso do PLA.</p>

<h3><strong>Qual impressora usar para comecar a vender?</strong></h3>
<p>Comece com uma impressora confiavel, simples de operar e com comunidade ativa. O mais importante no inicio e repetir qualidade, aprender suporte e reduzir falhas.</p>

<h3><strong>Como validar um produto antes de produzir muito?</strong></h3>
<p>Imprima poucas unidades, fotografe bem, publique para um publico pequeno e veja se as pessoas perguntam preco, tamanho, cor ou prazo. Interesse real aparece nas perguntas e pedidos.</p>
"""


def main() -> None:
    carregar_env()
    capa = criar_capa()
    cfg = {
        "wp_url": os.environ.get("WP_URL", "https://clube3dbrasil.com"),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_PASS", ""),
        "wp_post_status": "draft",
    }
    pub = WordPressPublisher(cfg)
    media_urls: dict[str, str] = {}

    for idx, item in enumerate(CONTENT_IMAGES, 1):
        media_id, media_url = pub.upload_media(str(item["path"]), alt_text=item["alt"])
        if not media_id or not media_url:
            raise SystemExit(f"Falha ao enviar foto do pacote #{idx}")
        media_urls[f"foto{idx}"] = media_url

    for item in AFFILIATES:
        media_id, media_url = pub.upload_media(str(item["image"]), alt_text=item["alt"])
        if not media_id or not media_url:
            raise SystemExit(f"Falha ao enviar imagem afiliada #{item['id']}")
        media_urls[f"af_{item['id']}"] = media_url

    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": build_content(media_urls),
        "excerpt": "Veja como ganhar dinheiro com impressao 3D escolhendo nichos com demanda real, alto valor percebido e menos disputa por preco.",
        "status": "draft",
        "tags": ["ganhar dinheiro com impressao 3d", "renda extra", "luminarias 3d", "decoracao 3d", "negocio 3d"],
        "categories": ["Ganhar Dinheiro com Impressao 3D"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Como Ganhar Dinheiro com Impressao 3D: Nichos",
        "yoast_meta": "Aprenda como ganhar dinheiro com impressao 3D escolhendo nichos promissores: luminarias, decoracao, pecas funcionais e personalizacao.",
        "gerado_em": "2026-05-16",
        "origem": "pacote_leve_youtube_tB7LFuwK2p0",
    }

    existente = pub._buscar_post_por_slug(SLUG)
    if existente:
        media_capa_id, _ = pub.upload_media(str(capa), alt_text=f"{TITLE} para Clube 3D Brasil")
        payload = {
            "title": post["titulo"],
            "content": post["content"],
            "excerpt": post["excerpt"],
            "status": "draft",
        }
        if media_capa_id:
            payload["featured_media"] = media_capa_id
        dados = pub._request("POST", f"posts/{existente['id']}", json=payload)
        pub._request(
            "POST",
            f"posts/{existente['id']}",
            json={
                "meta": {
                    "_yoast_wpseo_focuskw": post["yoast_keyphrase"],
                    "_yoast_wpseo_title": post["yoast_title"],
                    "_yoast_wpseo_metadesc": post["yoast_meta"],
                }
            },
        )
        result = {
            "wp_id": existente["id"],
            "url": dados.get("link", existente.get("link", "")),
            "slug": SLUG,
            "titulo": TITLE,
            "status": "updated",
        }
    else:
        result = pub.publicar_post(post)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
