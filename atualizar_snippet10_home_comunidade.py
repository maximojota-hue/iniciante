"""
Atualiza o snippet 10 da home visual com o bloco:
STL gratis, arquivos baratos, grupos e vaquinhas.

Uso:
  python atualizar_snippet10_home_comunidade.py
"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

import requests


SNIPPET_ID = 10
WHATSAPP_STL = "https://chat.whatsapp.com/DnPdJcOuVcfCln1vAdgWwj"
WHATSAPP_PRINCIPAL = "https://chat.whatsapp.com/CVnLPEIcaIE3BeIk2lwDVZ"
WHATSAPP_GERAL = "https://chat.whatsapp.com/DEZxJq456FW7xACVxZvXod"


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def conectar() -> tuple[requests.Session, str]:
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
        "User-Agent": "Mozilla/5.0 Clube3DHomeSnippet/1.0",
    })
    return session, wp_url


COMMUNITY_CSS = r"""
      .c3d-community-bridge {
        margin: clamp(1.25rem, 3vw, 2.2rem) auto;
        width: min(1180px, calc(100% - 2rem));
        border: 1px solid var(--border-hi);
        border-radius: 8px;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(251,191,36,.15), rgba(7,8,15,.96) 44%), #080a12;
        box-shadow: 0 26px 70px rgba(0,0,0,.28);
      }
      .c3d-community-bridge-top {
        padding: clamp(1.4rem, 3vw, 2.3rem);
      }
      .c3d-community-bridge-kicker {
        display: inline-flex;
        width: fit-content;
        margin-bottom: .9rem;
        padding: .45rem .65rem;
        border-radius: 3px;
        background: var(--trending);
        color: #000;
        font-family: var(--font-mono);
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
      }
      .c3d-community-bridge h2 {
        max-width: 820px;
        margin: 0 0 .85rem;
        color: var(--text-bright);
        font-size: clamp(1.95rem, 4.2vw, 4rem);
        line-height: .95;
      }
      .c3d-community-bridge p {
        max-width: 760px;
        margin: 0 0 1.35rem;
        color: var(--text-dim);
        font-size: clamp(1rem, 1.4vw, 1.12rem);
        line-height: 1.65;
      }
      .c3d-community-actions {
        display: flex;
        flex-wrap: wrap;
        gap: .8rem;
      }
      .c3d-community-btn {
        display: inline-flex;
        min-height: 44px;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--border-hi);
        border-radius: 4px;
        padding: .82rem 1rem;
        color: var(--text-bright);
        background: rgba(255,255,255,.08);
        font-family: var(--font-mono);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .06em;
        text-transform: uppercase;
        text-decoration: none;
      }
      .c3d-community-btn-primary {
        color: #000;
        background: var(--trending);
        border-color: var(--trending);
      }
      .c3d-community-points {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        border-top: 1px solid var(--border);
      }
      .c3d-community-point {
        padding: 1.15rem;
        border-right: 1px solid var(--border);
      }
      .c3d-community-point:last-child { border-right: 0; }
      .c3d-community-point strong {
        display: block;
        margin-bottom: .35rem;
        color: var(--text-bright);
        font-family: var(--font-display);
        font-size: 1.04rem;
      }
      .c3d-community-point span {
        display: block;
        color: var(--text-dim);
        font-size: .92rem;
        line-height: 1.45;
      }
