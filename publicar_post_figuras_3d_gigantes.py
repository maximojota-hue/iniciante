"""
Publica como rascunho o post #7:
"Como Imprimir Figuras 3D Grandes com Qualidade".

Baseado no video:
https://www.youtube.com/watch?v=DXH71bnrFwY

Nao chama API externa de conteudo. O texto foi preparado no fluxo do chat e
este script apenas cria capa, envia imagens afiliadas e publica no WordPress.
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


TITLE = "Como Imprimir Figuras 3D Grandes com Qualidade"
SLUG = "como-imprimir-figuras-3d-grandes-com-qualidade"
KEYPHRASE = "imprimir figuras 3D grandes"
VIDEO_URL = "https://www.youtube.com/watch?v=DXH71bnrFwY&t=14s"
CAPA_ORIGINAL = Path(r"C:\Users\jcarlos\Pictures\Screenshots\Captura de tela 2026-05-16 110656.png")
CAPA_PATH = Path("downloads/capas/como-imprimir-figuras-3d-grandes-com-qualidade.jpg")

AFFILIATES = [
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para imprimir figuras 3D grandes com menor custo",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para imprimir figuras 3D e miniaturas",
    },
    {
        "id": 3,
        "name": "PLA Bambu Lab Beige",
        "url": "https://amzn.to/4scbIb1",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 16_01_16.png"),
        "alt": "PLA Bambu Lab Bege para acabamento de figuras 3D",
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
    bg = ImageEnhance.Contrast(bg).enhance(1.16)
    bg = ImageEnhance.Color(bg).enhance(1.12)
    bg = bg.filter(ImageFilter.GaussianBlur(0.25))

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 88))
    draw.rectangle((0, 0, 690, h), fill=(0, 0, 0, 188))
    draw.rounded_rectangle((46, 46, 1154, 629), radius=24, outline=(255, 106, 19, 230), width=3)
    draw.rounded_rectangle((78, 78, 372, 126), radius=12, fill=(255, 106, 19, 245))
    draw.text((101, 88), "GUIA MAKER", font=font(25, True), fill=(8, 8, 8, 255))

    y = 162
    title_face = font(57, True)
    for line in wrap(draw, "Figuras 3D grandes com qualidade", title_face, 590)[:3]:
        draw.text((78, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 64
    draw.text((80, y + 18), "configuracoes, suportes e acabamento", font=font(28, True), fill=(0, 210, 255, 255))

    chip_x = 78
    for chip in ["0,12 mm", "5% gyroid", "orientacao", "pintura"]:
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
    pla_barato = product_block(AFFILIATES[0], media_urls[1], "bom para testes, pecas grandes e validacao antes do acabamento final.")
    impressora = product_block(AFFILIATES[1], media_urls[2], "opcao compacta para quem quer comecar a imprimir figuras e miniaturas.")
    pla_bege = product_block(AFFILIATES[2], media_urls[3], "cor util para pele, bustos, personagens e pecas que vao receber pintura.")
    return f"""
<p><strong>Imprimir figuras 3D grandes</strong> com qualidade nao depende apenas de aumentar a escala do arquivo. Quando a peca fica maior, qualquer erro de suporte, orientacao, camada ou acabamento aparece muito mais.</p>
<p>Este artigo foi criado a partir do video sobre figuras gigantes de Goku e Vegeta, onde o criador mostra o processo de impressao em escala grande, configuracoes de fatiamento, orientacao das pecas, suportes e pintura final.</p>

{youtube_embed(VIDEO_URL)}

<div style="border:2px solid #f97316;background:#160b05;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#fb923c;font-weight:800;text-transform:uppercase;">Resumo rapido</p>
  <p style="margin:0;color:#ffe7d1;">Para figuras grandes, use camada fina onde o acabamento importa, pouco preenchimento, bons perimetros, suporte bem posicionado e orientacao pensada para esconder marcas.</p>
</div>

