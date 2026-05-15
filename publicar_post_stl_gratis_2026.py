"""
Publica como rascunho o post pilar:
"Melhores Sites para Baixar STL Gratis em 2026".

Este arquivo nao chama APIs externas de conteudo. O texto foi preparado no chat
e o script apenas cria a capa local e envia o rascunho para o WordPress.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from publisher import WordPressPublisher


TITLE = "Melhores Sites para Baixar STL Gratis em 2026: Guia para Makers Brasileiros"
SLUG = "melhores-sites-baixar-stl-gratis-2026"
KEYPHRASE = "baixar STL gratis"
CAPA_PATH = Path("downloads/capas/melhores-sites-stl-gratis-2026.jpg")


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
    CAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 675
    bg = Image.new("RGB", (w, h), (6, 8, 15))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Fundo tecnico com grade e "cards" de arquivos STL.
    for x in range(0, w, 48):
        draw.line((x, 0, x, h), fill=(24, 35, 52, 115), width=1)
    for y in range(0, h, 48):
        draw.line((0, y, w, y), fill=(24, 35, 52, 115), width=1)
    draw.rounded_rectangle((650, 72, 1110, 560), radius=22, fill=(12, 18, 30, 235), outline=(0, 210, 255, 190), width=3)
    for i, label in enumerate(["Printables", "MakerWorld", "Thingiverse", "Cults", "Thangs"]):
        y = 118 + i * 78
        color = (0, 210, 255, 255) if i % 2 == 0 else (84, 230, 66, 255)
        draw.rounded_rectangle((690, y, 1070, y + 48), radius=12, fill=(18, 25, 40, 255), outline=color, width=2)
        draw.text((720, y + 11), f"{label}  STL", font=font(24, True), fill=(238, 246, 255, 255))
        draw.ellipse((1028, y + 16, 1044, y + 32), fill=color)

    draw.polygon([(785, 430), (905, 350), (1032, 438), (910, 528)], fill=(84, 230, 66, 90), outline=(84, 230, 66, 220))
    draw.line((905, 350, 910, 528), fill=(84, 230, 66, 190), width=3)
    draw.line((785, 430, 1032, 438), fill=(84, 230, 66, 190), width=3)
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).filter(ImageFilter.GaussianBlur(0.2)).convert("RGBA")

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((0, 0, 640, h), fill=(0, 0, 0, 132))
    draw.rounded_rectangle((58, 56, 344, 106), radius=12, fill=(255, 106, 19, 245))
    draw.text((78, 68), "GUIA GRATUITO 2026", font=font(25, True), fill=(0, 0, 0, 255))

    y = 142
    for line in wrap(draw, "Onde baixar STL gratis sem cair em arquivo ruim", font(64, True), 560)[:4]:
        draw.text((58, y), line, font=font(64, True), fill=(255, 255, 255, 255))
        y += 70
    draw.text((60, y + 18), "Sites confiaveis, licencas e dicas para imprimir melhor", font=font(29, True), fill=(84, 230, 66, 255))

    chip_y = 540
    for chip in ["STL gratis", "Maker Brasil", "Baixo custo"]:
        box = draw.textbbox((0, 0), chip, font=font(23, True))
        chip_w = box[2] - box[0] + 34
        draw.rounded_rectangle((58, chip_y, 58 + chip_w, chip_y + 42), radius=20, fill=(8, 18, 32, 240), outline=(0, 210, 255, 180), width=2)
        draw.text((75, chip_y + 8), chip, font=font(23, True), fill=(235, 244, 255, 255))
        chip_y += 0
        x_next = 58 + chip_w + 14
        draw = ImageDraw.Draw(layer)
        # Reposicionamento simples horizontal.
        if chip == "STL gratis":
            draw.rounded_rectangle((x_next, chip_y, x_next + 162, chip_y + 42), radius=20, fill=(8, 18, 32, 240), outline=(0, 210, 255, 180), width=2)
            draw.text((x_next + 17, chip_y + 8), "Maker Brasil", font=font(23, True), fill=(235, 244, 255, 255))
            draw.rounded_rectangle((x_next + 178, chip_y, x_next + 346, chip_y + 42), radius=20, fill=(8, 18, 32, 240), outline=(0, 210, 255, 180), width=2)
            draw.text((x_next + 195, chip_y + 8), "Baixo custo", font=font(23, True), fill=(235, 244, 255, 255))
            break

    draw.text((58, 625), "Clube 3D Brasil", font=font(24, False), fill=(218, 230, 245, 230))
    final = Image.alpha_composite(bg, layer).convert("RGB")
    final.save(CAPA_PATH, quality=92, optimize=True)
    return CAPA_PATH


CONTENT = r"""
<p>Se voce procura <strong>baixar STL gratis</strong> para imprimir em casa, a melhor estrategia em 2026 nao e sair clicando em qualquer arquivo bonito. O caminho mais seguro e escolher plataformas com fotos de impressoes reais, comentarios de makers, licenca clara e modelos que ja foram testados por outras pessoas.</p>

