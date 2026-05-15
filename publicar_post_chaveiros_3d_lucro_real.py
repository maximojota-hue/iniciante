"""
Publica como rascunho o post #4:
"Vale a Pena Vender Chaveiros 3D?".

Baseado na analise da transcricao do video:
https://www.youtube.com/watch?v=0B6A_Z6-iF0

Nao chama API externa de conteudo. O texto foi preparado no chat e este
script apenas cria capa, envia imagens e publica o rascunho no WordPress.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from publisher import WordPressPublisher


TITLE = "Vale a Pena Vender Chaveiros 3D? Custos, Lucro e Realidade"
SLUG = "vale-a-pena-vender-chaveiros-3d"
KEYPHRASE = "vender chaveiros 3D"
YOUTUBE_URL = "https://www.youtube.com/watch?v=0B6A_Z6-iF0"
CAPA_PATH = Path("downloads/capas/vale-a-pena-vender-chaveiros-3d.jpg")

AFFILIATES = [
    {
        "id": 1,
        "name": "PLA Voolt Outlet",
        "url": "https://meli.la/1LzFxA3",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"),
        "alt": "PLA Voolt Outlet para produzir chaveiros 3D com baixo custo",
    },
    {
        "id": 2,
        "name": "Bambu Lab A1 Mini",
        "url": "https://meli.la/18dLsT9",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 20_29_02.png"),
        "alt": "Bambu Lab A1 Mini para comecar a vender chaveiros 3D",
    },
    {
        "id": 4,
        "name": "Argola para chaveiro",
        "url": "https://meli.la/21q3Xkn",
        "image": Path(r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\argola.jpg"),
        "alt": "Argola para chaveiro usada em chaveiros impressos em 3D",
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
    for item in AFFILIATES:
        if not item["image"].exists():
            raise SystemExit(f"Imagem nao encontrada: {item['image']}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    left = fit_cover(AFFILIATES[1]["image"], (w // 2, h))
    right = fit_cover(AFFILIATES[2]["image"], (w // 2, h))
    bg = Image.new("RGB", (w, h), (7, 10, 16))
    bg.paste(left, (0, 0))
    bg.paste(right, (w // 2, 0))
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.05)
    bg = bg.filter(ImageFilter.GaussianBlur(0.35)).convert("RGBA")

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 112))
    draw.rectangle((0, 0, 710, h), fill=(0, 0, 0, 170))
    draw.rounded_rectangle((54, 54, 1146, 621), radius=24, outline=(255, 106, 19, 220), width=3)
    draw.rounded_rectangle((76, 78, 376, 126), radius=12, fill=(84, 230, 66, 245))
    draw.text((96, 88), "RENDA COM 3D", font=font(27, True), fill=(0, 14, 8, 255))

    y = 166
    title_face = font(62, True)
    for line in wrap(draw, "Vender chaveiros 3D vale a pena?", title_face, 630)[:4]:
        draw.text((76, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 68
    draw.text((78, y + 18), "Custos, lucro real e armadilhas", font=font(31, True), fill=(0, 210, 255, 255))

    chip_x = 76
    for chip in ["PLA", "A1 Mini", "Argolas"]:
        box = draw.textbbox((0, 0), chip, font=font(22, True))
        chip_w = box[2] - box[0] + 32
        draw.rounded_rectangle((chip_x, 532, chip_x + chip_w, 574), radius=20, fill=(8, 18, 32, 240), outline=(84, 230, 66, 190), width=2)
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
    bloco_pla = product_block(AFFILIATES[0], media_urls[1], "filamento para testar modelos, validar chaveiros e controlar custo.")
    bloco_a1 = product_block(AFFILIATES[1], media_urls[2], "impressora compacta para iniciar producao pequena com fluxo simples.")
    bloco_argola = product_block(AFFILIATES[2], media_urls[4], "insumo obrigatorio para transformar a peca impressa em chaveiro vendavel.")

    return f"""
