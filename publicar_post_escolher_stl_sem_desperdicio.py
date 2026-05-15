"""
Publica como rascunho o post #2:
"Como Escolher STL Gratis Sem Desperdicar Filamento".

Nao chama API externa de conteudo. O texto foi preparado no chat e este
script apenas cria capa, envia imagens e publica o rascunho no WordPress.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from publisher import WordPressPublisher


TITLE = "Como Escolher STL Gratis Sem Desperdicar Filamento: Checklist para Iniciantes"
SLUG = "como-escolher-stl-gratis-sem-desperdicar-filamento"
KEYPHRASE = "como escolher STL gratis"
AFFILIATE_ID = 1
AFFILIATE_NAME = "PLA Voolt Outlet"
AFFILIATE_URL = "https://meli.la/1LzFxA3"
AFFILIATE_IMAGE = Path(
    r"F:\ia cloud programas\programas e arquivos blog monetizacao\paginas wordpress\fotos\produto afiliados\ChatGPT Image 13 de mai. de 2026, 15_39_41.png"
)
CAPA_PATH = Path("downloads/capas/como-escolher-stl-gratis-sem-desperdicar-filamento.jpg")


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


def fit_cover(src: Image.Image, size: tuple[int, int]) -> Image.Image:
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
    top = max(0, int((new_h - target_h) * 0.44))
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
    if not AFFILIATE_IMAGE.exists():
        raise SystemExit(f"Imagem do afiliado nao encontrada: {AFFILIATE_IMAGE}")

    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    product = Image.open(AFFILIATE_IMAGE).convert("RGB")
    bg = fit_cover(product, (w, h))
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.15)
    bg = bg.filter(ImageFilter.GaussianBlur(0.4)).convert("RGBA")

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, 710, h), fill=(0, 0, 0, 176))
    draw.rectangle((0, 0, w, h), outline=(84, 230, 66, 160), width=4)

    draw.rounded_rectangle((62, 58, 350, 108), radius=12, fill=(84, 230, 66, 245))
    draw.text((82, 70), "CHECKLIST STL 2026", font=font(25, True), fill=(0, 16, 8, 255))

    y = 148
    title_face = font(64, True)
    for line in wrap(draw, "Escolha STL gratis sem gastar filamento a toa", title_face, 600)[:4]:
        draw.text((62, y), line, font=title_face, fill=(255, 255, 255, 255))
        y += 70

    draw.text((64, y + 18), "Fotos reais, suportes, escala e teste barato", font=font(30, True), fill=(0, 210, 255, 255))

    chip_x = 62
    for chip in ["PLA outlet", "Teste menor", "Menos falhas"]:
        box = draw.textbbox((0, 0), chip, font=font(23, True))
        chip_w = box[2] - box[0] + 34
        draw.rounded_rectangle((chip_x, 535, chip_x + chip_w, 578), radius=20, fill=(8, 18, 32, 240), outline=(255, 91, 190, 190), width=2)
        draw.text((chip_x + 17, 544), chip, font=font(23, True), fill=(235, 244, 255, 255))
        chip_x += chip_w + 14

    draw.text((62, 622), "Clube 3D Brasil", font=font(24, False), fill=(218, 230, 245, 230))
    final = Image.alpha_composite(bg, layer).convert("RGB")
    final.save(CAPA_PATH, quality=92, optimize=True)
    return CAPA_PATH


def affiliate_block(product_url: str) -> str:
    alt = "PLA Voolt Outlet para testar STL gratis sem gastar muito filamento"
    return f"""
<figure class="wp-block-image aligncenter" style="max-width:760px;margin:28px auto;text-align:center;">
  <a href="{AFFILIATE_URL}" target="_blank" rel="noopener noreferrer sponsored">
    <img src="{product_url}" alt="{alt}" style="width:100%;max-width:760px;height:auto;border-radius:8px;" />
  </a>
  <figcaption style="font-size:14px;color:#666;">Produto indicado: {AFFILIATE_NAME} para testes, prototipos e impressoes de baixo custo.</figcaption>
</figure>
"""


def build_content(product_url: str) -> str:
    bloco_afiliado = affiliate_block(product_url)
    return f"""
