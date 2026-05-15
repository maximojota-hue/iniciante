"""
Atualiza a hub atual do Clube 3D Brasil com um bloco de conversao para:
- baixar STL gratis
- entrar nos grupos
- descobrir arquivos baratos/testados
- participar de vaquinhas de arquivos premium

Uso:
  python atualizar_hub_atual_stl_grupos.py

Opcional no .env:
  TELEGRAM_INVITE_URL=https://t.me/+convite_publico_do_grupo
"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

import requests


WHATSAPP_PRINCIPAL = "https://chat.whatsapp.com/CVnLPEIcaIE3BeIk2lwDVZ"
WHATSAPP_STL = "https://chat.whatsapp.com/DnPdJcOuVcfCln1vAdgWwj"
WHATSAPP_GERAL = "https://chat.whatsapp.com/DEZxJq456FW7xACVxZvXod"

BLOCO_INICIO = "<!-- clube3d-hub-stl-gratis-grupos:start -->"
BLOCO_FIM = "<!-- clube3d-hub-stl-gratis-grupos:end -->"


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for linha in env.read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.startswith("#"):
            key, _, value = linha.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def conectar() -> tuple[requests.Session, str, str]:
    carregar_env()
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    wp_url = config.get("wp_url", "https://clube3dbrasil.com").rstrip("/")
    user = os.environ.get("WP_USER", "")
    password = os.environ.get("WP_PASS", "")
    if not user or not password:
        raise SystemExit("WP_USER/WP_PASS nao encontrados no .env.")

    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 Clube3DHub/1.0",
    })
    api = f"{wp_url}/wp-json/wp/v2"
    r = session.get(f"{api}/users/me", timeout=20)
    if r.status_code != 200:
        raise SystemExit(f"Falha na autenticacao WordPress: {r.status_code} {r.text[:160]}")
    print(f"Conectado ao WordPress como: {r.json().get('name', '')}")
    return session, api, wp_url


def localizar_hub_atual(session: requests.Session, api: str) -> dict:
    settings = session.get(f"{api}/settings", timeout=20)
    if settings.status_code == 200:
        page_id = settings.json().get("page_on_front")
        if page_id:
            page = session.get(f"{api}/pages/{page_id}", params={"context": "edit"}, timeout=20)
            if page.status_code == 200:
                return page.json()

    for slug in ("home", "inicio", "pagina-inicial", "principal"):
        page = session.get(
            f"{api}/pages",
            params={"slug": slug, "per_page": 1, "context": "edit"},
            timeout=20,
        )
        if page.status_code == 200 and page.json():
            return page.json()[0]

    raise SystemExit("Nao encontrei a hub atual via page_on_front nem pelos slugs home/inicio.")


def bloco_telegram() -> str:
    telegram_url = os.environ.get("TELEGRAM_INVITE_URL", "").strip()
    if not telegram_url:
        return ""
    return (
        f'<a class="c3d-community-btn c3d-community-btn-blue" href="{telegram_url}" '
        'target="_blank" rel="noopener">Entrar no Telegram</a>'
    )


def bloco_comunidade() -> str:
    telegram = bloco_telegram()
    return f"""
{BLOCO_INICIO}
<style>
.c3d-community-hub {{
  --c3d-ink: #151515;
  --c3d-muted: #596170;
  --c3d-line: #d9dee8;
  --c3d-green: #168a4a;
  --c3d-blue: #1457d9;
  --c3d-orange: #ff6a13;
  margin: 28px 0;
  border: 2px solid var(--c3d-ink);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 7px 7px 0 rgba(21, 21, 21, .12);
}}
.c3d-community-top {{
  padding: clamp(22px, 4vw, 38px);
  background:
    linear-gradient(135deg, rgba(255, 212, 71, .65), rgba(255, 255, 255, .94) 46%),
    radial-gradient(circle at 90% 12%, rgba(20, 87, 217, .18), transparent 34%);
}}
.c3d-community-kicker {{
  display: inline-block;
  margin-bottom: 10px;
  padding: 6px 10px;
  border: 2px solid var(--c3d-ink);
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}}
.c3d-community-hub h2 {{
  margin: 0 0 10px;
  color: var(--c3d-ink);
  font-size: clamp(28px, 5vw, 48px);
  line-height: 1;
}}
.c3d-community-hub p {{
  max-width: 820px;
  margin: 0 0 18px;
  color: #2d333d;
  font-size: 18px;
  line-height: 1.42;
}}
.c3d-community-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}}
.c3d-community-btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 11px 15px;
  border: 2px solid var(--c3d-ink);
  border-radius: 8px;
  background: var(--c3d-green);
  color: #fff !important;
  font-weight: 800;
  text-decoration: none !important;
  box-shadow: 3px 3px 0 rgba(21, 21, 21, .18);
}}
.c3d-community-btn-blue {{ background: var(--c3d-blue); }}
.c3d-community-btn-dark {{ background: var(--c3d-ink); }}
.c3d-community-grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  border-top: 2px solid var(--c3d-line);
}}
.c3d-community-item {{
  padding: 18px;
  border-right: 1px solid var(--c3d-line);
}}
.c3d-community-item:last-child {{ border-right: 0; }}
.c3d-community-item strong {{
  display: block;
  margin-bottom: 7px;
  color: var(--c3d-ink);
  font-size: 18px;
}}
.c3d-community-item span {{
  display: block;
  color: var(--c3d-muted);
  line-height: 1.35;
}}
@media (max-width: 900px) {{
  .c3d-community-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .c3d-community-item:nth-child(2) {{ border-right: 0; }}
  .c3d-community-item:nth-child(-n+2) {{ border-bottom: 1px solid var(--c3d-line); }}
}}
@media (max-width: 560px) {{
  .c3d-community-actions {{ display: grid; }}
  .c3d-community-grid {{ grid-template-columns: 1fr; }}
  .c3d-community-item {{
    border-right: 0;
    border-bottom: 1px solid var(--c3d-line);
  }}
  .c3d-community-item:last-child {{ border-bottom: 0; }}
}}
</style>
<section class="c3d-community-hub" aria-label="STL gratis, arquivos baratos e comunidade">
  <div class="c3d-community-top">
    <span class="c3d-community-kicker">Arquivos gratis, baratos e testados</span>
    <h2>Baixe STL gratis e entre nos grupos do Clube 3D Brasil</h2>
    <p>
      Comece com modelos gratuitos, descubra arquivos pagos baratos para testar e acompanhe
      as vaquinhas da comunidade para avaliar modelos premium sem gastar sozinho.
    </p>
    <div class="c3d-community-actions">
      <a class="c3d-community-btn" href="{WHATSAPP_STL}" target="_blank" rel="noopener">Grupo STL gratis</a>
      <a class="c3d-community-btn c3d-community-btn-blue" href="{WHATSAPP_PRINCIPAL}" target="_blank" rel="noopener">Grupo principal</a>
      <a class="c3d-community-btn c3d-community-btn-dark" href="{WHATSAPP_GERAL}" target="_blank" rel="noopener">Comunidade geral</a>
      {telegram}
    </div>
  </div>
  <div class="c3d-community-grid">
    <div class="c3d-community-item">
      <strong>STL gratis</strong>
      <span>Personagens, games, decoracao, chaveiros e modelos faceis para iniciantes.</span>
    </div>
    <div class="c3d-community-item">
      <strong>Arquivos baratos</strong>
      <span>Achados pagos de baixo custo para imprimir, comparar e evitar compra ruim.</span>
    </div>
    <div class="c3d-community-item">
      <strong>Vaquinhas</strong>
      <span>Compra coletiva de arquivos premium quando a comunidade quer testar um modelo.</span>
    </div>
    <div class="c3d-community-item">
      <strong>Testes reais</strong>
      <span>Resultados, configuracoes, filamentos e alertas compartilhados por makers brasileiros.</span>
    </div>
  </div>