<p>O video <a href="{YOUTUBE_URL}" target="_blank" rel="noopener noreferrer">"Fiquei rico com o meu negocio de chaveiros 3D"</a>, do canal Assunto Da Vez, mostra uma realidade que muita gente evita falar: <strong>vender chaveiros 3D</strong> pode gerar renda, mas dificilmente vira dinheiro rapido sem venda constante, controle de custo e produto certo.</p>

<p>Na transcricao, o criador abre a planilha e mostra algo muito util para quem esta comecando: vendas crescendo, despesas crescendo junto e lucro ainda pequeno. A licao principal e direta: fabricar chaveiro 3D e relativamente facil; vender bem, com margem e repeticao, e a parte dificil.</p>

<div style="border:2px solid #22c55e;background:#07140c;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#22c55e;font-weight:800;text-transform:uppercase;">Resumo do video</p>
  <p style="margin:0;color:#d8ffe5;">O negocio vendeu mais de 200 chaveiros em poucos meses, mas o lucro liquido ficou baixo no inicio porque filamento, energia, argolas e estoque consumiram boa parte do dinheiro que entrou.</p>
</div>

<h2>O que o video ensina sobre vender chaveiros 3D</h2>
<p>O ponto mais forte do video e a honestidade. O criador nao mostra apenas faturamento; ele mostra despesas, prejuizo inicial, estoque parado e lucro real. Isso e importante porque muita promessa na internet fala como se comprar uma impressora 3D fosse suficiente para ganhar dinheiro.</p>
<p>Segundo a transcricao, houve crescimento nas vendas: primeiro poucas unidades, depois dezenas, depois mais de cem em um mes. Mesmo assim, quando entram filamento, energia, argolas e reposicao de material, o lucro nao acompanha automaticamente o volume.</p>

<h2>Faturamento nao e lucro</h2>
<p>Esse e o primeiro erro de quem quer ganhar dinheiro com impressao 3D. Vender R$ 500, R$ 1.000 ou R$ 2.000 em chaveiros nao significa embolsar esse valor. Antes do lucro entram custos como filamento, energia, argola, embalagem, perda de impressao, tempo de acabamento e deslocamento.</p>
<p>O video deixa claro que o negocio pode estar "girando dinheiro" sem ainda dar grande lucro. Isso nao significa fracasso. Significa que a operacao esta aprendendo, formando estoque, testando mercado e descobrindo preco.</p>

<h2>O custo invisivel: estoque parado</h2>
<p>Um detalhe importante da transcricao e o estoque. O criador comenta que tem chaveiros prontos e filamento em estoque. Isso tem valor, mas ainda nao e dinheiro no bolso. Enquanto o chaveiro nao vende, ele e capital parado.</p>
<p>Por isso, para iniciantes, o melhor caminho e evitar produzir dezenas de modelos sem validar demanda. Faca poucas unidades, mostre para clientes reais e repita apenas os modelos que vendem.</p>

<h2>Filamento barato ajuda, mas precisa entrar na conta</h2>
<p>Chaveiro 3D parece pequeno, mas quando voce vende em volume o consumo de PLA aparece. Testes, falhas, cores diferentes e reposicao de estoque podem transformar filamento no maior custo variavel do negocio.</p>
<p>Uma estrategia inteligente e usar PLA de bom custo-beneficio para prototipos, testes de modelo e producao inicial. Assim voce valida preco e demanda antes de investir em cores mais caras.</p>

{bloco_pla}

<h2>Argola, corrente e acabamento tambem custam</h2>
<p>No video, a argolinha aparece como uma despesa relevante. Isso e normal: o cliente nao compra apenas uma peca impressa; ele compra um chaveiro pronto para usar. Sem argola, corrente e acabamento, o produto fica incompleto.</p>
<p>Para precificar corretamente, some o custo da argola em cada unidade. Se voce compra lote, divida o valor pelo numero de pecas aproveitaveis. Parece detalhe pequeno, mas em 100 ou 200 chaveiros vira dinheiro de verdade.</p>

{bloco_argola}