<p>Aprender <strong>como escolher STL gratis</strong> e uma das formas mais simples de economizar tempo, energia e filamento. O problema e que muitos iniciantes baixam o primeiro arquivo bonito que aparece, mandam para o slicer e so descobrem o erro depois de horas de impressao.</p>

<p>Este post e um checklist pratico para voce olhar um modelo antes de imprimir. A ideia nao e baixar menos STL, e sim escolher melhor: arquivo com foto real, comentarios, escala correta, suporte viavel e chance maior de sair bom na sua impressora.</p>

<div style="border:2px solid #22c55e;background:#07140c;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#22c55e;font-weight:800;text-transform:uppercase;">Resumo rapido</p>
  <p style="margin:0;color:#d8ffe5;">Antes de imprimir um STL gratis, verifique foto real, comentarios, licenca, suporte, escala, paredes finas e tempo de impressao. Se tiver duvida, teste pequeno antes da peca final.</p>
</div>

<h2>1. Comece pela foto real, nao pelo render bonito</h2>
<p>Render bonito vende clique, mas nao prova que o modelo imprime bem. O ideal e procurar uma foto real da peca impressa, de preferencia enviada por usuarios diferentes. Foto real mostra camada, suporte, base, textura e proporcao.</p>
<p>Se o modelo so tem imagem gerada ou render de computador, trate como risco maior. Ele pode funcionar, mas ainda nao existe prova visual de que alguem imprimiu com sucesso. Em plataformas como Printables e MakerWorld, procure tambem os "makes", comentarios e avaliacoes.</p>

<h2>2. Leia os comentarios antes de baixar</h2>
<p>Comentarios economizam filamento. Procure frases como "imprimiu sem suporte", "precisa escalar", "a base soltou", "as juntas ficaram grudadas" ou "funcionou em PLA". Esse tipo de informacao vale mais que uma descricao bonita.</p>
<p>Se varias pessoas reclamam do mesmo problema, escolha outro arquivo ou prepare uma correcao no slicer. Quando um criador responde duvidas e atualiza o arquivo, o risco cai bastante.</p>

<h2>3. Confira se o STL tem escala correta</h2>
<p>Um erro comum e abrir o STL e descobrir que ele esta gigante, minusculo ou em unidade errada. Antes de fatiar, veja as dimensoes no slicer. Para miniaturas, chaveiros e personagens pequenos, uma escala errada pode deixar detalhes finos impossiveis de imprimir.</p>
<p>Se for testar um modelo novo, faca uma versao em 40% ou 50% quando isso nao destruir detalhes importantes. Para pecas funcionais, cuidado: reduzir escala muda encaixes, tolerancias e resistencia.</p>

<h2>4. Verifique paredes finas e partes frageis</h2>
<p>Paredes muito finas sao uma das maiores causas de falha. Em FDM, detalhes abaixo de uma largura realista para o bico podem sumir, quebrar ou sair como fios. Em personagens, isso aparece em dedos, cabelo, espada, antena, asa e orelha.</p>
<p>Como regra pratica, modelos decorativos imprimem melhor quando as partes finas nao dependem de uma unica linha de extrusao. Se o slicer mostra trechos faltando na pre-visualizacao, o problema ja apareceu antes de gastar material.</p>

<h2>5. Olhe os suportes antes de apertar imprimir</h2>
<p>Um STL gratis pode parecer simples, mas exigir muito suporte escondido. Suporte demais aumenta tempo, gasta material e pode marcar a peca. O ideal e escolher modelos com boa orientacao, base estavel e angulos que respeitam o limite da sua impressora.</p>
<p>Guias tecnicos costumam usar 45 graus como uma referencia comum: angulos mais agressivos tendem a precisar de suporte. Nao e uma lei absoluta, mas ajuda muito na triagem de modelos.</p>

{bloco_afiliado}

