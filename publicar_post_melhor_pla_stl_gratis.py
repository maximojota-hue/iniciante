"""
Publica como rascunho o post #3:
"Melhor PLA para imprimir STL gratis".

Nao chama API externa de conteudo. O texto foi preparado no chat e este
script apenas cria capa, envia imagens e publica o rascunho no WordPress.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from publisher import WordPressPublisher


TITLE = "Melhor PLA para Imprimir STL Gratis: Como Escolher Filamento Barato Sem Perder Qualidade"
SLUG = "melhor-pla-para-imprimir-stl-gratis"
KEYPHRASE = "melhor PLA para imprimir STL gratis"
CAPA_PATH = Path("downloads/capas/melhor-pla-para-imprimir-stl-gratis.jpg")

AFFILIATES = [
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para testar STL gratis com baixo custo",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para imprimir STL gratis com facilidade",
    },
    {
        "id": 3,
        "name": "PLA Bambu Lab Beige",
        "url": "https://amzn.to/4scbIb1",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 16_01_16.png"),
        "alt": "PLA Bambu Lab Beige para miniaturas e pecas decorativas",
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
    for affiliate in AFFILIATES:
        if not affiliate["image"].exists():
            raise SystemExit(f"Imagem nao encontrada: {affiliate['image']}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    bg = Image.new("RGB", (w, h), (7, 10, 16))
    left = fit_cover(AFFILIATES[0]["image"], (w // 2, h))
    right = fit_cover(AFFILIATES[2]["image"], (w // 2, h))
    bg.paste(left, (0, 0))
    bg.paste(right, (w // 2, 0))
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.1).convert("RGBA")

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 112))
    draw.rectangle((0, 0, 700, h), fill=(0, 0, 0, 150))
    draw.rounded_rectangle((54, 54, 1146, 621), radius=24, outline=(84, 230, 66, 210), width=3)
    draw.rounded_rectangle((76, 78, 336, 126), radius=12, fill=(0, 210, 255, 235))
    draw.text((96, 88), "GUIA PLA 2026", font=font(27, True), fill=(0, 10, 18, 255))

    y = 166
    title_face = font(62, True)
    for line in wrap(draw, "Melhor PLA para imprimir STL gratis", title_face, 620)[:4]:
        draw.text((76, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 68
    draw.text((78, y + 18), "Barato para testar. Bom para finalizar.", font=font(31, True), fill=(84, 230, 66, 255))

    chip_x = 76
    for chip in ["Voolt Outlet", "Bambu A1 Mini", "PLA Beige"]:
        box = draw.textbbox((0, 0), chip, font=font(22, True))
        chip_w = box[2] - box[0] + 32
        draw.rounded_rectangle((chip_x, 532, chip_x + chip_w, 574), radius=20, fill=(8, 18, 32, 240), outline=(255, 91, 190, 190), width=2)
        draw.text((chip_x + 16, 541), chip, font=font(22, True), fill=(235, 244, 255, 255))
        chip_x += chip_w + 14

    draw.text((76, 598), "Clube 3D Brasil", font=font(24, False), fill=(218, 230, 245, 230))
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


def build_content(media_urls: dict[int, str]) -> str:
    voolt = product_block(AFFILIATES[0], media_urls[1], "boa opcao para testes baratos, prototipos e validacao de STL.")
    a1mini = product_block(AFFILIATES[1], media_urls[2], "impressora compacta para iniciar com menos configuracao manual.")
    beige = product_block(AFFILIATES[2], media_urls[3], "filamento para miniaturas, decoracao e acabamento visual mais limpo.")

    return f"""
<p>Escolher o <strong>melhor PLA para imprimir STL gratis</strong> nao significa comprar sempre o rolo mais caro. Para o maker brasileiro, a melhor estrategia e separar dois usos: um PLA barato para testar modelos e um PLA mais consistente para finalizar pecas bonitas.</p>