<h2>A impressora precisa trabalhar, mas nao pode virar gargalo</h2>
<p>Para comecar, uma impressora compacta pode ser suficiente. O importante e ter repetibilidade: imprimir varias unidades com pouca falha, boa primeira camada e manutencao simples. Quanto mais tempo voce perde ajustando maquina, menor fica sua margem real.</p>
<p>Uma maquina facil de operar ajuda principalmente quando o objetivo e produzir chaveiros em lote pequeno, testar modelos e manter rotina. O ganho nao esta apenas na velocidade, mas na reducao de retrabalho.</p>

{bloco_a1}

<h2>Marketplace nem sempre e o melhor caminho</h2>
<p>Outro ponto forte do video e a escolha de nao competir apenas por preco em marketplace. Em Shopee, Mercado Livre e similares, o cliente compara foto, frete e valor. Se muitos vendedores oferecem o mesmo modelo, a margem pode cair rapido.</p>
<p>Para chaveiros personalizados, venda local pode ser mais interessante: pet shops, barbearias, escolas, eventos, clubes, brindes empresariais e encomendas por WhatsApp. Quando o cliente pega a peca na mao, percebe acabamento e personalizacao melhor do que em uma listagem comum.</p>

<h2>Pet shop: bom nicho, mas venda pode estagnar</h2>
<p>No video, os chaveiros de cachorro aparecem como exemplo de nicho. Pet shop faz sentido porque o cliente ama o pet e aceita produto personalizado. Mas existe um limite: quem ja comprou um chaveiro do proprio cachorro talvez nao compre outro no mes seguinte.</p>
<p>Para evitar estagnar, pense em variacoes: chaveiro com nome, raca, plaquinha, datas especiais, presente para tutor, kits para loja e modelos sazonais. O segredo e criar motivo para recompra.</p>

<h2>Como calcular o preco de um chaveiro 3D</h2>
<p>Uma conta simples ajuda a evitar prejuizo:</p>
<ul>
  <li>custo do filamento por unidade;</li>
  <li>custo da argola e corrente;</li>
  <li>energia aproximada;</li>
  <li>embalagem;</li>
  <li>perdas e falhas;</li>
  <li>tempo de modelagem, impressao, limpeza e atendimento;</li>
  <li>margem de lucro desejada.</li>
</ul>
<p>Se o preco final fica parecido com o mercado, otimo. Se fica muito acima, voce precisa vender mais valor: personalizacao, qualidade, rapidez, nicho local ou atendimento.</p>

<h2>Checklist antes de comecar a vender chaveiros 3D</h2>
<table style="width:100%;border-collapse:collapse;margin:22px 0;">
  <thead>
    <tr>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Etapa</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">O que fazer</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Por que importa</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ddd;padding:10px;">Modelo</td><td style="border:1px solid #ddd;padding:10px;">Escolha 3 a 5 modelos para testar.</td><td style="border:1px solid #ddd;padding:10px;">Evita estoque parado.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Custo</td><td style="border:1px solid #ddd;padding:10px;">Some filamento, argola, energia e perda.</td><td style="border:1px solid #ddd;padding:10px;">Mostra lucro real.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Venda</td><td style="border:1px solid #ddd;padding:10px;">Teste pet shops, grupos e clientes locais.</td><td style="border:1px solid #ddd;padding:10px;">Venda local reduz guerra de preco.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Qualidade</td><td style="border:1px solid #ddd;padding:10px;">Padronize cor, argola e acabamento.</td><td style="border:1px solid #ddd;padding:10px;">Cliente percebe valor.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Controle</td><td style="border:1px solid #ddd;padding:10px;">Anote cada venda e cada despesa.</td><td style="border:1px solid #ddd;padding:10px;">Evita confundir faturamento com lucro.</td></tr>
  </tbody>
</table>

<h2>Entao, vale a pena?</h2>
<p>Vale a pena se voce tratar como aprendizado, renda extra e validacao de mercado. Nao vale a pena se a expectativa for comprar uma impressora hoje e pagar contas importantes no mes seguinte apenas com chaveiros.</p>
<p>O video mostra um negocio pequeno, real e em crescimento. O lucro inicial pode ser baixo, mas o conhecimento acumulado e valioso: precificacao, producao, venda, estoque, contato com cliente e melhoria de produto.</p>

