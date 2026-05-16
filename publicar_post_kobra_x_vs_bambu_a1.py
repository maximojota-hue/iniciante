"""
Publica como rascunho o post #6:
"Kobra X Vale a Pena? Comparativo com Bambu Lab A1".

Baseado em duas fontes de YouTube:
- Barbacast: https://www.youtube.com/watch?v=9FF2UnfhaBk
- Anycubic: https://www.youtube.com/watch?v=8k4rUUexwUs

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


TITLE = "Kobra X Vale a Pena? Comparativo com Bambu Lab A1"
SLUG = "kobra-x-vale-a-pena-comparativo-bambu-lab-a1"
KEYPHRASE = "Kobra X vale a pena"
VIDEO_REVIEW = "https://www.youtube.com/watch?v=9FF2UnfhaBk"
VIDEO_OFICIAL = "https://www.youtube.com/watch?v=8k4rUUexwUs"
CAPA_ORIGINAL = Path(r"C:\Users\jcarlos\Pictures\Screenshots\Captura de tela 2026-05-16 102701.png")
CAPA_PATH = Path("downloads/capas/kobra-x-vale-a-pena-comparativo-bambu-lab-a1.jpg")

AFFILIATES = [
    {
        "id": 5,
        "name": "Anycubic Kobra X Combo",
        "url": "https://meli.la/1suuv4n",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\cobra x.jpg"),
        "alt": "Anycubic Kobra X Combo para impressao 3D multicolor",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para comparar com Anycubic Kobra X",
    },
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para testar impressoras 3D com menor custo",
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
    for affiliate in AFFILIATES:
        if not affiliate["image"].exists():
            raise SystemExit(f"Imagem afiliada nao encontrada: {affiliate['image']}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    bg = fit_cover(CAPA_ORIGINAL, (w, h)).convert("RGBA")
    bg = ImageEnhance.Contrast(bg).enhance(1.14)
    bg = ImageEnhance.Color(bg).enhance(1.08)
    bg = bg.filter(ImageFilter.GaussianBlur(0.2))

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 92))
    draw.rectangle((0, 0, 665, h), fill=(0, 0, 0, 182))
    draw.rounded_rectangle((48, 48, 1152, 627), radius=24, outline=(255, 106, 19, 230), width=3)
    draw.rounded_rectangle((78, 78, 326, 126), radius=12, fill=(255, 106, 19, 245))
    draw.text((99, 88), "REVIEW 2026", font=font(25, True), fill=(8, 8, 8, 255))

    y = 162
    title_face = font(59, True)
    for line in wrap(draw, "Kobra X vale a pena?", title_face, 560)[:3]:
        draw.text((78, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 66
    draw.text((80, y + 18), "Comparativo honesto com Bambu Lab A1", font=font(28, True), fill=(0, 210, 255, 255))

    chip_x = 78
    for chip in ["Multicolor", "ACE Gen 2", "Speed X2", "Compra consciente"]:
        box = draw.textbbox((0, 0), chip, font=font(19, True))
        chip_w = box[2] - box[0] + 26
        draw.rounded_rectangle((chip_x, 532, chip_x + chip_w, 574), radius=20, fill=(8, 18, 32, 240), outline=(255, 106, 19, 210), width=2)
        draw.text((chip_x + 13, 542), chip, font=font(19, True), fill=(235, 244, 255, 255))
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


def product_block(item: dict, media_url: str, caption: str) -> str:
    return f"""
<figure class="wp-block-image aligncenter" style="max-width:760px;margin:28px auto;text-align:center;">
  <a href="{item['url']}" target="_blank" rel="noopener noreferrer sponsored">
    <img src="{media_url}" alt="{item['alt']}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" />
  </a>
  <figcaption style="font-size:14px;color:#666;">Produto indicado: {item['name']} - {caption}</figcaption>
</figure>
"""


def build_content(media_urls: dict[int, str]) -> str:
    kobra = product_block(AFFILIATES[0], media_urls[5], "combo principal analisado neste comparativo.")
    bambu = product_block(AFFILIATES[1], media_urls[2], "referencia de ecossistema simples para comparar antes da compra.")
    pla = product_block(AFFILIATES[2], media_urls[1], "filamento para testes, benchy e primeiras calibracoes sem gastar tanto.")
    return f"""
<p><strong>Kobra X vale a pena</strong> para quem quer uma impressora multicolor mais moderna e com promessa de menor desperdicio, mas ela ainda precisa ser analisada com calma antes de substituir a Bambu Lab A1 como escolha segura para iniciantes.</p>
<p>Este artigo cruza duas fontes: o unboxing do canal Barbacast e o video oficial da Anycubic. A ideia nao e repetir propaganda, e sim separar o que parece forte, o que ainda precisa de teste e para quem a compra faz sentido.</p>