<p>STL gratis e excelente para aprender, mas tambem pode desperdiçar material quando o arquivo tem escala errada, suporte ruim ou detalhe fino demais. Por isso, antes de gastar um rolo premium, vale imprimir pequeno, validar suporte e so depois fazer a versao final.</p>

<div style="border:2px solid #22c55e;background:#07140c;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#22c55e;font-weight:800;text-transform:uppercase;">Resumo rapido</p>
  <p style="margin:0;color:#d8ffe5;">Use PLA barato para testar STL gratis. Use PLA de melhor acabamento para a peca final. Para iniciantes, priorize facilidade de impressao, boa primeira camada, diametro consistente e baixa chance de entupimento.</p>
</div>

<h2>O que faz um PLA ser bom para STL gratis?</h2>
<p>Um bom PLA para STL gratis precisa ser previsivel. Isso quer dizer: aderir bem na mesa, fluir sem falhar, nao variar muito o diametro e manter boa aparencia mesmo em configuracoes simples. Iniciante precisa de filamento que perdoe pequenos erros, nao de material temperamental.</p>
<p>Para modelos decorativos, bustos, chaveiros, miniaturas e personagens, o PLA ainda e o ponto de partida mais amigavel. Ele imprime em temperatura moderada, nao exige camara fechada e funciona bem na maioria das impressoras FDM.</p>

<h2>Quando usar PLA barato ou outlet</h2>
<p>PLA barato ou outlet combina com teste. Se voce baixou um STL gratuito e ainda nao sabe se a escala esta correta, se o suporte vai marcar ou se o encaixe funciona, nao faz sentido gastar o filamento mais bonito logo de cara.</p>
<p>Use esse tipo de PLA para validar tamanho, tempo de impressao, suporte, orientacao e resistencia basica. Se o teste ficar bom, voce parte para a versao final com mais seguranca.</p>

{voolt}

<h2>Quando usar PLA de acabamento melhor</h2>
<p>Depois que o modelo passou no teste, ai sim vale escolher um PLA com cor mais bonita, acabamento uniforme e confiabilidade maior. Isso importa em personagens, decoracao, bustos, miniaturas, vasos, organizadores visiveis e qualquer peca que vai aparecer em foto ou venda.</p>
<p>Cores claras como bege ajudam muito em miniaturas e objetos decorativos porque mostram linhas, sombras e textura de forma mais suave. Tambem sao boas para pintura posterior, ja que exigem menos cobertura que filamentos escuros.</p>

{beige}

<h2>A impressora tambem influencia o resultado do PLA</h2>
<p>O filamento ajuda, mas a impressora precisa entregar primeira camada boa, extrusao estavel e resfriamento suficiente. Para quem esta comecando, maquinas com nivelamento automatico, perfil pronto e ecossistema simples reduzem bastante a curva de aprendizado.</p>
<p>Uma impressora compacta como a Bambu Lab A1 Mini conversa bem com esse publico porque simplifica o fluxo: montar, fatiar, mandar imprimir e ajustar menos coisa manualmente. Para quem quer imprimir STL gratis todo dia, isso economiza paciencia.</p>

{a1mini}

<h2>Configurações seguras para PLA em modelos STL</h2>
<p>Para começar, use camada de 0,20 mm em testes rapidos. Em figuras pequenas ou detalhes finos, reduza para 0,16 mm ou 0,12 mm depois que o modelo provar que funciona. Preenchimento entre 10% e 15% basta para muita peca decorativa.</p>
<p>Temperatura comum de PLA fica na faixa indicada pelo fabricante, frequentemente em torno de 200 a 220 graus Celsius. A mesa costuma trabalhar bem perto de 50 a 60 graus Celsius, mas isso muda conforme impressora, superficie e marca do filamento.</p>
<p>O ponto mais importante e observar a primeira camada. Se ela esta falhando, nada depois compensa. Ajuste limpeza da mesa, nivelamento, offset e fluxo antes de culpar o STL ou o filamento.</p>