</section>
{BLOCO_FIM}
"""


def atualizar_conteudo(content: str) -> tuple[str, str]:
    bloco = bloco_comunidade()
    if BLOCO_INICIO in content and BLOCO_FIM in content:
        pattern = re.compile(re.escape(BLOCO_INICIO) + r".*?" + re.escape(BLOCO_FIM), re.S)
        return pattern.sub(bloco, content), "atualizado"

    primeiro_fechamento = content.find("</p>")
    if primeiro_fechamento >= 0:
        pos = primeiro_fechamento + len("</p>")
        return content[:pos] + "\n" + bloco + "\n" + content[pos:], "adicionado"

    return bloco + "\n" + content, "adicionado"


def main() -> None:
    session, api, wp_url = conectar()
    pagina = localizar_hub_atual(session, api)
    page_id = pagina["id"]
    raw_content = pagina.get("content", {}).get("raw") or pagina.get("content", {}).get("rendered", "")
    novo_content, acao = atualizar_conteudo(raw_content)

    payload = {
        "content": novo_content,
        "meta": {
            "_yoast_wpseo_title": "Clube 3D Brasil - STL gratis, grupos e impressao 3D",
            "_yoast_wpseo_metadesc": (
                "Baixe STL gratis, descubra arquivos baratos e entre nos grupos "
                "do Clube 3D Brasil para testar modelos de impressao 3D."
            ),
        },
    }
    r = session.post(f"{api}/pages/{page_id}", json=payload, timeout=30)
    if r.status_code not in (200, 201):
        raise SystemExit(f"Falha ao atualizar hub: {r.status_code} {r.text[:300]}")

    link = r.json().get("link") or wp_url
    print(f"Hub atual {acao}: ID {page_id}")
    print(f"URL: {link}")
    if not os.environ.get("TELEGRAM_INVITE_URL"):
        print("Telegram: CTA publico nao exibido porque TELEGRAM_INVITE_URL nao esta configurado.")


if __name__ == "__main__":
    main()