<h2><strong>Kobra X vale a pena?</strong></h2>
<p>A resposta curta: pode valer a pena se o preco ficar abaixo da Bambu Lab A1 Combo e se voce quer testar multicolor com recursos mais novos. Para quem quer o ecossistema mais maduro, a A1 ainda continua uma referencia forte.</p>
<p>No video do Barbacast, a Kobra X aparece como uma concorrente direta da A1. O apresentador destaca que comprou a unidade, fez unboxing, montou a maquina e imprimiu um benchy como primeiro teste.</p>

{youtube_embed(VIDEO_REVIEW)}

<div style="border:2px solid #f97316;background:#160b05;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#fb923c;font-weight:800;text-transform:uppercase;">Resumo honesto</p>
  <p style="margin:0;color:#ffe7d1;">A Kobra X promete multicolor mais integrado, menos desperdicio e volume levemente maior. A Bambu Lab A1 ainda vence em maturidade de ecossistema e experiencia comprovada.</p>
</div>

<h2><strong>O que chamou atencao no unboxing</strong></h2>
<p>O primeiro ponto e a semelhanca visual com a Bambu Lab A1. O proprio video comenta que a impressora lembra bastante a A1 no formato geral, mas traz tela maior, conexoes simples e montagem aparentemente direta.</p>
<p>A transcricao tambem cita configuracao em portugues do Brasil, aplicativo, fatiador da Anycubic e uma calibracao inicial de cerca de 35 minutos. Isso interessa para iniciante, porque a experiencia fora da caixa define se a primeira semana sera produtiva ou frustrante.</p>
<p>O benchy inicial saiu limpo, segundo a avaliacao do video. Mas isso ainda e primeiro contato, nao teste de longo prazo. Um benchy bonito nao prova durabilidade, repetibilidade nem suporte tecnico.</p>

<h2><strong>Multicolor e ACE Gen 2</strong></h2>
<p>O video oficial da Anycubic apresenta a Kobra X como uma solucao de entrada para impressao multicolor. A promessa principal e integrar o sistema ACE Gen 2 ao conjunto, reduzindo dependencia de hardware externo grande.</p>
<p>A marca tambem afirma que o cortador fica a 35 mm do bico, o que ajudaria a reduzir purge e desperdicio nas trocas de cor. No material oficial, um dinossauro de quatro cores aparece com tempo de 9h34 na Kobra X contra 15h21 em outras impressoras.</p>
<p>Esse dado e forte para marketing, mas deve ser lido como promessa de fabricante. Para compra real, o ideal e comparar o mesmo arquivo, mesmo filamento, mesmo perfil e mesma quantidade de trocas.</p>

{youtube_embed(VIDEO_OFICIAL)}

<h2><strong>Kobra X vs Bambu Lab A1</strong></h2>
<p>Na comparacao feita no video do Barbacast, a Kobra X aparece com algumas vantagens no papel: velocidade maxima citada de ate 600 mm/s, volume de impressao um pouco maior e promessa de menos desperdicio nas trocas de cor.</p>
<p>A Bambu Lab A1, por outro lado, tem um ecossistema mais conhecido. O app, os perfis, o AMS Lite, a comunidade, os acessorios e a disponibilidade de informacao contam muito para quem esta comecando.</p>
<p>Um detalhe interessante da transcricao e o comentario sobre ruido. O apresentador diz que, pela memoria dele, achou a Kobra X mais silenciosa que a A1 naquele primeiro teste, embora tambem reconheca que nao estava com as duas lado a lado.</p>

<h2><strong>Quando a Kobra X faz sentido</strong></h2>
<p>A Kobra X faz mais sentido para quem quer entrar no multicolor, gosta de testar novidade e aceita aprender um ecossistema menos consolidado. Tambem pode ser atraente se o preco do combo ficar realmente abaixo da A1 Combo no Brasil.</p>
<p>Ela tambem chama atencao para quem se incomoda com desperdicio de filamento em troca de cor. Se a promessa de menos purge se confirmar em testes independentes, isso pode pesar bastante para quem imprime personagens, logos, placas e decoracao colorida.</p>

{kobra}

<h2><strong>Quando a Bambu Lab A1 ainda e mais segura</strong></h2>
<p>A A1 ainda tende a ser a escolha mais segura para quem quer menos descoberta e mais previsibilidade. Isso nao significa que ela seja perfeita, mas o ecossistema Bambu ja tem mais usuarios, mais perfis prontos e mais conteudo de suporte.</p>
<p>Para um iniciante absoluto, isso pesa. Quando algo da errado, encontrar resposta rapida em grupo, video e forum pode valer mais do que um recurso novo no papel.</p>

