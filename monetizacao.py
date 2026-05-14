"""
monetizacao.py — Gerenciador de afiliados e blocos de anúncio.
"""

import random


class Monetizacao:

    def __init__(self, afiliados: list[dict]):
        """
        afiliados = [
            {"keyword": "impressora 3d", "nome": "...", "link": "..."},
        ]
        """
        self.afiliados = afiliados

    def escolher_produto(self, texto: str) -> dict | None:
        texto = texto.lower()
        # Prioriza match mais específico (keyword mais longa)
        candidatos = sorted(
            [a for a in self.afiliados if a["keyword"] in texto],
            key=lambda a: len(a["keyword"]),
            reverse=True,
        )
        return candidatos[0] if candidatos else None

    def bloco_topo(self, produto: dict) -> str:
        return f"""
<div style="background:#fff8e1;border:1px solid #ffcc02;border-radius:10px;padding:16px 20px;margin:20px 0;display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  <span style="font-size:2em;">🛒</span>
  <div style="flex:1;min-width:180px;">
    <strong style="display:block;font-size:1.05em;margin-bottom:4px;">Produto Recomendado</strong>
    <span style="color:#555;">{produto['nome']}</span>
  </div>
  <a href="{produto['link']}" target="_blank" rel="noopener sponsored"
     style="background:#ff9900;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:bold;white-space:nowrap;display:inline-block;">
    Ver na loja ↗
  </a>
</div>
"""

    def bloco_meio(self, produto: dict) -> str:
        return f"""
<div style="background:#f0f7ff;border-left:4px solid #0073aa;padding:12px 16px;margin:16px 0;border-radius:0 8px 8px 0;">
  <p style="margin:0;">👉 <strong>Recomendamos para este projeto:</strong>
    <a href="{produto['link']}" target="_blank" rel="noopener sponsored"
       style="color:#0073aa;font-weight:bold;">{produto['nome']}</a>
  </p>
</div>
"""

    def bloco_final(self, produto: dict) -> str:
        return f"""
<div style="background:#e8f4f8;border:2px solid #0073aa;border-radius:10px;padding:24px;margin:28px 0;text-align:center;">
  <h3 style="margin:0 0 8px;color:#0073aa;">🚀 Pronto para imprimir?</h3>
  <p style="margin:0 0 18px;color:#555;">Confira o equipamento recomendado pelo Clube 3D Brasil:</p>
  <strong style="display:block;margin-bottom:14px;font-size:1.05em;">{produto['nome']}</strong>
  <a href="{produto['link']}" target="_blank" rel="noopener sponsored"
     style="background:#0073aa;color:#fff;padding:13px 32px;border-radius:7px;text-decoration:none;font-weight:bold;display:inline-block;font-size:1em;">
    🛒 Comprar agora
  </a>
  <p style="margin:12px 0 0;font-size:0.8em;color:#888;">* Link de afiliado — ajuda a manter o blog gratuito</p>
</div>
"""

    def bloco_adsense(self) -> str:
        return """
<div style="text-align:center;margin:20px 0;">
<!-- Google AdSense — substitua pelo seu código -->
</div>
"""