<h2><strong>O segredo para imprimir figuras 3D grandes</strong></h2>
<p>O ponto principal do video e que figuras grandes precisam ser tratadas como projeto, nao como impressao rapida. O criador tinha pouco tempo para preparar duas figuras grandes de anime para um evento, por isso precisou equilibrar qualidade, prazo e risco de falha.</p>
<p>A decisao mais importante foi imprimir em escala grande, mas em partes. Isso reduz risco, facilita acabamento e permite corrigir uma peca especifica sem perder o modelo inteiro.</p>

<h2><strong>Configuracao de camada: quando usar 0,12 mm</strong></h2>
<p>No video, a altura de camada citada para ganhar resolucao foi <strong>0,12 mm</strong>. Essa configuracao ajuda muito em rosto, cabelo, musculos, roupa e regioes curvas, porque diminui o efeito de degrau entre as camadas.</p>
<p>O lado negativo e o tempo. Uma figura grande em 0,12 mm pode demorar bastante, entao vale usar essa resolucao quando a peca realmente precisa de acabamento fino. Para bases, partes internas ou areas que serao lixadas com mais forca, voce pode avaliar camadas maiores.</p>

<h2><strong>Preenchimento: menos infill, mais parede</strong></h2>
<p>Uma dica forte do video e usar pouco preenchimento. Ele cita <strong>gyroid com 5%</strong>, porque em figuras decorativas o preenchimento nao costuma ser o que segura a qualidade visual.</p>
<p>Em peca grande de personagem, o que importa mais e ter boa parede externa, boa aderencia e orientacao correta. Preenchimento demais aumenta tempo, peso e gasto de filamento sem necessariamente melhorar o acabamento.</p>

{pla_barato}

<h2><strong>Orientacao da peca evita marcas feias</strong></h2>
<p>A orientacao e uma das partes mais importantes para imprimir figuras 3D grandes. Se voce posiciona a cabeca, o cabelo ou o rosto de qualquer jeito, os suportes podem cair em regioes visiveis e deixar marcas dificeis de esconder.</p>
<p>No video, a peca e girada para reduzir suporte em areas como sobrancelha, rosto e detalhes aparentes. Essa e uma decisao que separa uma impressao bonita de uma peca que exige horas extras de lixamento.</p>

<h2><strong>Suporte normal ou suporte arvore?</strong></h2>
<p>Suporte arvore economiza material e pode ser excelente em miniaturas, mas o video chama atencao para um risco: em impressao grande e com prazo apertado, suporte arvore pode ter mais chance de falhar dependendo da geometria.</p>
<p>Por isso, em algumas partes ele prefere suporte normal, mais ajustado e previsivel. A licao para o maker brasileiro e simples: se a peca e grande, cara e demorada, escolha o suporte pelo risco, nao apenas pela economia de filamento.</p>

<h2><strong>Primeira camada e aderencia</strong></h2>
<p>Outro detalhe citado e a expansao da primeira camada, usada para aumentar a area de contato e melhorar a aderencia. Isso ajuda especialmente em partes altas, finas ou com suporte, onde uma pequena falha pode derrubar muitas horas de impressao.</p>
<p>Antes de imprimir uma figura enorme, faca uma peca menor com o mesmo filamento para testar temperatura, fluxo, retracao e aderencia. Esse teste custa pouco e evita perder muito material depois.</p>

{impressora}

<h2><strong>Costura: esconda antes de fatiar</strong></h2>
<p>Em figuras grandes, a costura da impressao fica mais visivel. Se ela cair no rosto, no peito ou em uma parte lisa, o acabamento sofre. O melhor e posicionar a costura em uma area escondida, como costas, dobra de roupa, encaixe ou regiao que sera lixada.</p>
<p>Esse cuidado deve ser feito antes de fatiar. Depois que a peca esta impressa, esconder costura vira trabalho manual.</p>

