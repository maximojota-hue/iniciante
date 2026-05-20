"""
Publica rascunhos em lote para Top MakerWorld.

Origem: pacote leve CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS.
Nao usa API externa de conteudo; gera HTML local, usa fotos das pastas,
insere afiliados do pacote e publica rascunhos no WordPress.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import asdict
from pathlib import Path

from PIL import Image

from preparador_pacote_personagem import build_package, carregar_afiliados, scan_batch
from publisher import WordPressPublisher


ROOT_FOLDER = Path(r"C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\posts\pagina\top makerworld")
CATEGORY = "Games & Personagens"
CONTROL_PATH = Path("CONTROLE_POSTS.md")
AFFILIATE_IDS = {1, 2, 9}
AFFILIATE_MARKER = "clube3d-afiliados-top-makerworld"


NAME_BY_URL_TOKEN = {
    "donkey-kong-dk": "Donkey Kong DK Porta-Canetas",
    "thanos-no-ams": "Thanos Sem AMS",
    "thank-you-6k-naruto": "Naruto Fanart 25 cm",
    "thanks-2k-goku-daima": "Goku Daima Fanart 19 cm",
    "naruto-akatsuki-controller": "Suporte para Controle Naruto Akatsuki",
    "not-a-meowning-person": "Nao Sou Uma Pessoa Matinal",
    "mario-super-mario-movie": "Mario do Filme Super Mario",
    "stylized-eagle-owl": "Estatueta de Coruja-Real",
    "chibi-street-fighter-chun-li": "Chun-Li Chibi Street Fighter",
    "bowser-attack": "Ataque do Bowser",
    "chibi-street-fighter-ryu": "Ryu Chibi Street Fighter",
    "cute-cat-photo-frame": "Porta-Retrato de Gato Fofo",
    "dog-in-a-dinosaur-costume": "Cachorro com Fantasia de Dinossauro",
}


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


def display_name(pacote: dict) -> str:
    url = pacote["fonte"].get("download_url", "")
    for token, name in NAME_BY_URL_TOKEN.items():
        if token in url:
            return name
    keyword = pacote.get("keyword_alvo") or pacote["fonte"].get("keyword_sugerida") or pacote["fonte"].get("titulo_sugerido")
    keyword = re.sub(r"\((?:sem|nao|não)?\s*ams[^)]*\)", "", keyword, flags=re.IGNORECASE)
    keyword = re.sub(r"\b(modelo|gratuito|gratis|para|impressao|3d|makerworld)\b", "", keyword, flags=re.IGNORECASE)
    keyword = re.sub(r"\s+", " ", keyword).strip(" -_")
    return keyword[:72] if keyword else "Modelo 3D MakerWorld"


def title_for(name: str) -> str:
    return f"{name} STL Gratis no MakerWorld: Modelo 3D para Imprimir"


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


def preparar_foto_afiliado(afiliado: dict) -> str:
    src = Path(afiliado["foto"])
    if not src.exists():
        raise SystemExit(f"Foto de afiliado nao encontrada: #{afiliado['id']} {src}")
    out_dir = Path("downloads/afiliados/top-makerworld")
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
        _, media_url = pub.upload_media(local, alt_text=f"{af['nome']} produto indicado para impressao 3D")
        if not media_url:
            raise SystemExit(f"Falha ao enviar imagem do afiliado #{af['id']}.")
        urls[af["id"]] = media_url
    return urls


def affiliate_block(afiliados: list[dict], media_urls: dict[int, str], name: str) -> str:
    cards = []
    for af in afiliados:
        cards.append(
            f"""
    <div style="border:1px solid #1f2937;border-radius:8px;padding:14px;background:#0b1220;">
      <a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="display:block;text-decoration:none;">
        <img src="{media_urls[af['id']]}" alt="{af['nome']} produto indicado para imprimir {name}" style="width:100%;max-width:360px;height:auto;border-radius:6px;display:block;margin:0 auto 10px;" />
      </a>
      <p style="margin:0 0 8px;color:#f8fafc;font-weight:800;">{af['nome']}</p>
      <p style="margin:0 0 12px;color:#cbd5e1;">Produto de apoio para testar o modelo, escolher filamento e melhorar o acabamento da impressao.</p>
      <p style="margin:0;"><a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="color:#ffb36c;font-weight:800;">Ver oferta</a></p>
    </div>
