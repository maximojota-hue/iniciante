"""
Publica rascunhos em lote para personagens Pokemon 3D.

Origem: pacote leve CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS.
Nao usa API externa de conteudo; apenas gera HTML local e envia ao WordPress.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

from PIL import Image

from preparador_pacote_personagem import build_package, scan_batch
from publisher import WordPressPublisher


ROOT_FOLDER = Path(r"C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\posts\pagina\pokemon")
CATEGORY = "Games & Personagens"
CONTROL_PATH = Path("CONTROLE_POSTS.md")


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
        "wp_timeout": 75,
        "telegram_notify_statuses": os.environ.get("TELEGRAM_NOTIFY_STATUSES", "publish"),
    }


def ascii_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return normalized.encode("ascii", "ignore").decode("ascii")


def slugify(text: str) -> str:
    text = ascii_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def display_name(keyword: str) -> str:
    cleaned = re.sub(r"\s+", " ", keyword or "").strip()
    replacements = {
        "Pokémon Inteligente Wooper, multicolorido em peças separadas (SEM AMS) e múltiplas versões integrada mu": "Wooper Multicolor Sem AMS",
        "Pokemon Pikachu Poly": "Pikachu Poly",
        "Pokémon Eevee": "Eevee",
    }
    return replacements.get(cleaned, cleaned.replace("Pokémon ", "").replace("Pokemon ", ""))


def title_for(name: str) -> str:
    return f"{name} STL Gratis: Modelo Pokemon para Imprimir em 3D"


def keyphrase_for(name: str) -> str:
    return f"{name} STL gratis"


def next_post_number() -> int:
    text = CONTROL_PATH.read_text(encoding="utf-8")
    numbers = []
    for line in text.splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|", line)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers or [0]) + 1


def controle_has_slug(slug: str) -> bool:
    return f"`{slug}`" in CONTROL_PATH.read_text(encoding="utf-8")


def preparar_imagens(pacote: dict, slug: str) -> list[str]:
    out_dir = Path("downloads/personagens") / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    prepared: list[str] = []
    for idx, image in enumerate(pacote["midia"].get("imagens_disponiveis", [])[:2], 1):
        src = Path(image)
        if not src.exists():
            continue
        out = out_dir / f"{slug}-{idx}.jpg"
        img = Image.open(src).convert("RGB")
        img.thumbnail((1400, 1000))
        img.save(out, quality=84, optimize=True)
        prepared.append(str(out))
    return prepared


def download_cta(name: str, url: str, label: str) -> str:
    return f"""
<div style="border:2px solid #ff6a13;background:#100904;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Baixar modelo 3D</p>
  <p style="margin:0 0 14px;color:#fff4e8;">Acesse a pagina original do criador para baixar o arquivo do {name}, conferir perfil de impressao, comentarios e atualizacoes.</p>
  <p style="margin:0;">
    <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#ff6a13;color:#111;padding:12px 18px;border-radius:6px;font-weight:800;text-decoration:none;">
      Abrir pagina de download do {name}
    </a>
  </p>
  <p style="margin:12px 0 0;color:#cbd5e1;font-size:14px;">Fonte: {label}</p>
</div>
"""


def content_for(name: str, pacote: dict) -> str:
    keyphrase = keyphrase_for(name)
    url = pacote["fonte"]["download_url"]
    label = pacote["fonte"]["download_label"]
    return f"""
<p>O <strong>{keyphrase}</strong> e uma boa escolha para quem quer montar uma colecao geek impressa em 3D sem comecar por um arquivo complicado demais. O modelo tem apelo visual imediato, combina com setups gamers e ajuda a testar acabamento, cor e calibracao da impressora.</p>

<p>Este guia mostra como analisar o arquivo antes de baixar, quais configuracoes usar no slicer e quando vale imprimir pequeno para teste antes de fazer uma versao maior.</p>

<!--IMAGEM_1-->