<h2>6. Use PLA barato para validar modelos duvidosos</h2>
<p>Quando o STL e novo, nao faz sentido gastar seu melhor filamento logo de primeira. Para teste de escala, suporte e encaixe, um PLA de bom custo-beneficio resolve muito bem. Depois que o arquivo prova que funciona, voce imprime a versao final na cor ou material mais bonito.</p>
<p>O <strong>{AFFILIATE_NAME}</strong> entra bem nesse ponto: ele serve para testar modelos gratis, validar miniaturas, fazer prototipos e imprimir pecas onde o objetivo e aprender sem medo de desperdicaro rolo mais caro.</p>

<h2>7. Prefira arquivos 3MF quando eles vierem bem preparados</h2>
<p>STL e universal, mas o 3MF pode carregar mais informacoes, como orientacao, pecas separadas e perfil de impressao. Em plataformas como MakerWorld, muitos modelos aparecem com perfis prontos para Bambu Studio, o que ajuda iniciantes.</p>
<p>Mesmo assim, nao confie cegamente. Abra a pre-visualizacao, confira tempo, suporte, material e se o perfil combina com a sua impressora.</p>

<h2>8. Faca um teste pequeno antes da peca final</h2>
<p>Para personagem, busto, miniatura ou articulado, um teste pequeno pode salvar horas. Imprima uma versao reduzida ou apenas uma parte critica: rosto, encaixe, articulacao, base ou area com suporte.</p>
<p>Se o teste falhar, voce perdeu pouco. Se funcionar, aumenta a chance da versao final sair limpa. Esse habito separa o maker paciente do maker que transforma filamento em frustracao.</p>

<h2>Checklist antes de imprimir um STL gratis</h2>
<table style="width:100%;border-collapse:collapse;margin:22px 0;">
  <thead>
    <tr>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Item</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">O que verificar</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Risco se ignorar</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ddd;padding:10px;">Foto real</td><td style="border:1px solid #ddd;padding:10px;">Existe peca impressa por alguem?</td><td style="border:1px solid #ddd;padding:10px;">Modelo bonito que nao imprime bem.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Comentarios</td><td style="border:1px solid #ddd;padding:10px;">Ha relatos de falha, suporte ou escala?</td><td style="border:1px solid #ddd;padding:10px;">Repetir erro que outro maker ja avisou.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Escala</td><td style="border:1px solid #ddd;padding:10px;">Dimensoes fazem sentido no slicer?</td><td style="border:1px solid #ddd;padding:10px;">Imprimir gigante, pequeno ou fragil.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Paredes</td><td style="border:1px solid #ddd;padding:10px;">Partes finas aparecem na pre-visualizacao?</td><td style="border:1px solid #ddd;padding:10px;">Quebras, falhas e detalhes sumindo.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Suporte</td><td style="border:1px solid #ddd;padding:10px;">A peca exige suporte demais?</td><td style="border:1px solid #ddd;padding:10px;">Mais gasto, marcas e pos-processamento.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Licenca</td><td style="border:1px solid #ddd;padding:10px;">Permite uso pessoal ou comercial?</td><td style="border:1px solid #ddd;padding:10px;">Problema ao vender a peca impressa.</td></tr>
  </tbody>
</table>

<h2>Configuração segura para primeiro teste em PLA</h2>
<p>Para validar um STL decorativo, comece simples: camada 0,20 mm, 2 ou 3 paredes, 10% a 15% de preenchimento, velocidade moderada e suporte em arvore quando fizer sentido. Para detalhes finos, reduza para 0,16 mm ou 0,12 mm depois que o modelo for aprovado.</p>
<p>Em articulados, ajuste fluxo e primeira camada com cuidado. Se a primeira camada ficar esmagada demais, juntas print-in-place podem sair grudadas. Se ficar alta demais, a peca pode soltar da mesa.</p>

<h2>Conclusao</h2>
<p>Saber <strong>como escolher STL gratis</strong> e tao importante quanto saber onde baixar. Um bom arquivo economiza filamento, reduz falhas e deixa a impressao 3D mais divertida. Antes de imprimir, olhe foto real, comentarios, escala, suportes, paredes e licenca.</p>
<p>Se o modelo passar no checklist, faca um teste pequeno com PLA de bom custo-beneficio. Depois disso, vale investir tempo, acabamento e filamento melhor na versao final.</p>