<p>Este guia foi feito para o maker brasileiro que quer economizar filamento, encontrar arquivos bons e participar de comunidades onde aparecem achados, testes e modelos baratos. A ideia e simples: baixar menos arquivo ruim, imprimir mais coisa que funciona e gastar melhor.</p>

<div style="border:2px solid #22c55e;background:#07140c;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#22c55e;font-weight:800;text-transform:uppercase;">Atalho do Clube 3D Brasil</p>
  <p style="margin:0;color:#d8ffe5;">Antes de baixar qualquer STL, salve este checklist: foto real impressa, comentarios recentes, licenca permitida, orientacao de suporte e configuracao sugerida pelo criador.</p>
</div>

<h2>1. Printables: o melhor equilibrio para iniciantes</h2>
<p>O <a href="https://www.printables.com/" target="_blank" rel="noopener noreferrer">Printables</a> costuma ser uma das melhores portas de entrada porque a comunidade publica muitas fotos reais, remixes e comentarios tecnicos. Para quem esta comecando, isso reduz bastante a chance de baixar um arquivo bonito na tela, mas ruim na impressora.</p>
<p>Use o Printables para procurar modelos funcionais, brinquedos, suportes, organizadores, pecas para casa e projetos com configuracao detalhada. Quando houver varias versoes do mesmo modelo, priorize a que tem fotos de impressao, avaliacao recente e respostas do criador.</p>

<h2>2. MakerWorld: otimo para quem usa Bambu Lab ou quer perfil pronto</h2>
<p>A <a href="https://makerworld.com/" target="_blank" rel="noopener noreferrer">MakerWorld</a> cresceu muito porque facilita a vida de quem usa Bambu Studio e impressoras Bambu Lab. Mesmo quem nao tem Bambu pode aproveitar muitos STL e 3MF, mas o grande diferencial esta nos perfis prontos e na integracao com o fluxo de impressao.</p>
<p>Para o publico brasileiro, ela e forte em modelos rapidos, decoracao, brinquedos articulados e pecas que ja chegam com orientacao pratica. Se voce tem A1 Mini, A1, P1S ou X1, vale conferir primeiro se existe perfil validado antes de fatiar tudo manualmente.</p>

<h2>3. Thingiverse: biblioteca gigante, mas precisa filtrar bem</h2>
<p>O <a href="https://www.thingiverse.com/" target="_blank" rel="noopener noreferrer">Thingiverse</a> continua importante por ter uma biblioteca historica enorme. Ele e muito bom para achar modelos classicos, pecas antigas, suportes, upgrades e objetos que ja foram remixados por varios anos.</p>
<p>O cuidado aqui e filtrar. Veja a data, os comentarios, as fotos de usuarios e se o arquivo ainda faz sentido para impressoras atuais. Muitos modelos funcionam perfeitamente, mas alguns foram criados para maquinas antigas e podem exigir ajuste no slicer.</p>