<h2>Por que imprimir o {name}?</h2>
<p>Modelos Pokemon funcionam muito bem para treino de impressao porque misturam curvas, detalhes pequenos e cores fortes. O {name} tambem e interessante para comparar filamentos, testar troca de cor e criar conteudo visual para grupos de makers.</p>

<p>Para iniciantes, a vantagem e ter um personagem reconhecivel mesmo quando a impressao ainda nao esta perfeita. Isso torna o teste mais divertido e ajuda a enxergar onde a impressora precisa melhorar.</p>

<h2>Antes de baixar o arquivo</h2>
<p>Antes de abrir o arquivo no slicer, confira a pagina original. Veja se existe perfil de impressao, comentarios recentes, fotos de usuarios e atualizacoes do criador.</p>

<ul>
  <li>confira se o modelo tem STL, 3MF ou perfil pronto;</li>
  <li>observe se ha recomendacao de suporte ou orientacao de impressao;</li>
  <li>veja se outros makers relataram problema de escala;</li>
  <li>leia a licenca antes de qualquer uso comercial;</li>
  <li>salve o link original para baixar futuras atualizacoes.</li>
</ul>

<h2>Material recomendado</h2>
<p>Para a maioria dos casos, use <strong>PLA</strong>. Ele e barato, facil de imprimir e tem boa variedade de cores. Em personagens multicoloridos, voce pode usar troca manual de filamento, pintura depois da impressao ou sistema multicolor se sua impressora tiver esse recurso.</p>

<!--IMAGEM_2-->

<h2>Configuracao segura para comecar</h2>
<p>Uma configuracao inicial equilibrada para imprimir o {name} em FDM seria:</p>

<ul>
  <li>altura de camada entre 0,16 mm e 0,20 mm;</li>
  <li>10% a 15% de preenchimento para peca decorativa;</li>
  <li>2 ou 3 paredes;</li>
  <li>suporte apenas onde o slicer indicar necessidade;</li>
  <li>velocidade moderada para preservar detalhes;</li>
  <li>mesa bem nivelada e primeira camada limpa.</li>
</ul>

<p>Se voce ainda nao conhece o modelo, faca uma impressao menor primeiro. Esse teste evita perder horas de maquina e ajuda a encontrar suporte ruim, base pequena ou detalhes frageis.</p>

<h2>Cuidados com escala, suporte e acabamento</h2>
<p>Ao aumentar a escala, detalhes pequenos ficam mais bonitos, mas o consumo de filamento cresce rapido. Ao reduzir demais, olhos, pontas, patas, folhas, asas ou partes finas podem perder definicao.</p>

<p>Depois de imprimir, remova os suportes com calma. Em personagens, marcas de suporte aparecem bastante em areas curvas. Se quiser acabamento melhor, use lixa fina, primer e pintura leve.</p>

<h2>Pode vender a peca impressa?</h2>
<p>Tenha cuidado. Pokemon e uma marca conhecida. Mesmo quando o arquivo e gratuito, vender personagem famoso pode envolver risco de direitos autorais e marca. Para venda, prefira arquivos autorais, modelos com licenca comercial clara ou personagens proprios.</p>

<h2>Vale a pena baixar?</h2>
<p>Sim, se o objetivo for aprendizado, decoracao, teste de cor ou colecao pessoal. O melhor caminho e baixar pela pagina original, imprimir primeiro em escala moderada e registrar a configuracao que funcionou.</p>

{download_cta(name, url, label)}

<h2>Perguntas frequentes sobre {name} STL gratis</h2>

<h3>Esse modelo e bom para iniciantes?</h3>
<p>Sim. Ele e indicado para testar acabamento, suporte e cores sem depender de uma peca funcional complexa.</p>

<h3>Qual filamento usar?</h3>
<p>PLA e o material mais indicado para comecar. Ele e facil de imprimir, barato e tem muitas cores para personagens.</p>

