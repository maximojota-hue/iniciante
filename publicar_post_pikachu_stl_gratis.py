"""
Publica como rascunho o post de personagem 3D:
"Pokemon Pikachu STL Gratis para Impressao 3D".

Origem: pacote leve CRIAR_POST_PERSONAGEM_3D_COM_PASTA.
Nao usa API externa de conteudo; apenas envia o rascunho ao WordPress.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

from publisher import WordPressPublisher


TITLE = "Pokemon Pikachu STL Gratis: Modelo 3D para Imprimir"
SLUG = "pokemon-pikachu-stl-gratis-impressao-3d"
KEYPHRASE = "Pokemon Pikachu STL gratis"
CATEGORY = "Games & Personagens"
DOWNLOAD_URL = "https://makerworld.com/pt/models/1701940-pokemon-pikachu?from=search#profileId-1804955"
DOWNLOAD_LABEL = "Pokemon Pikachu - Modelo gratuito para impressao 3D - MakerWorld"

IMAGES = [
    r"C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\posts\pagina\pokemon\Nova pasta\download (2).jpg",
    r"C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\posts\pagina\pokemon\Nova pasta\20250815_084456.jpg",
]


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def config_wp() -> dict:
    return {
        "wp_url": os.environ.get("WP_URL", "https://clube3dbrasil.com"),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_PASS", ""),
        "telegram_notify_statuses": os.environ.get("TELEGRAM_NOTIFY_STATUSES", "publish"),
    }


def validar_imagens() -> None:
    for image in IMAGES:
        if not Path(image).exists():
            raise SystemExit(f"Imagem nao encontrada: {image}")


def preparar_imagens() -> list[str]:
    out_dir = Path("downloads/personagens")
    out_dir.mkdir(parents=True, exist_ok=True)
    prepared: list[str] = []
    for idx, image in enumerate(IMAGES, 1):
        src = Path(image)
        out = out_dir / f"pikachu-stl-gratis-{idx}.jpg"
        img = Image.open(src).convert("RGB")
        img.thumbnail((1400, 1000))
        img.save(out, quality=84, optimize=True)
        prepared.append(str(out))
    return prepared


def download_cta() -> str:
    return f"""
<div style="border:2px solid #ff6a13;background:#100904;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Baixar modelo 3D</p>
  <p style="margin:0 0 14px;color:#fff4e8;">Acesse a pagina original do criador para baixar o arquivo, conferir perfil de impressao, comentarios e eventuais atualizacoes do modelo.</p>
  <p style="margin:0;">
    <a href="{DOWNLOAD_URL}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#ff6a13;color:#111;padding:12px 18px;border-radius:6px;font-weight:800;text-decoration:none;">
      Abrir pagina de download do Pikachu
    </a>
  </p>
  <p style="margin:12px 0 0;color:#cbd5e1;font-size:14px;">Fonte: {DOWNLOAD_LABEL}</p>
</div>
"""


CONTENT = f"""
<p>O <strong>Pokemon Pikachu STL gratis</strong> e um daqueles modelos que chamam atencao rapidamente porque mistura personagem conhecido, formato simples de reconhecer e bom potencial para decorar setup gamer, quarto infantil, mesa de trabalho ou prateleira de colecionaveis.</p>

<p>Este post e para quem quer imprimir o Pikachu sem complicar demais: como analisar o modelo antes de baixar, quais cuidados ter no fatiador, que filamento usar e quando vale reduzir ou aumentar a escala para nao desperdiçar material.</p>

<!--IMAGEM_1-->

<h2>Por que esse Pikachu e uma boa escolha para o primeiro personagem 3D?</h2>
<p>Personagens muito detalhados podem ser bonitos no render, mas nem sempre sao amigaveis para quem ainda esta calibrando a impressora. O Pikachu costuma ser uma opcao melhor porque tem silhueta facil de reconhecer, cores simples e visual forte mesmo em tamanho pequeno.</p>

<p>Para o publico brasileiro, esse tipo de modelo tambem funciona bem como teste de acabamento. Voce consegue avaliar primeira camada, linhas curvas, pequenas pontas, encaixe visual das partes e qualidade da pintura ou troca de cor sem gastar tanto quanto gastaria em uma estatua grande.</p>