<h2>Perguntas frequentes</h2>

<h3>Todo STL gratis e seguro para imprimir?</h3>
<p>Nao. Muitos arquivos gratis sao excelentes, mas outros nao foram testados, tem parede fina, escala errada ou exigem suporte demais. Sempre confira no slicer antes de imprimir.</p>

<h3>Qual filamento usar para testar STL gratis?</h3>
<p>PLA e o melhor ponto de partida para a maioria dos testes porque e facil de imprimir, barato e suficiente para validar escala, suporte e detalhes. Guarde filamentos especiais para a versao final.</p>

<h3>Como saber se o STL precisa de suporte?</h3>
<p>Abra no slicer e veja a pre-visualizacao. Areas no ar, angulos fortes e partes horizontais longas geralmente precisam de suporte. Se o suporte domina a peca, talvez exista uma orientacao melhor.</p>

<h3>Posso vender uma peca feita com STL gratis?</h3>
<p>Depende da licenca do arquivo. Alguns modelos permitem uso comercial, outros apenas uso pessoal. Leia a licenca antes de vender em marketplace, grupo ou encomenda.</p>

<h3>STL ou 3MF: qual escolher?</h3>
<p>STL funciona em quase qualquer slicer. 3MF pode ser melhor quando vem com orientacao, pecas organizadas e perfil de impressao. Para iniciantes, 3MF bem preparado pode reduzir erros.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Todo STL gratis e seguro para imprimir?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Nao. Muitos arquivos gratis sao excelentes, mas outros nao foram testados, tem parede fina, escala errada ou exigem suporte demais. Sempre confira no slicer antes de imprimir."}}
    }},
    {{
      "@type": "Question",
      "name": "Qual filamento usar para testar STL gratis?",
      "acceptedAnswer": {{"@type": "Answer", "text": "PLA e o melhor ponto de partida para a maioria dos testes porque e facil de imprimir, barato e suficiente para validar escala, suporte e detalhes. Guarde filamentos especiais para a versao final."}}
    }},
    {{
      "@type": "Question",
      "name": "Como saber se o STL precisa de suporte?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Abra no slicer e veja a pre-visualizacao. Areas no ar, angulos fortes e partes horizontais longas geralmente precisam de suporte. Se o suporte domina a peca, talvez exista uma orientacao melhor."}}
    }},
    {{
      "@type": "Question",
      "name": "Posso vender uma peca feita com STL gratis?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Depende da licenca do arquivo. Alguns modelos permitem uso comercial, outros apenas uso pessoal. Leia a licenca antes de vender em marketplace, grupo ou encomenda."}}
    }},
    {{
      "@type": "Question",
      "name": "STL ou 3MF: qual escolher?",
      "acceptedAnswer": {{"@type": "Answer", "text": "STL funciona em quase qualquer slicer. 3MF pode ser melhor quando vem com orientacao, pecas organizadas e perfil de impressao. Para iniciantes, 3MF bem preparado pode reduzir erros."}}
    }}
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

    product_id, product_url = publisher.upload_media(
        str(AFFILIATE_IMAGE),
        alt_text="PLA Voolt Outlet para testar STL gratis em impressao 3D",
    )
    if not product_url:
        raise SystemExit("Falha ao enviar imagem do afiliado.")

    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": build_content(product_url),
        "excerpt": "Checklist para escolher STL gratis sem desperdiçar filamento: foto real, comentarios, escala, suporte, paredes e teste barato em PLA.",
        "status": "draft",
        "tags": ["STL gratis", "filamento PLA", "Voolt3D", "impressao 3D", "slicer", "modelos 3D", "iniciantes"],
        "categories": ["STL, Modelos e Personagens"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Como Escolher STL Gratis Sem Desperdicar Filamento",
        "yoast_meta": "Checklist para escolher STL gratis sem desperdiçar filamento: veja foto real, comentarios, escala, suportes, paredes e teste barato em PLA.",
    }

    result = publisher.publicar_post(post, skip_if_exists=True)
    print(json.dumps({"capa": str(capa), "produto_media_id": product_id, "post": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
