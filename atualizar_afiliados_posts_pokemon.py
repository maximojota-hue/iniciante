"""
Atualiza posts Pokemon publicados com 2 afiliados aleatorios por post.

Nao usa API externa de conteudo. Apenas edita HTML existente no WordPress,
inserindo imagens clicaveis dos afiliados com target blank e rel sponsored.
"""

from __future__ import annotations

import os
import random
import re
from pathlib import Path

from PIL import Image

from publisher import WordPressPublisher


CONTROL_POSTS = Path("CONTROLE_POSTS.md")
CONTROL_AFILIADOS = Path("CONTROLE_AFILIADOS.md")
OUT_DIR = Path("downloads/afiliados/pokemon")
MARKER = "clube3d-afiliados-pokemon"

POST_IDS = [3067, 3073, 3077, 3081, 3085, 3089, 3093, 3097, 3101, 3105, 3109, 3113]


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
    }


def carregar_afiliados() -> list[dict]:
    afiliados: list[dict] = []
    for line in CONTROL_AFILIADOS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or "Nome curto" in line or "|---" in line:
            continue
        cols = [col.strip() for col in line.strip("|").split("|")]
        if len(cols) < 6 or not cols[0].isdigit():
            continue
        afiliados.append(
            {
                "id": int(cols[0]),
                "nome": cols[1],
                "link": cols[2].strip("`"),
                "foto": cols[3].strip("`"),
                "obs": cols[5],
            }
        )
    if len(afiliados) < 2:
        raise SystemExit("E necessario ter pelo menos 2 afiliados cadastrados.")
    return afiliados


def safe_slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "afiliado"


def preparar_foto(afiliado: dict) -> str:
    src = Path(afiliado["foto"])
    if not src.exists():
        raise SystemExit(f"Foto de afiliado nao encontrada: #{afiliado['id']} {src}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"afiliado-{afiliado['id']}-{safe_slug(afiliado['nome'])}.jpg"
    if not out.exists():
        img = Image.open(src).convert("RGB")
        img.thumbnail((900, 700))
        img.save(out, quality=84, optimize=True)
    return str(out)


def upload_afiliados(pub: WordPressPublisher, afiliados: list[dict]) -> dict[int, str]:
    urls: dict[int, str] = {}
    for af in afiliados:
        local = preparar_foto(af)
        media_id, media_url = pub.upload_media(
            local,
            alt_text=f"{af['nome']} produto indicado para impressao 3D",
        )
        if not media_url:
            raise SystemExit(f"Falha ao enviar imagem do afiliado #{af['id']}.")
        urls[af["id"]] = media_url
    return urls


def bloco_afiliados(afiliados: list[dict], media_urls: dict[int, str]) -> str:
    cards = []
    for af in afiliados:
        image = media_urls[af["id"]]
        cards.append(
            f"""
    <div style="border:1px solid #1f2937;border-radius:8px;padding:14px;background:#0b1220;">
      <a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="display:block;text-decoration:none;">
        <img src="{image}" alt="{af['nome']} produto indicado para impressao 3D" style="width:100%;max-width:360px;height:auto;border-radius:6px;display:block;margin:0 auto 10px;" />
      </a>
      <p style="margin:0 0 8px;color:#f8fafc;font-weight:800;">{af['nome']}</p>
      <p style="margin:0 0 12px;color:#cbd5e1;">Produto util para imprimir modelos Pokemon, testar STL gratis e melhorar seu fluxo de impressao 3D.</p>
      <p style="margin:0;"><a href="{af['link']}" target="_blank" rel="noopener noreferrer sponsored" style="color:#ffb36c;font-weight:800;">Ver oferta</a></p>
    </div>
"""
        )
    return f"""
<!-- {MARKER} inicio -->
<div style="border:2px solid #ff6a13;background:#070b12;padding:18px 20px;margin:30px 0;border-radius:8px;">
  <p style="margin:0 0 8px;color:#ffb36c;font-weight:800;text-transform:uppercase;">Produtos indicados para imprimir Pokemon em 3D</p>
  <p style="margin:0 0 16px;color:#e5e7eb;">Separei duas sugestoes de apoio para quem quer imprimir estes modelos com mais praticidade: filamento, impressora ou acessorios cadastrados no Clube 3D Brasil.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
    {''.join(cards)}
  </div>
</div>
<!-- {MARKER} fim -->
"""


def inserir_bloco(content: str, bloco: str) -> str:
    if MARKER in content:
        return content
    download_marker = '<div style="border:2px solid #ff6a13;background:#100904'
    if download_marker in content:
        return content.replace(download_marker, bloco + "\n" + download_marker, 1)
    faq_marker = "<h2>Perguntas frequentes"
    if faq_marker in content:
        return content.replace(faq_marker, bloco + "\n" + faq_marker, 1)
    return content + "\n" + bloco


def atualizar_controle(selecoes: dict[int, list[dict]], statuses: dict[int, str]) -> None:
    text = CONTROL_POSTS.read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if not line.startswith("| "):
            lines.append(line)
            continue
        cols = [col.strip() for col in line.strip("|").split("|")]
        if len(cols) < 8 or not cols[3].isdigit():
            lines.append(line)
            continue
        wp_id = int(cols[3])
        if wp_id not in selecoes:
            lines.append(line)
            continue
        afiliado_text = "; ".join(f"#{af['id']} {af['nome']}" for af in selecoes[wp_id])
        cols[4] = "publicado" if statuses.get(wp_id) == "publish" else cols[4]
        cols[6] = afiliado_text
        obs = cols[7]
        if "Afiliados inseridos" not in obs:
            obs = obs.rstrip(".") + f". Afiliados inseridos aleatoriamente: {afiliado_text}."
        cols[7] = obs
        lines.append("| " + " | ".join(cols) + " |")
    CONTROL_POSTS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    carregar_env()
    afiliados = carregar_afiliados()
    pub = WordPressPublisher(config_wp())
    media_urls = upload_afiliados(pub, afiliados)
    rng = random.Random(20260516)
    selecoes: dict[int, list[dict]] = {}
    statuses: dict[int, str] = {}

    for wp_id in POST_IDS:
        post = pub._request("GET", f"posts/{wp_id}", params={"context": "edit"})
        status = post.get("status", "")
        statuses[wp_id] = status
        title = post.get("title", {}).get("raw") or post.get("title", {}).get("rendered", "")
        content = post.get("content", {}).get("raw") or post.get("content", {}).get("rendered", "")
        escolhidos = rng.sample(afiliados, 2)
        selecoes[wp_id] = escolhidos
        novo_content = inserir_bloco(content, bloco_afiliados(escolhidos, media_urls))
        if novo_content != content:
            pub._request("POST", f"posts/{wp_id}", json={"content": novo_content})
            print(f"Atualizado {wp_id}: {title} -> {[af['id'] for af in escolhidos]}")
        else:
            print(f"Ja tinha afiliados {wp_id}: {title}")

    atualizar_controle(selecoes, statuses)
    print({"posts": len(POST_IDS), "atualizados": len(selecoes)})


if __name__ == "__main__":
    main()