<h2><strong>Acabamento e pintura fazem parte do plano</strong></h2>
<p>O video tambem mostra processo de pos-impressao e pintura. Para figuras grandes, a impressao e apenas metade do resultado. Remover suporte com cuidado, lixar marcas, encaixar partes e pintar com paciencia muda completamente a percepcao de qualidade.</p>
<p>Se voce pretende pintar, escolha cores de filamento que facilitem o fundo. Tons claros e neutros ajudam em pele, bustos e personagens, enquanto cores muito fortes podem exigir mais primer.</p>

{pla_bege}

<h2><strong>Checklist para imprimir figura grande sem desperdicar filamento</strong></h2>
<ul>
  <li>separe o modelo em partes quando possivel;</li>
  <li>use altura de camada menor nas areas visiveis;</li>
  <li>prefira pouco infill e paredes bem configuradas;</li>
  <li>oriente a peca para esconder suportes e costuras;</li>
  <li>teste suporte normal e suporte arvore antes da impressao final;</li>
  <li>garanta boa aderencia de primeira camada;</li>
  <li>planeje lixamento, encaixe, primer e pintura.</li>
</ul>

<h2><strong>Vale a pena imprimir figuras 3D grandes?</strong></h2>
<p>Vale muito a pena quando voce entende que o projeto exige tempo e planejamento. Figuras grandes chamam atencao, geram conteudo para redes sociais, podem virar presente, decoracao, exposicao ou produto sob encomenda.</p>
<p>Mas nao e o melhor tipo de impressao para fazer no improviso. Uma figura grande consome horas, filamento e energia. Por isso, o ideal e testar em menor escala, validar suporte e so depois partir para a versao final.</p>

<h2><strong>Consideracoes finais</strong></h2>
<p>O segredo para imprimir figuras 3D grandes com qualidade esta em controlar risco: camada adequada, pouco preenchimento, suporte confiavel, orientacao inteligente e acabamento bem planejado.</p>
<p>Para quem esta comecando, a melhor estrategia e usar filamento mais acessivel nos testes, escolher uma impressora simples de operar e deixar o filamento premium para a peca final.</p>

<h2><strong>Perguntas Frequentes</strong></h2>
<h3><strong>Qual altura de camada usar em figuras 3D grandes?</strong></h3>
<p>Para acabamento fino, 0,12 mm e uma boa referencia. Se a peca for muito grande ou pouco detalhada, voce pode testar 0,16 mm ou 0,20 mm para economizar tempo.</p>

<h3><strong>Quanto preenchimento usar em figura decorativa?</strong></h3>
<p>Em muitas figuras decorativas, 5% a 10% pode ser suficiente. O mais importante e configurar paredes e suporte corretamente, porque o acabamento externo pesa mais que o miolo.</p>

<h3><strong>Suporte arvore e melhor para miniaturas?</strong></h3>
<p>Depende da geometria. Suporte arvore economiza material e pode marcar menos, mas em pecas grandes pode falhar se ficar instavel. Para projeto longo, teste antes.</p>

<h3><strong>Como evitar marcas de suporte no rosto da figura?</strong></h3>
<p>Oriente a peca para que os suportes fiquem em areas menos visiveis. Evite suporte direto em rosto, sobrancelha, cabelo frontal e detalhes que serao vistos de perto.</p>

<h3><strong>Qual filamento usar para figuras que serao pintadas?</strong></h3>
<p>PLA claro ou neutro costuma facilitar. Tons bege, branco ou cinza ajudam a aplicar primer e pintura com menos camadas.</p>
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
        "excerpt": "Aprenda como imprimir figuras 3D grandes com qualidade usando camada fina, pouco infill, suporte correto, orientacao e acabamento.",
        "status": "draft",
        "tags": ["figuras 3d", "impressao 3d", "miniaturas", "anime", "acabamento 3d"],
        "categories": ["STL Geek"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Como Imprimir Figuras 3D Grandes com Qualidade",
        "yoast_meta": "Veja como imprimir figuras 3D grandes com qualidade: camada 0,12 mm, infill, suportes, orientacao, acabamento e pintura.",
        "gerado_em": "2026-05-16",
        "origem": "youtube_manual_DXH71bnrFwY",
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
