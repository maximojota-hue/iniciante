"""
Publica rascunhos em lote para personagens Decormaster/Cults 3D.

Origem: pacote leve CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS.
Nao usa API externa de conteudo; gera HTML local, insere afiliados do pacote
e envia os rascunhos ao WordPress.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import asdict
from pathlib import Path

from PIL import Image

from preparador_pacote_personagem import (
    build_package,
    carregar_afiliados,
    scan_batch,
    traduzir_termo_principal,
)
from publisher import WordPressPublisher


ROOT_FOLDER = Path(r"C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\posts\pagina\decormaster")
CATEGORY = "Games & Personagens"
CONTROL_PATH = Path("CONTROLE_POSTS.md")
AFFILIATE_IDS = {1, 2, 3}
AFFILIATE_MARKER = "clube3d-afiliados-decormaster"


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


def clean_name(keyword: str, download_url: str = "") -> str:
    text = keyword or ""
    text = re.sub(r"[🎨👨👤]+", " ", text)
    text = text.replace("・", " ")
    text = re.sub(r"Arquivo\s+3MF.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Fan art", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\((?:no|sem)\s+ams[^)]*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCults\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[?]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" -_")
    replacements = {
        "wonder amy wonder woman x amy rose": "Wonder Amy",
        "busto de goku Arte de fa": "Busto de Goku",
        "busto de goku Arte de fã": "Busto de Goku",
        "Mario goku": "Mario Goku",
        "iron man": "Homem de Ferro (Iron Man)",
        "art the clown": "Art, o Palhaco (Art the Clown)",
        "ghostface": "Ghostface de Panico",
        "leatherface": "Leatherface",
        "kratos": "Kratos",
    }
    key = ascii_text(text).lower()
    for raw, value in replacements.items():
        if key == ascii_text(raw).lower():
            return traduzir_termo_principal(value)
    if not text and download_url:
        text = download_url.rstrip("/").split("/")[-1].replace("-", " ")
    text = text[:1].upper() + text[1:] if text else "Personagem 3D"
    return traduzir_termo_principal(text)


def title_for(name: str) -> str:
    return f"{name} 3MF: Fan Art para Imprimir em 3D"


def keyphrase_for(name: str) -> str:
    return f"{name} 3MF"


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


def preparar_foto_afiliado(afiliado: dict) -> str:
    src = Path(afiliado["foto"])
    if not src.exists():
        raise SystemExit(f"Foto de afiliado nao encontrada: #{afiliado['id']} {src}")
    out_dir = Path("downloads/afiliados/decormaster")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"afiliado-{afiliado['id']}-{slugify(afiliado['nome'])}.jpg"
    if not out.exists():
        img = Image.open(src).convert("RGB")
        img.thumbnail((900, 700))
        img.save(out, quality=84, optimize=True)
    return str(out)


def upload_afiliados(pub: WordPressPublisher, afiliados: list[dict]) -> dict[int, str]:
    urls: dict[int, str] = {}
    for af in afiliados:
        local = preparar_foto_afiliado(af)
        _, media_url = pub.upload_media(
            local,
            alt_text=f"{af['nome']} produto indicado para impressao 3D",
        )
        if not media_url:
            raise SystemExit(f"Falha ao enviar imagem do afiliado #{af['id']}.")
        urls[af["id"]] = media_url
    return urls


def affiliate_block(afiliados: list[dict], media_urls: dict[int, str]) -> str:
    cards = []
    for af in afiliados:
        cards.append(
            f"""
    <div style="border:1px solid #1f2937;border-radius:8px;padding:14px;background:#0b1220;">
      <a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="display:block;text-decoration:none;">
        <img src="{media_urls[af['id']]}" alt="{af['nome']} produto indicado para impressao 3D" style="width:100%;max-width:360px;height:auto;border-radius:6px;display:block;margin:0 auto 10px;" />
      </a>
      <p style="margin:0 0 8px;color:#f8fafc;font-weight:800;">{af['nome']}</p>
      <p style="margin:0 0 12px;color:#cbd5e1;">Produto de apoio para imprimir fan arts, modelos 3MF e personagens decorativos com mais praticidade.</p>
      <p style="margin:0;"><a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="color:#ffb36c;font-weight:800;">Ver oferta</a></p>
    </div>
"""
        )
    return f"""
<!-- {AFFILIATE_MARKER} inicio -->
<div style="border:2px solid #ff6a13;background:#070b12;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Produtos indicados para imprimir fan arts em 3D</p>
  <p style="margin:0 0 16px;color:#e5e7eb;">Use estes itens como apoio para testar o modelo, escolher filamento e melhorar o acabamento da sua impressao.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
    {''.join(cards)}
  </div>