<h2>Como comparar PLA sem cair em propaganda</h2>
<p>Compare o que aparece na impressao, nao so o que aparece no anuncio. Um PLA bom para voce deve entregar menos falhas, menos stringing, boa adesao entre camadas e acabamento aceitavel no seu tipo de peca.</p>
<p>Crie um teste padrao: um chaveiro, uma miniatura simples e uma peca com encaixe. Imprima os mesmos arquivos com filamentos diferentes. Assim voce entende qual rolo serve para teste, qual serve para acabamento e qual nao vale recomprar.</p>

<h2>Tabela rapida: qual PLA usar?</h2>
<table style="width:100%;border-collapse:collapse;margin:22px 0;">
  <thead>
    <tr>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Situacao</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Melhor escolha</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Motivo</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ddd;padding:10px;">Testar STL novo</td><td style="border:1px solid #ddd;padding:10px;">PLA outlet/barato</td><td style="border:1px solid #ddd;padding:10px;">Reduz custo se o arquivo falhar.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Miniatura decorativa</td><td style="border:1px solid #ddd;padding:10px;">PLA de cor clara ou acabamento melhor</td><td style="border:1px solid #ddd;padding:10px;">Mostra detalhes e facilita pintura.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Peca funcional leve</td><td style="border:1px solid #ddd;padding:10px;">PLA confiavel com boa adesao</td><td style="border:1px solid #ddd;padding:10px;">Mantem encaixe e resistencia basica.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Primeira impressora</td><td style="border:1px solid #ddd;padding:10px;">PLA facil + perfil pronto</td><td style="border:1px solid #ddd;padding:10px;">Menos ajustes e menos frustracao.</td></tr>
  </tbody>
</table>

<h2>Erros comuns ao comprar PLA para STL gratis</h2>
<p>O primeiro erro e comprar pela cor mais bonita sem pensar no uso. Filamento bonito nao resolve suporte ruim, escala errada ou primeira camada mal ajustada. O segundo erro e usar filamento caro para validar arquivo desconhecido.</p>
<p>Outro erro e misturar muitas variaveis: troca filamento, troca temperatura, troca velocidade e troca suporte tudo de uma vez. Mude uma coisa por vez. Assim voce aprende de verdade o que melhorou ou piorou.</p>

<h2>Conclusao</h2>
<p>O <strong>melhor PLA para imprimir STL gratis</strong> e aquele que combina com a etapa do projeto. Para teste, escolha custo-beneficio. Para acabamento, escolha consistencia e cor. Para iniciantes, escolha facilidade.</p>
<p>Se voce usar um PLA barato para validar e um PLA melhor para finalizar, vai errar menos, gastar melhor e aproveitar muito mais os arquivos gratuitos que encontra no Clube 3D Brasil e nas plataformas de STL.</p>

<h2>Perguntas frequentes</h2>

<h3>PLA barato serve para imprimir STL gratis?</h3>
<p>Sim. PLA barato e otimo para testar escala, suporte e encaixe. Para peca final decorativa, pode valer usar um PLA com acabamento mais consistente.</p>

<h3>Qual cor de PLA e melhor para miniaturas?</h3>
<p>Cores claras como bege, branco e cinza ajudam a ver detalhes e facilitam pintura. Cores muito escuras escondem textura e podem dificultar acabamento manual.</p>

<h3>Preciso de impressora cara para imprimir bem em PLA?</h3>
<p>Nao. Uma impressora bem calibrada e com perfil correto imprime PLA muito bem. Modelos com nivelamento automatico e perfis prontos ajudam iniciantes a errar menos.</p>

<h3>Qual temperatura usar no PLA?</h3>
<p>Siga a faixa do fabricante. Muitos PLAs imprimem bem entre 200 e 220 graus Celsius, com mesa entre 50 e 60 graus Celsius, mas o ideal e testar uma torre de temperatura.</p>