<h2>Antes de baixar: confira estes pontos</h2>
<p>Mesmo sendo um modelo gratuito, vale checar alguns detalhes na pagina original antes de mandar para o slicer:</p>

<ul>
  <li>se existe foto real impressa ou apenas render;</li>
  <li>se o criador publicou perfil de impressao ou configuracao sugerida;</li>
  <li>se outros usuarios comentaram problemas de suporte, escala ou aderencia;</li>
  <li>se o arquivo tem versao em STL, 3MF ou perfil pronto;</li>
  <li>qual e a licenca de uso do modelo.</li>
</ul>

<h2>Material recomendado para imprimir o Pikachu</h2>
<p>Para a maioria dos makers, o melhor caminho e usar <strong>PLA</strong>. Ele e facil de imprimir, tem boa variedade de cores e costuma entregar acabamento bonito em personagem decorativo.</p>

<p>Se voce tiver filamento amarelo, preto e vermelho, pode imprimir por partes ou fazer pintura manual depois. Se tiver AMS ou sistema multicolor, o resultado pode ficar mais limpo, mas nao e obrigatorio para criar uma peca bonita.</p>

<!--IMAGEM_2-->

<h2>Configuracao inicial segura no slicer</h2>
<p>Como ponto de partida, use uma configuracao simples e conservadora. Para uma impressora FDM bem calibrada, uma base segura seria:</p>

<ul>
  <li>altura de camada: 0,16 mm ou 0,20 mm;</li>
  <li>preenchimento: 10% a 15% para peca decorativa;</li>
  <li>paredes: 2 ou 3 perimetros;</li>
  <li>suporte: ativar apenas se houver areas suspensas no modelo;</li>
  <li>velocidade: moderada para preservar curvas e detalhes;</li>
  <li>material: PLA comum ou PLA de melhor acabamento.</li>
</ul>

<p>Se a sua impressora ainda nao esta perfeitamente calibrada, imprima primeiro em escala menor. Isso ajuda a testar suporte, aderencia e acabamento antes de gastar mais filamento em uma versao grande.</p>

<h2>Escala: pequeno para teste, medio para presente</h2>
<p>O Pikachu funciona bem em tamanhos diferentes. Em escala pequena, ele vira um teste rapido de detalhe e acabamento. Em tamanho medio, pode virar item de decoracao, presente ou peca para montar um conjunto de personagens Pokemon.</p>

<p>Evite aumentar demais logo na primeira tentativa. Modelos de personagem podem aparentar ser simples, mas qualquer erro de suporte ou retracao aparece mais quando a peca cresce.</p>

<h2>Cuidados com licenca e uso comercial</h2>
<p>Como o Pikachu e um personagem de uma marca conhecida, tenha cuidado com uso comercial. Baixar e imprimir para uso pessoal e uma coisa; vender pecas de personagem famoso pode envolver risco de marca e direitos autorais.</p>

<p>Para o Clube 3D Brasil, o caminho mais seguro e tratar esse tipo de arquivo como conteudo de aprendizado, teste de impressao e inspiracao para comunidade. Para venda, prefira modelos autorais, arquivos com licenca comercial clara ou projetos proprios.</p>

<h2>Checklist rapido antes de imprimir</h2>
<ul>
  <li>baixe sempre pela pagina original do modelo;</li>
  <li>confira comentarios e atualizacoes do criador;</li>
  <li>teste uma escala menor antes da versao final;</li>
  <li>use PLA se quiser facilidade e baixo custo;</li>
  <li>registre temperatura, velocidade e suporte que funcionaram;</li>
  <li>compartilhe o resultado no grupo para ajudar outros makers.</li>
</ul>

<h2>Vale a pena baixar esse Pikachu?</h2>
<p>Sim, principalmente se voce quer um personagem conhecido para testar acabamento, cores e configuracao de suporte. Ele tambem e uma boa peca para criar conteudo visual, comparar filamentos e montar uma colecao geek impressa em 3D.</p>