</div>
<!-- {AFFILIATE_MARKER} fim -->
"""


def download_cta(name: str, url: str, label: str) -> str:
    return f"""
<div style="border:2px solid #ff6a13;background:#100904;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Baixar modelo 3D</p>
  <p style="margin:0 0 14px;color:#fff4e8;">Acesse a pagina original do criador para baixar o arquivo do {name}, conferir licenca, fotos, comentarios e atualizacoes.</p>
  <p style="margin:0;">
    <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#ff6a13;color:#111;padding:12px 18px;border-radius:6px;font-weight:800;text-decoration:none;">
      Abrir pagina de download do {name}
    </a>
  </p>
  <p style="margin:12px 0 0;color:#cbd5e1;font-size:14px;">Fonte: {label}</p>
</div>
"""


def content_for(name: str, pacote: dict, afiliados: list[dict], media_urls: dict[int, str]) -> str:
    keyphrase = keyphrase_for(name)
    url = pacote["fonte"]["download_url"]
    label = pacote["fonte"]["download_label"]
    return f"""
<p>O <strong>{keyphrase}</strong> e uma fan art em formato 3MF para quem gosta de personagens marcantes, decoracao geek e impressoes multicoloridas sem depender obrigatoriamente de AMS. A proposta e baixar o modelo pela pagina original, testar em escala segura e ajustar acabamento antes de gastar muito filamento.</p>

<p>Este guia rapido ajuda a decidir como imprimir o {name}, quais cuidados tomar com material, suporte, escala e licenca, alem de separar produtos uteis para quem quer transformar esses modelos em pecas bonitas para colecao.</p>

<!--IMAGEM_1-->

<h2>Por que imprimir o {name}?</h2>
<p>Fan arts decorativas sao excelentes para testar qualidade visual. Elas mostram rapidamente se a impressora esta lidando bem com curvas, pequenos detalhes, separacao de pecas e troca de cor manual.</p>

<p>Como muitos arquivos deste tipo usam partes separadas, o resultado pode ficar chamativo mesmo em impressoras simples. A vantagem e poder imprimir cada cor em um PLA diferente e montar depois com mais controle.</p>

<h2>Antes de baixar no Cults</h2>
<p>Antes de baixar ou imprimir, confira a pagina original. Veja se o arquivo esta atualizado, se ha instrucoes de montagem, fotos reais, comentarios e informacoes de licenca.</p>

<ul>
  <li>confira se o download inclui 3MF, STL ou partes separadas;</li>
  <li>verifique se o modelo foi pensado para impressao sem AMS;</li>
  <li>leia a licenca antes de vender qualquer peca impressa;</li>
  <li>observe imagens de outros usuarios quando existirem;</li>
  <li>salve a pagina original para baixar atualizacoes.</li>
</ul>

{affiliate_block(afiliados, media_urls)}

<h2>Material recomendado</h2>
<p>Para esse tipo de fan art, o <strong>PLA</strong> e o material mais pratico. Ele facilita a impressao, tem ampla variedade de cores e oferece bom acabamento para decoracao. Se voce for montar partes separadas, escolha cores consistentes e faca um teste pequeno de encaixe antes da versao final.</p>

<!--IMAGEM_2-->

<h2>Configuracao segura no slicer</h2>
<p>Uma configuracao inicial equilibrada para imprimir o {name} seria:</p>

<ul>
  <li>altura de camada entre 0,16 mm e 0,20 mm;</li>
  <li>10% a 15% de preenchimento para peca decorativa;</li>
  <li>2 ou 3 paredes;</li>
  <li>suporte apenas onde houver area suspensa real;</li>
  <li>velocidade moderada para preservar detalhes;</li>
  <li>teste menor antes de imprimir grande.</li>
</ul>

<h2>Cuidados com montagem e acabamento</h2>
<p>Se o modelo vier em varias partes, organize as pecas por cor antes de imprimir. Isso reduz troca de filamento e evita misturar componentes parecidos. Depois da impressao, teste encaixes antes de colar definitivamente.</p>

<p>Para acabamento melhor, remova suportes com calma, use lixa fina em marcas aparentes e aplique cola apenas depois de confirmar o alinhamento. Em pecas decorativas, pequenos ajustes fazem muita diferenca no resultado final.</p>

<h2>Atencao ao uso comercial</h2>
<p>Como se trata de fan art, tenha cuidado com venda. Personagens conhecidos podem envolver direitos autorais e marcas registradas. O uso mais seguro e aprendizado, teste, colecao pessoal e estudo de acabamento.</p>

<h2>Vale a pena baixar?</h2>
<p>Vale, principalmente para quem quer treinar impressao colorida, montar uma prateleira geek ou testar modelos decorativos com visual forte. Baixe pela pagina original, comece em escala menor e registre as configuracoes que funcionarem.</p>