{bambu}

<h2><strong>Filamento para testar antes de confiar</strong></h2>
<p>Em qualquer impressora nova, o primeiro erro e gastar filamento caro logo nos testes. Benchy, torre de temperatura, primeira camada e pecas pequenas servem para entender fluxo, retracao, aderencia e ruido antes de imprimir algo grande.</p>
<p>Um PLA de custo menor ajuda nesse periodo de validacao. Se a maquina passar bem nos testes simples, ai faz sentido usar cores melhores para modelos multicolor ou pecas de acabamento.</p>

{pla}

<h2><strong>Pontos de atencao antes de comprar</strong></h2>
<ul>
  <li>confirme se o produto esta em pronta entrega ou pre-venda;</li>
  <li>compare o preco final com frete e garantia;</li>
  <li>verifique disponibilidade de bicos, pecas e assistencia;</li>
  <li>procure testes reais de purge em multicolor;</li>
  <li>confira se o fatiador da Anycubic atende seu fluxo;</li>
  <li>nao compre apenas pela promessa de ser "matadora da A1".</li>
</ul>

<h2><strong>Veredito para o maker brasileiro</strong></h2>
<p>A Kobra X parece uma concorrente real da Bambu Lab A1, principalmente por trazer multicolor, volume levemente maior e promessa de reduzir desperdicio. O video oficial vende uma proposta forte. O unboxing mostra uma primeira impressao positiva.</p>
<p>Mesmo assim, o melhor caminho e comprar com expectativa correta. Se voce quer novidade e preco agressivo, a Kobra X merece entrar na lista. Se quer o caminho mais conhecido, a A1 continua dificil de ignorar.</p>

<h2><strong>Consideracoes Finais</strong></h2>
<p>A Kobra X nao deve ser vista como compra magica, mas como uma alternativa interessante em 2026. Ela pode ser muito boa se entregar, na pratica, o que promete em multicolor, tempo e desperdicio.</p>
<p>Para o Clube 3D Brasil, a recomendacao e simples: compare preco real no Brasil, veja garantia, acompanhe testes de longo prazo e escolha pela sua necessidade, nao pelo hype.</p>

<h2><strong>Kobra X vale a pena - Perguntas Frequentes</strong></h2>
<h3><strong>A Kobra X e melhor que a Bambu Lab A1?</strong></h3>
<p>Ainda e cedo para afirmar isso de forma definitiva. A Kobra X tem promessas fortes em multicolor, velocidade e desperdicio. A Bambu Lab A1 tem ecossistema mais maduro e mais historico de uso real.</p>

<h3><strong>A Kobra X imprime em varias cores?</strong></h3>
<p>Sim, a proposta da Kobra X Combo e trabalhar com impressao multicolor usando o sistema ACE Gen 2. O ponto que precisa ser observado em testes reais e quanto material ela desperdiça nas trocas de cor.</p>

<h3><strong>A Kobra X e boa para iniciante?</strong></h3>
<p>Pode ser boa se o usuario aceitar aprender o ecossistema Anycubic. Para quem quer o caminho com mais tutoriais e comunidade pronta, a Bambu Lab A1 ainda pode ser mais tranquila.</p>

<h3><strong>Vale comprar a Kobra X na pre-venda?</strong></h3>
<p>Pre-venda pode valer quando o desconto e forte e a loja oferece garantia clara. Se a diferenca de preco for pequena, pode ser melhor esperar reviews de longo prazo e relatos de usuarios brasileiros.</p>

<h3><strong>O que olhar antes de comprar uma impressora multicolor?</strong></h3>
<p>Veja custo de filamento desperdicado, facilidade de troca de cor, suporte do fatiador, disponibilidade de pecas, garantia e tamanho da comunidade. Multicolor bonito nao compensa maquina dificil de manter.</p>
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
        "excerpt": "Kobra X vale a pena? Veja comparativo honesto com Bambu Lab A1, multicolor, desperdicio, velocidade e pontos de atencao.",
        "status": "draft",
        "tags": ["kobra x", "bambu lab a1", "impressora 3d", "review impressora 3d", "multicolor"],
        "categories": ["Impressoras e Reviews"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Kobra X Vale a Pena? Comparativo com Bambu Lab A1",
        "yoast_meta": "Kobra X vale a pena? Compare com Bambu Lab A1 em multicolor, desperdicio, velocidade, preco e compra consciente.",
        "gerado_em": "2026-05-16",
        "origem": "youtube_manual_9FF2UnfhaBk_8k4rUUexwUs",
    }

    existente = pub._buscar_post_por_slug(SLUG)
    if existente:
        media_capa_id, _ = pub.upload_media(str(capa), alt_text=f"{TITLE} para impressao 3D")
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