<p>A recomendacao e baixar pela pagina original, conferir se existe perfil atualizado e fazer um primeiro teste com pouca escala. Depois, se o resultado ficar bom, vale imprimir maior e caprichar no acabamento.</p>

{download_cta()}

<h2>Perguntas frequentes sobre o Pikachu STL gratis</h2>

<h3>Esse modelo do Pikachu e bom para iniciantes?</h3>
<p>Sim. Ele e um bom modelo para iniciantes porque tem visual reconhecivel, nao exige acabamento extremamente tecnico e permite testar cor, suporte e qualidade de camada.</p>

<h3>Qual filamento usar para imprimir Pikachu?</h3>
<p>PLA e a melhor escolha para a maioria dos casos. Ele imprime facil, tem bom acabamento e existe em cores ideais para personagem, como amarelo, preto, vermelho e branco.</p>

<h3>Posso vender o Pikachu impresso?</h3>
<p>Tenha cuidado. Pikachu e personagem de marca conhecida. Para uso comercial, verifique licenca, direitos de marca e prefira modelos com permissao comercial clara.</p>

<h3>Precisa de suporte para imprimir?</h3>
<p>Depende da orientacao e da versao do arquivo. Antes de imprimir, abra no slicer e confira areas suspensas. Se precisar, use suporte em arvore ou suporte organico para facilitar a remocao.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Esse modelo do Pikachu e bom para iniciantes?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Sim. Ele e um bom modelo para iniciantes porque tem visual reconhecivel, nao exige acabamento extremamente tecnico e permite testar cor, suporte e qualidade de camada."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Qual filamento usar para imprimir Pikachu?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "PLA e a melhor escolha para a maioria dos casos. Ele imprime facil, tem bom acabamento e existe em cores ideais para personagem, como amarelo, preto, vermelho e branco."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Posso vender o Pikachu impresso?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Tenha cuidado. Pikachu e personagem de marca conhecida. Para uso comercial, verifique licenca, direitos de marca e prefira modelos com permissao comercial clara."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Precisa de suporte para imprimir?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Depende da orientacao e da versao do arquivo. Antes de imprimir, abra no slicer e confira areas suspensas. Se precisar, use suporte em arvore ou suporte organico para facilitar a remocao."
      }}
    }}
  ]
}}
</script>
"""


def atualizar_controle(result: dict) -> None:
    path = Path("CONTROLE_POSTS.md")
    text = path.read_text(encoding="utf-8")
    row = (
        f"| 9 | {TITLE} | `{SLUG}` | {result['wp_id']} | rascunho | nao enviado | "
        "sem afiliado | Post de personagem 3D criado pelo fluxo `CRIAR_POST_PERSONAGEM_3D_COM_PASTA`, "
        "com fotos locais e CTA final para download no MakerWorld. |\n"
    )
    if f"| 9 | {TITLE} |" in text or f"`{SLUG}`" in text:
        return
    marker = "\n## Regra Para Novos Posts\n"
    text = text.replace(marker, row + marker)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    carregar_env()
    validar_imagens()
    imagens_post = preparar_imagens()
    pub = WordPressPublisher(config_wp())
    post = {
        "titulo": TITLE,
        "slug": SLUG,
        "content": CONTENT,
        "excerpt": (
            "Baixe o modelo 3D gratuito do Pokemon Pikachu e veja dicas de material, "
            "escala, suporte e cuidados antes de imprimir."
        ),
        "status": "draft",
        "categories": [CATEGORY],
        "tags": ["Pokemon", "Pikachu", "STL gratis", "impressao 3D", "MakerWorld"],
        "yoast_keyphrase": KEYPHRASE,
        "yoast_title": "Pokemon Pikachu STL Gratis para Impressao 3D",
        "yoast_meta": (
            "Veja o Pokemon Pikachu STL gratis para imprimir em 3D, com dicas de PLA, "
            "escala, suporte e link para baixar no MakerWorld."
        ),
        "imagens_lista": imagens_post,
    }
    result = pub.publicar_post(post, skip_if_exists=True)
    if not result:
        raise SystemExit("WordPress nao retornou resultado.")
    atualizar_controle(result)
    print(result)


if __name__ == "__main__":
    main()
