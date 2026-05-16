"""
Gera um catalogo visual dos produtos afiliados cadastrados.

Fonte: CONTROLE_AFILIADOS.md
Saida: AFILIADOS_CADASTRADOS.html
"""

from __future__ import annotations

import html
import re
from pathlib import Path


SOURCE = Path("CONTROLE_AFILIADOS.md")
OUTPUT = Path("AFILIADOS_CADASTRADOS.html")


def parse_rows() -> list[dict[str, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "|---" in line or "| # " in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue
        number, name, link, image, status, notes = parts[:6]
        if not number.strip().isdigit():
            continue
        rows.append(
            {
                "number": number,
                "name": name,
                "link": strip_code(link),
                "image": strip_code(image),
                "status": status,
                "notes": notes,
            }
        )
    return rows


def strip_code(value: str) -> str:
    return value.strip().strip("`")


def image_src(path: str) -> str:
    if not path:
        return ""
    normalized = path.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", normalized):
        return "file:///" + normalized
    return normalized


def render_card(item: dict[str, str]) -> str:
    src = image_src(item["image"])
    img = (
        f'<img src="{html.escape(src)}" alt="{html.escape(item["name"])}">'
        if src
        else '<div class="no-image">Sem imagem</div>'
    )
    return f"""
      <article class="card">
        <div class="media">{img}</div>
        <div class="body">
          <div class="topline"><span class="id">#{html.escape(item["number"])}</span><span class="status">{html.escape(item["status"])}</span></div>
          <h2>{html.escape(item["name"])}</h2>
          <p>{html.escape(item["notes"])}</p>
          <a href="{html.escape(item["link"])}" target="_blank" rel="noopener noreferrer sponsored">Abrir link afiliado</a>
          <code>{html.escape(item["image"])}</code>
        </div>
      </article>
"""


def render(rows: list[dict[str, str]]) -> str:
    cards = "\n".join(render_card(row) for row in rows)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Afiliados Cadastrados - Clube 3D Brasil</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #070a0f;
      --panel: #111722;
      --line: #263244;
      --text: #eef4ff;
      --muted: #98a6bb;
      --accent: #36d65c;
      --blue: #00c8ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    header {{
      padding: 32px 24px 18px;
      border-bottom: 1px solid var(--line);
      background: #0b1018;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      letter-spacing: 0;
    }}
    header p {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }}
    main {{
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}
    .card {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      overflow: hidden;
      min-width: 0;
    }}
    .media {{
      height: 210px;
      background: #05070b;
      display: grid;
      place-items: center;
      border-bottom: 1px solid var(--line);
    }}
    .media img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      padding: 10px;
      background: #fff;
    }}
    .no-image {{
      color: var(--muted);
    }}
    .body {{
      padding: 16px;
    }}
    .topline {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }}
    .id {{
      color: var(--accent);
      font-weight: 800;
      font-size: 18px;
    }}
    .status {{
      color: var(--blue);
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 700;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 21px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    p {{
      color: var(--muted);
      line-height: 1.45;
      min-height: 60px;
      margin: 0 0 14px;
    }}
    a {{
      display: inline-flex;
      align-items: center;
      min-height: 38px;
      padding: 0 14px;
      border-radius: 6px;
      background: var(--accent);
      color: #041007;
      font-weight: 800;
      text-decoration: none;
    }}
    code {{
      display: block;
      margin-top: 14px;
      color: #a9b8cc;
      font-size: 11px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Afiliados Cadastrados</h1>
    <p>Clube 3D Brasil - {len(rows)} produto(s) registrados em CONTROLE_AFILIADOS.md</p>
  </header>
  <main>
{cards}
  </main>
</body>
</html>
"""


def main() -> None:
    rows = parse_rows()
    OUTPUT.write_text(render(rows), encoding="utf-8")
    print(f"Catalogo gerado: {OUTPUT.resolve()} ({len(rows)} afiliados)")


if __name__ == "__main__":
    main()