{download_cta(name, url, label)}

<h2>Perguntas frequentes sobre {name} 3MF</h2>

<h3>Esse modelo precisa de AMS?</h3>
<p>Nem sempre. Muitos modelos multiparts permitem imprimir cada peca em uma cor diferente e montar depois, sem AMS.</p>

<h3>Qual filamento usar?</h3>
<p>PLA e a melhor escolha para comecar, porque imprime facil, tem muitas cores e entrega bom acabamento em pecas decorativas.</p>

<h3>Posso vender a fan art impressa?</h3>
<p>Tenha cuidado. Fan arts de personagens conhecidos podem envolver direitos autorais e marca. Verifique a licenca e evite uso comercial sem permissao clara.</p>

<h3>Precisa imprimir grande?</h3>
<p>Nao. O ideal e testar pequeno primeiro. Depois que suporte, encaixe e cores estiverem certos, aumente a escala.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question", "name": "Esse modelo precisa de AMS?", "acceptedAnswer": {{"@type": "Answer", "text": "Nem sempre. Muitos modelos multiparts permitem imprimir cada peca em uma cor diferente e montar depois, sem AMS."}}}},
    {{"@type": "Question", "name": "Qual filamento usar?", "acceptedAnswer": {{"@type": "Answer", "text": "PLA e a melhor escolha para comecar, porque imprime facil, tem muitas cores e entrega bom acabamento em pecas decorativas."}}}},
    {{"@type": "Question", "name": "Posso vender a fan art impressa?", "acceptedAnswer": {{"@type": "Answer", "text": "Tenha cuidado. Fan arts de personagens conhecidos podem envolver direitos autorais e marca. Verifique a licenca e evite uso comercial sem permissao clara."}}}},
    {{"@type": "Question", "name": "Precisa imprimir grande?", "acceptedAnswer": {{"@type": "Answer", "text": "Nao. O ideal e testar pequeno primeiro. Depois que suporte, encaixe e cores estiverem certos, aumente a escala."}}}}
  ]
}}
</script>
"""


def atualizar_controle(created: list[dict], afiliados: list[dict]) -> None:
    if not created:
        return
    text = CONTROL_PATH.read_text(encoding="utf-8")
    marker = "\n## Regra Para Novos Posts\n"
    number = next_post_number()
    af_text = "; ".join(f"#{af['id']} {af['nome']}" for af in afiliados)
    rows = []
    for item in created:
        rows.append(
            f"| {number} | {item['title']} | `{item['slug']}` | {item['wp_id']} | rascunho | nao enviado | "
            f"{af_text} | Post Decormaster/Cults criado pelo lote `CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS`, "
            "com fotos locais, afiliados do pacote e CTA final para download no Cults. |\n"
        )
        number += 1
    text = text.replace(marker, "".join(rows) + marker)
    CONTROL_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    carregar_env()
    all_affiliates = [asdict(af) for af in carregar_afiliados()]
    afiliados = [af for af in all_affiliates if af["id"] in AFFILIATE_IDS]
    if len(afiliados) != 3:
        raise SystemExit("Nao encontrei os afiliados #1, #2 e #3.")

    pub = WordPressPublisher(config_wp())
    media_urls = upload_afiliados(pub, afiliados)
    packages = [build_package(item, "", CATEGORY, afiliados) for item in scan_batch(ROOT_FOLDER)]
    created: list[dict] = []
    skipped: list[str] = []

    for pacote in packages:
        name = clean_name(pacote["keyword_alvo"], pacote["fonte"]["download_url"])
        slug = slugify(f"{name} 3MF impressao 3D")
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
            "content": content_for(name, pacote, afiliados, media_urls),
            "excerpt": f"Veja o modelo 3MF do {name} e confira dicas de PLA, montagem, escala e acabamento.",
            "status": "draft",
            "categories": [CATEGORY],
            "tags": ["Cults", "Fan art", name, "3MF", "impressao 3D"],
            "yoast_keyphrase": keyphrase,
            "yoast_title": f"{name} 3MF para Impressao 3D",
            "yoast_meta": f"Veja o {name} 3MF para imprimir em 3D, com dicas de PLA, montagem, acabamento e link para acessar a pagina no Cults.",
            "imagens_lista": images,
        }
        print(f"PUBLICANDO: {title}")
        result = pub.publicar_post(post, skip_if_exists=True)
        if result and result.get("status") != "existente":
            created.append({"title": title, "slug": slug, "wp_id": result["wp_id"], "url": result.get("url", "")})
        else:
            skipped.append(name)

    atualizar_controle(created, afiliados)
    print({"criados": len(created), "pulados": skipped, "ids": [item["wp_id"] for item in created]})


if __name__ == "__main__":
    main()