<h2>4. Thangs: bom para pesquisar o mesmo modelo em varias fontes</h2>
<p>O <a href="https://thangs.com/" target="_blank" rel="noopener noreferrer">Thangs</a> funciona muito bem como buscador e biblioteca de modelos 3D. Ele ajuda quando voce sabe o que quer, por exemplo "suporte headset", "flexi dragon" ou "organizador de mesa", mas ainda nao sabe qual plataforma tem a melhor versao.</p>
<p>Use o Thangs para comparar resultados, encontrar modelos parecidos e descobrir criadores. Depois, antes de baixar, confira sempre a pagina original, licenca e comentarios.</p>

<h2>5. Cults: bons modelos gratuitos e pagos, com atencao a licenca</h2>
<p>O <a href="https://cults3d.com/" target="_blank" rel="noopener noreferrer">Cults</a> mistura arquivos gratuitos e pagos. Ele e forte em decoracao, personagens, miniaturas, cosplay, colecionaveis e modelos com acabamento visual mais chamativo.</p>
<p>Para quem quer vender impressao 3D, leia a licenca com cuidado. Nem todo arquivo gratuito permite venda da peca impressa. Alguns permitem uso pessoal, outros exigem licenca comercial. Essa diferenca evita dor de cabeca quando voce comecar a anunciar na Shopee, Elo7 ou grupos.</p>

<h2>6. MyMiniFactory: bom para miniaturas e modelos mais curados</h2>
<p>A <a href="https://www.myminifactory.com/" target="_blank" rel="noopener noreferrer">MyMiniFactory</a> e interessante para miniaturas, RPG, figuras, estatuas e projetos com visual mais profissional. Ela tem muitos arquivos pagos, mas tambem aparecem modelos gratuitos de qualidade.</p>
<p>Se voce imprime miniaturas, bustos ou pecas decorativas, vale acompanhar criadores especificos. A vantagem e que muitos projetos ja nascem pensando em impressao real, suporte e acabamento.</p>

<h2>7. Fab365: quando o foco e articulado, dobravel e print-in-place</h2>
<p>Modelos articulados, dobraveis e "print-in-place" seguem fortes em 2026 porque chamam atencao em video curto e sao otimos para presentear. A <a href="https://fab365.net/" target="_blank" rel="noopener noreferrer">Fab365</a> e uma referencia nesse tipo de arquivo, especialmente para quem gosta de modelos que saem da mesa ja com movimento.</p>
<p>O ponto de atencao e calibracao. Articulados exigem boa primeira camada, fluxo correto e retracao bem ajustada. Se a sua impressora estiver descalibrada, o modelo pode sair grudado ou com articulacao dura.</p>

<h2>Como escolher um STL gratis sem desperdiçar filamento</h2>
<p>O erro mais comum e baixar pelo render bonito. Render nao prova que o arquivo imprime bem. Antes de colocar na maquina, procure sinais de confianca:</p>

<ul>
  <li>fotos reais enviadas por usuarios;</li>
  <li>comentarios recentes confirmando que imprimiu;</li>
  <li>orientacao de suporte, escala e material;</li>
  <li>licenca clara para uso pessoal ou comercial;</li>
  <li>arquivo atualizado ou remix bem explicado;</li>
  <li>modelo com base plana, paredes viaveis e detalhes nao exageradamente finos.</li>
</ul>