<h3>Como economizar filamento com STL gratis?</h3>
<p>Imprima teste menor, use preenchimento baixo em pecas decorativas, confira suporte antes de imprimir e valide o modelo com PLA barato antes da versao final.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question", "name": "PLA barato serve para imprimir STL gratis?", "acceptedAnswer": {{"@type": "Answer", "text": "Sim. PLA barato e otimo para testar escala, suporte e encaixe. Para peca final decorativa, pode valer usar um PLA com acabamento mais consistente."}}}},
    {{"@type": "Question", "name": "Qual cor de PLA e melhor para miniaturas?", "acceptedAnswer": {{"@type": "Answer", "text": "Cores claras como bege, branco e cinza ajudam a ver detalhes e facilitam pintura. Cores muito escuras escondem textura e podem dificultar acabamento manual."}}}},
    {{"@type": "Question", "name": "Preciso de impressora cara para imprimir bem em PLA?", "acceptedAnswer": {{"@type": "Answer", "text": "Nao. Uma impressora bem calibrada e com perfil correto imprime PLA muito bem. Modelos com nivelamento automatico e perfis prontos ajudam iniciantes a errar menos."}}}},
    {{"@type": "Question", "name": "Qual temperatura usar no PLA?", "acceptedAnswer": {{"@type": "Answer", "text": "Siga a faixa do fabricante. Muitos PLAs imprimem bem entre 200 e 220 graus Celsius, com mesa entre 50 e 60 graus Celsius, mas o ideal e testar uma torre de temperatura."}}}},
    {{"@type": "Question", "name": "Como economizar filamento com STL gratis?", "acceptedAnswer": {{"@type": "Answer", "text": "Imprima teste menor, use preenchimento baixo em pecas decorativas, confira suporte antes de imprimir e valide o modelo com PLA barato antes da versao final."}}}}
  ]
}}
</script>
"""


def main() -> None:
    carregar_env()
    with open("config.json", encoding="utf-8") as f:
        base_config = json.load(f)

    config = {
        "wp_url": base_config.get("wp_url", "https://clube3dbrasil.com"),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_PASS", ""),
        "telegram_notify_statuses": os.environ.get("TELEGRAM_NOTIFY_STATUSES", "publish"),
    }
    if not config["wp_user"] or not config["wp_app_password"]:
        raise SystemExit("WP_USER/WP_PASS nao encontrados no .env.")

    capa = criar_capa()
    publisher = WordPressPublisher(config)
    if not publisher.testar_conexao():
        raise SystemExit("Falha na conexao WordPress.")

    media_urls: dict[int, str] = {}
    media_ids: dict[int, int] = {}
    for item in AFFILIATES:
        media_id, media_url = publisher.upload_media(str(item["image"]), alt_text=item["alt"])
        if not media_url:
            raise SystemExit(f"Falha ao enviar imagem do afiliado #{item['id']}.")
        media_urls[item["id"]] = media_url
        media_ids[item["id"]] = media_id or 0

    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": build_content(media_urls),
        "excerpt": "Veja como escolher o melhor PLA para imprimir STL gratis sem desperdiçar filamento: quando usar PLA barato, PLA de acabamento e impressora certa.",
        "status": "draft",
        "tags": ["PLA", "filamento PLA", "STL gratis", "Bambu Lab", "Voolt3D", "A1 Mini", "impressao 3D"],
        "categories": ["Filamentos"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Melhor PLA para Imprimir STL Gratis | Guia 2026",
        "yoast_meta": "Veja como escolher o melhor PLA para imprimir STL gratis sem desperdiçar filamento: PLA barato, PLA de acabamento e dicas para iniciantes.",
    }

    result = publisher.publicar_post(post, skip_if_exists=True)
    print(json.dumps({"capa": str(capa), "produtos_media": media_ids, "post": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