"""
        )
    return f"""
<!-- {AFFILIATE_MARKER} inicio -->
<div style="border:2px solid #ff6a13;background:#070b12;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Produtos indicados para imprimir modelos do MakerWorld</p>
  <p style="margin:0 0 16px;color:#e5e7eb;">Separei estes produtos para quem quer baixar o STL gratis, testar material e melhorar o resultado final.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
    {''.join(cards)}
  </div>
</div>
<!-- {AFFILIATE_MARKER} fim -->
"""


def download_cta(name: str, url: str, label: str) -> str:
    return f"""
<div style="border:2px solid #ff6a13;background:#100904;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Baixar STL gratis no MakerWorld</p>
  <p style="margin:0 0 14px;color:#fff4e8;">Acesse a pagina original para baixar o modelo gratuito do {name}, conferir perfil de impressao, fotos, comentarios e atualizacoes do criador.</p>
  <p style="margin:0;">
    <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#ff6a13;color:#111;padding:12px 18px;border-radius:6px;font-weight:800;text-decoration:none;">
      Abrir pagina do {name} no MakerWorld
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
<p>O <strong>{keyphrase}</strong> e uma opcao interessante para quem procura um modelo 3D gratuito no MakerWorld e quer imprimir uma peca visualmente chamativa sem depender de um projeto tecnico complicado.</p>

<p>Neste guia, voce ve como analisar o {name} antes de baixar, quais cuidados tomar no slicer, que material usar e como aproveitar melhor as fotos e informacoes da pagina original.</p>

<!--IMAGEM_1-->

<h2>Por que baixar o {name}?</h2>
<p>Modelos gratuitos do MakerWorld ajudam muito quem esta montando uma rotina de testes. Voce consegue avaliar acabamento, suporte, escala, cor e tempo de impressao sem gastar com arquivo pago logo de inicio.</p>

<p>O {name} tambem funciona bem para criar conteudo visual, testar filamentos diferentes e movimentar grupos de makers com resultados reais de impressao.</p>

<h2>Antes de abrir no slicer</h2>
<p>Antes de imprimir, acesse a pagina original do MakerWorld. Verifique se existe perfil pronto, comentarios recentes, fotos de usuarios, versoes atualizadas e observacoes do criador.</p>

<ul>
  <li>confira se o arquivo vem em STL, 3MF ou perfil de impressao;</li>
  <li>observe se o modelo pede suporte ou montagem por partes;</li>
  <li>veja se a impressao foi pensada para ser feita sem AMS;</li>
  <li>leia a licenca antes de vender qualquer peca impressa;</li>
  <li>salve o link original para baixar futuras atualizacoes.</li>
</ul>

{affiliate_block(afiliados, media_urls, name)}

<h2>Material recomendado</h2>
<p>Para comecar, o <strong>PLA</strong> e o material mais seguro. Ele imprime facil, tem boa variedade de cores e costuma entregar um acabamento bonito em pecas decorativas, suportes, personagens e objetos de mesa.</p>

<!--IMAGEM_2-->

<h2>Configuracao inicial segura</h2>
<p>Uma configuracao equilibrada para testar o {name} em impressoras FDM seria:</p>

<ul>
  <li>altura de camada entre 0,16 mm e 0,20 mm;</li>
  <li>10% a 15% de preenchimento em pecas decorativas;</li>
  <li>2 ou 3 paredes;</li>
  <li>suporte somente onde houver area suspensa real;</li>
  <li>velocidade moderada para preservar detalhes;</li>
  <li>primeira camada bem ajustada antes de imprimir grande.</li>
</ul>

<h2>Cuidados com escala e acabamento</h2>
<p>Se for um personagem ou peca com muitos detalhes, evite reduzir demais. Partes pequenas podem perder definicao, quebrar durante a remocao de suporte ou ficar dificeis de pintar.</p>