<h3>Precisa de suporte?</h3>
<p>Depende da orientacao do modelo e da versao baixada. Abra no slicer e confira as areas suspensas antes de imprimir.</p>

<h3>Posso vender o Pokemon impresso?</h3>
<p>Tenha cautela. Para uso comercial, confira direitos de marca e licenca do arquivo. O uso mais seguro e aprendizado, teste e colecao pessoal.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Esse modelo e bom para iniciantes?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Sim. Ele e indicado para testar acabamento, suporte e cores sem depender de uma peca funcional complexa."}}
    }},
    {{
      "@type": "Question",
      "name": "Qual filamento usar?",
      "acceptedAnswer": {{"@type": "Answer", "text": "PLA e o material mais indicado para comecar. Ele e facil de imprimir, barato e tem muitas cores para personagens."}}
    }},
    {{
      "@type": "Question",
      "name": "Precisa de suporte?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Depende da orientacao do modelo e da versao baixada. Abra no slicer e confira as areas suspensas antes de imprimir."}}
    }},
    {{
      "@type": "Question",
      "name": "Posso vender o Pokemon impresso?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Tenha cautela. Para uso comercial, confira direitos de marca e licenca do arquivo. O uso mais seguro e aprendizado, teste e colecao pessoal."}}
    }}
  ]
}}
</script>
"""


def atualizar_controle(created: list[dict]) -> None:
    if not created:
        return
    text = CONTROL_PATH.read_text(encoding="utf-8")
    marker = "\n## Regra Para Novos Posts\n"
    number = next_post_number()
    rows = []
    for item in created:
        rows.append(
            f"| {number} | {item['title']} | `{item['slug']}` | {item['wp_id']} | rascunho | nao enviado | "
            "sem afiliado | Post Pokemon criado pelo lote `CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS`, "
            f"com fotos locais e CTA final para download no MakerWorld. |\n"
        )
        number += 1
    text = text.replace(marker, "".join(rows) + marker)
    CONTROL_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    carregar_env()
    pub = WordPressPublisher(config_wp())
    packages = [build_package(item, "", CATEGORY) for item in scan_batch(ROOT_FOLDER)]
    created: list[dict] = []
    skipped: list[str] = []

    for pacote in packages:
        name = display_name(pacote["keyword_alvo"])
        if name == "Pikachu":
            skipped.append(name)
            continue
        slug = slugify(f"{name} STL gratis impressao 3D")
        if controle_has_slug(slug):
            skipped.append(name)
            continue
        images = preparar_imagens(pacote, slug)
        if not images:
            print(f"SEM IMAGEM: {name}")
            skipped.append(name)
            continue
        title = title_for(name)
        keyphrase = keyphrase_for(name)
        post = {
            "titulo": title,
            "slug": slug,
            "content": content_for(name, pacote),
            "excerpt": f"Baixe o modelo 3D gratuito do {name} e veja dicas de PLA, escala, suporte e cuidados de impressao.",
            "status": "draft",
            "categories": [CATEGORY],
            "tags": ["Pokemon", name, "STL gratis", "impressao 3D", "MakerWorld"],
            "yoast_keyphrase": keyphrase,
            "yoast_title": f"{name} STL Gratis para Impressao 3D",
            "yoast_meta": f"Veja o {name} STL gratis para imprimir em 3D, com dicas de PLA, escala, suporte e link para baixar no MakerWorld.",
            "imagens_lista": images,
        }
        print(f"PUBLICANDO: {title}")
        result = pub.publicar_post(post, skip_if_exists=True)
        if result and result.get("status") != "existente":
            created.append({"title": title, "slug": slug, "wp_id": result["wp_id"], "url": result.get("url", "")})
        else:
            skipped.append(name)

    atualizar_controle(created)
    print({"criados": len(created), "pulados": skipped, "ids": [item["wp_id"] for item in created]})


if __name__ == "__main__":
    main()