"""


COMMUNITY_JS = f"""
        var quickForCommunity = document.querySelector('.quick-nav');
        if (quickForCommunity && !document.querySelector('.c3d-community-bridge')) {{
          var community = document.createElement('section');
          community.className = 'c3d-community-bridge reveal visible';
          community.setAttribute('aria-label', 'Bloco Whatsapp Stl');
          community.innerHTML =
            '<div class=\"c3d-community-bridge-top\">' +
              '<span class=\"c3d-community-bridge-kicker\">STL gratis + arquivos baratos</span>' +
              '<h2>Baixe arquivos gratis e entre nos grupos do Clube 3D Brasil</h2>' +
              '<p>Comece com modelos STL gratuitos, descubra arquivos pagos baratos para testar e participe das vaquinhas da comunidade para avaliar modelos premium sem gastar sozinho.</p>' +
              '<div class=\"c3d-community-actions\">' +
                '<a class=\"c3d-community-btn c3d-community-btn-primary\" href=\"{WHATSAPP_STL}\" target=\"_blank\" rel=\"noopener\">Grupo STL gratis</a>' +
                '<a class=\"c3d-community-btn\" href=\"{WHATSAPP_PRINCIPAL}\" target=\"_blank\" rel=\"noopener\">Grupo principal</a>' +
                '<a class=\"c3d-community-btn\" href=\"{WHATSAPP_GERAL}\" target=\"_blank\" rel=\"noopener\">Comunidade geral</a>' +
              '</div>' +
            '</div>' +
            '<div class=\"c3d-community-points\">' +
              '<div class=\"c3d-community-point\"><strong>STL gratis</strong><span>Personagens, games, decoracao, chaveiros e modelos faceis para iniciantes.</span></div>' +
              '<div class=\"c3d-community-point\"><strong>Arquivos baratos</strong><span>Achados pagos de baixo custo para imprimir, comparar e evitar compra ruim.</span></div>' +
              '<div class=\"c3d-community-point\"><strong>Vaquinhas</strong><span>Compra coletiva de arquivos premium quando a comunidade quer testar um modelo.</span></div>' +
              '<div class=\"c3d-community-point\"><strong>Testes reais</strong><span>Resultados, configuracoes, filamentos e alertas de makers brasileiros.</span></div>' +
            '</div>';
          var newsletterForCommunity = Array.from(document.querySelectorAll('section, div'))
            .find(function(el) {{ return /Entre para o maior hub/i.test(el.textContent || ''); }});
          if (newsletterForCommunity && newsletterForCommunity.parentNode) {{
            newsletterForCommunity.insertAdjacentElement('beforebegin', community);
          }} else if (quickForCommunity.parentNode) {{
            quickForCommunity.parentNode.appendChild(community);
          }}
        }}
"""


def aplicar_alteracoes(code: str) -> str:
    if ".c3d-community-bridge" not in code:
        marker_css = "      @media (max-width: 1100px) {"
        if marker_css not in code:
            raise RuntimeError("Marcador CSS nao encontrado no snippet 10.")
        code = code.replace(marker_css, COMMUNITY_CSS + "\n" + marker_css, 1)

    marker_js = "        setText('.ticker-label'"
    inicio_js = "        var quickForCommunity = document.querySelector('.quick-nav');"
    if marker_js not in code:
        raise RuntimeError("Marcador JS nao encontrado no snippet 10.")
    if inicio_js in code:
        pattern = re.compile(re.escape(inicio_js) + r".*?(?=" + re.escape(marker_js) + r")", re.S)
        code = pattern.sub(COMMUNITY_JS + "\n", code, count=1)
    else:
        code = code.replace(marker_js, COMMUNITY_JS + "\n" + marker_js, 1)

    if "@media (max-width: 700px) {" in code and ".c3d-community-points { grid-template-columns: 1fr; }" not in code:
        code = code.replace(
            "      @media (max-width: 700px) {",
            "      @media (max-width: 700px) {\n"
            "        .c3d-community-points { grid-template-columns: 1fr; }\n"
            "        .c3d-community-point { border-right: 0; border-bottom: 1px solid var(--border); }\n"
            "        .c3d-community-point:last-child { border-bottom: 0; }\n"
            "        .c3d-community-actions { display: grid; }\n",
            1,
        )
    return code


def main() -> None:
    session, wp_url = conectar()
    endpoint = f"{wp_url}/wp-json/code-snippets/v1/snippets/{SNIPPET_ID}"
    response = session.get(endpoint, timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"Falha ao ler snippet {SNIPPET_ID}: {response.status_code} {response.text[:200]}")

    snippet = response.json()
    original = snippet.get("code", "")
    updated = aplicar_alteracoes(original)
    if updated == original:
        print("Snippet 10 ja estava atualizado.")
        return

    payload = {
        "name": snippet.get("name"),
        "desc": snippet.get("desc", ""),
        "code": updated,
        "tags": snippet.get("tags", []),
        "scope": snippet.get("scope", "front-end"),
        "active": snippet.get("active", True),
        "priority": snippet.get("priority", 20),
    }
    save = session.post(endpoint, json=payload, timeout=30)
    if save.status_code not in (200, 201):
        raise SystemExit(f"Falha ao salvar snippet {SNIPPET_ID}: {save.status_code} {save.text[:300]}")
    print(f"Snippet {SNIPPET_ID} atualizado com bloco de comunidade/STL.")


if __name__ == "__main__":
    main()