<h2>Conclusao</h2>
<p><strong>Vender chaveiros 3D</strong> pode funcionar, especialmente com nichos locais e produtos personalizados. Mas a realidade e menos romantica que muitos anuncios: o dinheiro entra, os custos acompanham, e o lucro so aparece com controle.</p>
<p>Comece pequeno, calcule tudo, compre insumos com criterio, teste venda local e nao produza estoque sem demanda. A impressora fabrica; quem faz o negocio dar certo e a sua capacidade de vender com margem.</p>

<h2>Perguntas frequentes</h2>

<h3>Da para viver vendendo chaveiros 3D?</h3>
<p>Em geral, nao no comeco. Chaveiros podem gerar renda extra, mas viver disso exige volume, clientes recorrentes, margem e controle forte de custos.</p>

<h3>Qual o maior custo de um chaveiro 3D?</h3>
<p>Normalmente entram filamento, argola/corrente, energia, embalagem, perdas e tempo. Em volume, a argola e o filamento pesam bastante.</p>

<h3>Marketplace e bom para vender chaveiro 3D?</h3>
<p>Pode funcionar, mas costuma ter muita concorrencia por preco. Venda local e personalizada pode dar margem melhor para quem esta comecando.</p>

<h3>Qual impressora serve para comecar?</h3>
<p>Uma impressora FDM compacta, confiavel e facil de calibrar ja serve para testar. O importante e repetir qualidade com pouca falha.</p>

<h3>Como evitar prejuizo vendendo chaveiros 3D?</h3>
<p>Anote cada despesa, produza pouco no inicio, teste demanda antes de fazer estoque e inclua argola, energia, falhas e tempo no preco final.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question", "name": "Da para viver vendendo chaveiros 3D?", "acceptedAnswer": {{"@type": "Answer", "text": "Em geral, nao no comeco. Chaveiros podem gerar renda extra, mas viver disso exige volume, clientes recorrentes, margem e controle forte de custos."}}}},
    {{"@type": "Question", "name": "Qual o maior custo de um chaveiro 3D?", "acceptedAnswer": {{"@type": "Answer", "text": "Normalmente entram filamento, argola/corrente, energia, embalagem, perdas e tempo. Em volume, a argola e o filamento pesam bastante."}}}},
    {{"@type": "Question", "name": "Marketplace e bom para vender chaveiro 3D?", "acceptedAnswer": {{"@type": "Answer", "text": "Pode funcionar, mas costuma ter muita concorrencia por preco. Venda local e personalizada pode dar margem melhor para quem esta comecando."}}}},
    {{"@type": "Question", "name": "Qual impressora serve para comecar?", "acceptedAnswer": {{"@type": "Answer", "text": "Uma impressora FDM compacta, confiavel e facil de calibrar ja serve para testar. O importante e repetir qualidade com pouca falha."}}}},
    {{"@type": "Question", "name": "Como evitar prejuizo vendendo chaveiros 3D?", "acceptedAnswer": {{"@type": "Answer", "text": "Anote cada despesa, produza pouco no inicio, teste demanda antes de fazer estoque e inclua argola, energia, falhas e tempo no preco final."}}}}
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
        "excerpt": "Vale a pena vender chaveiros 3D? Veja custos reais, lucro, estoque, argolas, filamento e a realidade de transformar impressao 3D em renda extra.",
        "status": "draft",
        "tags": ["chaveiros 3D", "ganhar dinheiro com 3D", "impressao 3D", "renda extra", "Bambu Lab", "filamento PLA"],
        "categories": ["Ganhar Dinheiro com 3D"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Vender Chaveiros 3D Vale a Pena? Custos e Lucro",
        "yoast_meta": "Vale a pena vender chaveiros 3D? Veja custos reais, lucro, estoque, argolas, filamento e a realidade da renda extra.",
    }

    result = publisher.publicar_post(post, skip_if_exists=True)
    print(json.dumps({"capa": str(capa), "produtos_media": media_ids, "post": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