<h2>Qual site usar primeiro?</h2>
<table style="width:100%;border-collapse:collapse;margin:22px 0;">
  <thead>
    <tr>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Objetivo</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Melhor ponto de partida</th>
      <th style="border:1px solid #ddd;padding:10px;text-align:left;">Por que usar</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="border:1px solid #ddd;padding:10px;">Comecar sem erro</td><td style="border:1px solid #ddd;padding:10px;">Printables</td><td style="border:1px solid #ddd;padding:10px;">Comunidade forte, fotos reais e comentarios uteis.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Usar Bambu Studio</td><td style="border:1px solid #ddd;padding:10px;">MakerWorld</td><td style="border:1px solid #ddd;padding:10px;">Perfis prontos e fluxo rapido para Bambu Lab.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Achar modelo classico</td><td style="border:1px solid #ddd;padding:10px;">Thingiverse</td><td style="border:1px solid #ddd;padding:10px;">Biblioteca enorme e muitos remixes antigos.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Pesquisar varias fontes</td><td style="border:1px solid #ddd;padding:10px;">Thangs</td><td style="border:1px solid #ddd;padding:10px;">Bom buscador para comparar modelos semelhantes.</td></tr>
    <tr><td style="border:1px solid #ddd;padding:10px;">Miniaturas e decoracao</td><td style="border:1px solid #ddd;padding:10px;">Cults ou MyMiniFactory</td><td style="border:1px solid #ddd;padding:10px;">Modelos visuais, colecionaveis e projetos mais autorais.</td></tr>
  </tbody>
</table>

<h2>Configuracao segura para testar um STL novo</h2>
<p>Quando o arquivo e novo para voce, nao comece imprimindo gigante. Faca um teste menor, com menos material e tempo reduzido. Para PLA, uma base segura costuma ser: camada de 0,20 mm para teste, 15% de preenchimento, 2 a 3 paredes, velocidade moderada e suporte em arvore quando houver muitos balancos.</p>
<p>Depois que o modelo provar que funciona, aumente a qualidade para 0,16 mm ou 0,12 mm se houver detalhes finos. Em figuras, isso melhora rosto, textura, cabelo, armadura e pequenas curvas. Em pecas funcionais, priorize dimensao e resistencia antes de acabamento visual.</p>

<h2>Oportunidade para grupos: por que baixar junto e melhor</h2>
<p>O publico brasileiro gosta de arquivo gratuito ou barato, mas tambem quer saber se aquilo funciona antes de gastar horas de maquina. Por isso os grupos ajudam tanto: um maker testa, outro mostra configuracao, outro alerta sobre suporte ruim e todo mundo economiza filamento.</p>
<p>No Clube 3D Brasil, a ideia e usar os grupos para compartilhar STL gratis, achar arquivos pagos baratos, fazer vaquinhas quando um modelo premium vale teste e publicar resultado real. Esse formato transforma o blog em hub, nao apenas em lista de links.</p>

<div style="border:2px solid #0ea5e9;background:#06131f;padding:16px 18px;margin:28px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#67e8f9;font-weight:800;">Dica pratica</p>
  <p style="margin:0;color:#dff7ff;">Se voce encontrou um STL interessante, envie no grupo antes de imprimir. A comunidade pode avisar se precisa suporte, se a escala esta errada ou se existe uma versao melhor.</p>
</div>

<h2>Links internos para continuar</h2>
<p>Se voce esta comecando agora, leia tambem o guia de <a href="https://clube3dbrasil.com/melhor-pla-para-iniciantes/">melhor PLA para iniciantes</a>. Para quem quer transformar impressao em renda, o proximo passo e separar modelos com boa demanda, calcular custo de filamento e testar acabamento antes de vender.</p>

<h2>Conclusao</h2>
<p>Para <strong>baixar STL gratis</strong> em 2026, os melhores resultados aparecem quando voce combina boas plataformas com criterio. Printables, MakerWorld, Thingiverse, Thangs, Cults, MyMiniFactory e Fab365 podem render modelos excelentes, mas nenhum substitui uma checagem basica antes de imprimir.</p>
<p>Comece pelos arquivos com prova real, teste em escala menor, participe dos grupos e registre suas configuracoes. Assim voce imprime mais, erra menos e transforma cada download em aprendizado para a comunidade.</p>

<h2>Perguntas frequentes sobre baixar STL gratis</h2>

<h3>Qual e o melhor site para baixar STL gratis?</h3>
<p>Para iniciantes, o Printables costuma ser o melhor ponto de partida porque tem comunidade ativa, fotos reais e muitos comentarios de impressao. MakerWorld e excelente para quem usa Bambu Lab, enquanto Thingiverse ainda e forte para modelos classicos.</p>