<p>Se for um suporte, porta-retrato ou porta-canetas, confira a escala pensando no uso real. Um teste menor pode mostrar se encaixes, base e espessura estao bons antes de gastar mais filamento.</p>

<h2>Vale a pena imprimir?</h2>
<p>Vale a pena se voce quer treinar impressao 3D com um arquivo gratuito, criar uma peca visual para setup ou testar filamentos de forma pratica. O melhor caminho e baixar no MakerWorld, imprimir primeiro em escala segura e guardar a configuracao que funcionou.</p>

{download_cta(name, url, label)}

<h2>Perguntas frequentes sobre {name} STL gratis</h2>

<h3>Esse modelo e gratuito?</h3>
<p>Sim. Neste post, a origem informada e o MakerWorld, entao o modelo pode ser tratado como gratuito de acordo com a pagina enviada.</p>

<h3>Precisa de AMS?</h3>
<p>Depende do arquivo. Quando o modelo vem em partes ou informa "sem AMS", voce pode imprimir cada cor separadamente e montar depois.</p>

<h3>Qual filamento usar?</h3>
<p>PLA e a melhor escolha para comecar, principalmente para pecas decorativas, personagens, suportes e testes de cor.</p>

<h3>Posso vender a peca impressa?</h3>
<p>Confira a licenca do MakerWorld antes de vender. Em personagens famosos, tambem considere risco de marca e direitos autorais.</p>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question", "name": "Esse modelo e gratuito?", "acceptedAnswer": {{"@type": "Answer", "text": "Sim. Neste post, a origem informada e o MakerWorld, entao o modelo pode ser tratado como gratuito de acordo com a pagina enviada."}}}},
    {{"@type": "Question", "name": "Precisa de AMS?", "acceptedAnswer": {{"@type": "Answer", "text": "Depende do arquivo. Quando o modelo vem em partes ou informa sem AMS, voce pode imprimir cada cor separadamente e montar depois."}}}},
    {{"@type": "Question", "name": "Qual filamento usar?", "acceptedAnswer": {{"@type": "Answer", "text": "PLA e a melhor escolha para comecar, principalmente para pecas decorativas, personagens, suportes e testes de cor."}}}},
    {{"@type": "Question", "name": "Posso vender a peca impressa?", "acceptedAnswer": {{"@type": "Answer", "text": "Confira a licenca do MakerWorld antes de vender. Em personagens famosos, tambem considere risco de marca e direitos autorais."}}}}
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
            f"{af_text} | Post Top MakerWorld criado pelo lote `CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS`, "
            "com fotos locais, afiliados do pacote e CTA final para download gratuito no MakerWorld. |\n"
        )
        number += 1
    text = text.replace(marker, "".join(rows) + marker)
    CONTROL_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    carregar_env()
    all_affiliates = [asdict(af) for af in carregar_afiliados()]
    afiliados = [af for af in all_affiliates if af["id"] in AFFILIATE_IDS]
    if {af["id"] for af in afiliados} != AFFILIATE_IDS:
        raise SystemExit("Nao encontrei os afiliados #1, #2 e #9.")

    pub = WordPressPublisher(config_wp())
    media_urls = upload_afiliados(pub, afiliados)
    packages = [build_package(item, "", CATEGORY, afiliados) for item in scan_batch(ROOT_FOLDER)]
    created: list[dict] = []
    skipped: list[str] = []

    for pacote in packages:
        name = display_name(pacote)
        slug = slugify(f"{name} STL gratis MakerWorld impressao 3D")
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
            "excerpt": f"Baixe o STL gratis do {name} no MakerWorld e veja dicas de PLA, escala, suporte e acabamento.",
            "status": "draft",
            "categories": [CATEGORY],
            "tags": ["MakerWorld", name, "STL gratis", "impressao 3D", "modelo 3D"],
            "yoast_keyphrase": keyphrase,
            "yoast_title": f"{name} STL Gratis no MakerWorld",
            "yoast_meta": f"Veja o {name} STL gratis no MakerWorld, com dicas de PLA, escala, suporte, acabamento e link para baixar o modelo.",
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