<h3>Posso vender uma peca impressa de um STL gratis?</h3>
<p>Depende da licenca. Alguns modelos gratuitos permitem apenas uso pessoal. Outros permitem venda da peca impressa, as vezes com atribuicao ao criador. Sempre leia a licenca antes de anunciar.</p>

<h3>STL gratis imprime pior que STL pago?</h3>
<p>Nao necessariamente. Existem STLs gratuitos excelentes e arquivos pagos ruins. O que importa e a qualidade do design, fotos reais, comentarios, suporte do criador e compatibilidade com sua impressora.</p>

<h3>Qual formato e melhor: STL ou 3MF?</h3>
<p>STL e universal e funciona em praticamente qualquer slicer. 3MF pode guardar mais informacoes, como orientacao, perfis e organizacao de pecas. Quando houver 3MF bem preparado, ele pode facilitar a vida.</p>

<h3>Como saber se um modelo articulado vai funcionar?</h3>
<p>Procure fotos reais, comentarios recentes e recomendacao de tolerancia. Antes de imprimir grande, faca um teste pequeno. Modelos articulados exigem boa calibracao de fluxo, primeira camada e retracao.</p>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Qual e o melhor site para baixar STL gratis?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Para iniciantes, o Printables costuma ser o melhor ponto de partida porque tem comunidade ativa, fotos reais e muitos comentarios de impressao. MakerWorld e excelente para quem usa Bambu Lab, enquanto Thingiverse ainda e forte para modelos classicos."
      }
    },
    {
      "@type": "Question",
      "name": "Posso vender uma peca impressa de um STL gratis?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Depende da licenca. Alguns modelos gratuitos permitem apenas uso pessoal. Outros permitem venda da peca impressa, as vezes com atribuicao ao criador. Sempre leia a licenca antes de anunciar."
      }
    },
    {
      "@type": "Question",
      "name": "STL gratis imprime pior que STL pago?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Nao necessariamente. Existem STLs gratuitos excelentes e arquivos pagos ruins. O que importa e a qualidade do design, fotos reais, comentarios, suporte do criador e compatibilidade com sua impressora."
      }
    },
    {
      "@type": "Question",
      "name": "Qual formato e melhor: STL ou 3MF?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "STL e universal e funciona em praticamente qualquer slicer. 3MF pode guardar mais informacoes, como orientacao, perfis e organizacao de pecas. Quando houver 3MF bem preparado, ele pode facilitar a vida."
      }
    },
    {
      "@type": "Question",
      "name": "Como saber se um modelo articulado vai funcionar?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Procure fotos reais, comentarios recentes e recomendacao de tolerancia. Antes de imprimir grande, faca um teste pequeno. Modelos articulados exigem boa calibracao de fluxo, primeira camada e retracao."
      }
    }
  ]
}
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
    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": CONTENT,
        "excerpt": "Veja os melhores sites para baixar STL gratis em 2026, com dicas para evitar arquivo ruim, economizar filamento e encontrar modelos testados.",
        "status": "draft",
        "tags": ["STL gratis", "baixar STL", "modelos 3D", "Printables", "MakerWorld", "Thingiverse", "impressao 3D"],
        "categories": ["STL, Modelos e Personagens"],
        "featured_image_path": str(capa),
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Baixar STL Gratis: Melhores Sites 2026 | Clube 3D Brasil",
        "yoast_meta": "Veja onde baixar STL gratis em 2026 com seguranca: Printables, MakerWorld, Thingiverse, Cults e dicas para evitar arquivo ruim.",
    }

    publisher = WordPressPublisher(config)
    if not publisher.testar_conexao():
        raise SystemExit("Falha na conexao WordPress.")
    result = publisher.publicar_post(post, skip_if_exists=True)
    print(json.dumps({"capa": str(capa), "post": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
