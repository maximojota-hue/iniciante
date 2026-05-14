"""
corrigir_eeat.py — Corrige E-E-A-T: página Sobre, Contato e perfil do autor.
Execução única: python corrigir_eeat.py
"""

import base64
import json
import os
import requests
from pathlib import Path


def carregar_env():
    env = Path(".env")
    if not env.exists():
        return
    for linha in env.read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.startswith("#"):
            k, _, v = linha.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


SOBRE_HTML = """
<h2>Quem somos</h2>
<p>O <strong>Clube 3D Brasil</strong> nasceu em 2020 com uma missão clara: mostrar que a impressão 3D é acessível, divertida e pode gerar renda extra para qualquer pessoa.</p>

<p>Compartilhamos modelos STL gratuitos, tutoriais e dicas práticas para makers de todo o Brasil. Aqui você encontra figures, chaveiros, vasos, luminárias, peças de crochê 3D e muito mais — tudo testado e impresso por nós antes de ser publicado.</p>

<h2>Como trabalhamos</h2>
<p>Imprimimos em casa, aqui no <strong>Rio de Janeiro, RJ</strong>, usando <strong>Bambu Lab A1</strong> e <strong>Bambu Lab P1S</strong> — duas das impressoras mais rápidas e precisas do mercado. Cada modelo publicado no blog passou por testes reais de impressão.</p>

<h2>Por que criamos o Clube 3D Brasil?</h2>
<p>Queríamos um espaço em português onde qualquer pessoa pudesse descobrir modelos gratuitos, aprender a imprimir e até começar um negócio com impressão 3D. Nos nossos grupos de WhatsApp, já ajudamos centenas de makers a dar os primeiros passos — e muitos já faturam vendendo peças impressas em casa.</p>

<h2>O que você encontra aqui</h2>
<ul>
  <li>Modelos STL gratuitos: figures, chaveiros, vasos, luminárias e muito mais</li>
  <li>Tutoriais de impressão 3D para iniciantes e avançados</li>
  <li>Dicas de configuração, material e fatiadores (Cura, Bambu Studio, PrusaSlicer)</li>
  <li>Comunidade ativa no WhatsApp com makers de todo o Brasil</li>
</ul>

<h2>Fale conosco</h2>
<p>Entre em contato pelo e-mail <a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a> ou pelo telefone <strong>(21) 2209-4593</strong> — Rio de Janeiro, RJ.</p>
<p>Também temos grupos ativos no WhatsApp. <a href="https://chat.whatsapp.com/CVnLPEIcaIE3BeIk2lwDVZ" target="_blank" rel="noopener">Clique aqui para participar da comunidade.</a></p>
"""

CONTATO_HTML = """
<h2>Entre em contato</h2>
<p>Tem dúvidas, sugestões ou quer fazer uma parceria? Estamos aqui para ajudar!</p>

<h2>📧 E-mail</h2>
<p><a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a><br>
Respondemos em até 2 dias úteis.</p>

<h2>📞 Telefone</h2>
<p><strong>(21) 2209-4593</strong> — Rio de Janeiro, RJ</p>

<h2>💬 Comunidade no WhatsApp</h2>
<ul>
  <li><a href="https://chat.whatsapp.com/CVnLPEIcaIE3BeIk2lwDVZ" target="_blank" rel="noopener">Grupo principal — Clube 3D Brasil</a></li>
  <li><a href="https://chat.whatsapp.com/DnPdJcOuVcfCln1vAdgWwj" target="_blank" rel="noopener">Grupo STL Gratuitos</a></li>
  <li><a href="https://chat.whatsapp.com/DEZxJq456FW7xACVxZvXod" target="_blank" rel="noopener">Comunidade Geral</a></li>
</ul>

<h2>🤝 Parcerias</h2>
<p>Se você é loja, marca de filamento ou criador de modelos 3D e quer fazer parceria, mande um e-mail para <a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a> com o assunto <strong>"Parceria"</strong>.</p>

<h2>📩 Envio de modelos</h2>
<p>Quer que publicamos seu modelo no blog? Envie o link do arquivo e uma descrição para o nosso e-mail. Avaliamos todos os envios.</p>
"""

BIO_AUTOR = (
    "Maker e entusiasta de impressão 3D desde 2020. "
    "Fundador do Clube 3D Brasil — comunidade dedicada a popularizar a impressão 3D e ajudar makers a gerar renda extra. "
    "Imprimo em casa, no Rio de Janeiro, com Bambu Lab A1 e Bambu Lab P1S. "
    "Compartilho modelos STL gratuitos, tutoriais e dicas práticas para makers de todo o Brasil."
)


def main():
    carregar_env()

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    wp_url = config["wp_url"].rstrip("/")
    user   = os.environ.get("WP_USER", "")
    senha  = os.environ.get("WP_PASS", "")

    if not user or not senha:
        print("❌ Credenciais não encontradas no .env")
        return

    api = f"{wp_url}/wp-json/wp/v2"
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    r = session.get(f"{api}/users/me")
    if r.status_code != 200:
        print(f"❌ Falha na autenticação: {r.status_code}")
        return
    usuario = r.json()
    print(f"✅ Conectado como: {usuario.get('name', '')} (ID {usuario.get('id', '')})\n")

    erros = 0

    # ── 1. Página Sobre Nós ──────────────────────────────────
    print("📄 Buscando página Sobre Nós...")
    r = session.get(f"{api}/pages", params={"slug": "sobre-nos", "per_page": 5})
    paginas = r.json()

    if not paginas:
        print("  ⚠️  Página 'sobre-nos' não encontrada pelo slug. Tentando busca geral...")
        r = session.get(f"{api}/pages", params={"per_page": 100})
        todos = r.json()
        paginas = [p for p in todos if "sobre" in p.get("slug", "").lower()]

    if paginas:
        pid = paginas[0]["id"]
        r = session.post(f"{api}/pages/{pid}", json={
            "content": SOBRE_HTML,
            "title":   "Sobre o Clube 3D Brasil",
        })
        if r.status_code in (200, 201):
            print(f"  ✅ Sobre Nós atualizada (ID {pid})")
        else:
            erros += 1
            print(f"  ❌ Erro {r.status_code}: {r.text[:120]}")
    else:
        erros += 1
        print("  ❌ Página Sobre Nós não encontrada")

    # ── 2. Página Contato ────────────────────────────────────
    print("\n📄 Buscando página Contato...")
    r = session.get(f"{api}/pages", params={"slug": "contato", "per_page": 5})
    paginas = r.json()

    if paginas:
        pid = paginas[0]["id"]
        r = session.post(f"{api}/pages/{pid}", json={
            "content": CONTATO_HTML,
            "title":   "Contato — Clube 3D Brasil",
        })
        if r.status_code in (200, 201):
            print(f"  ✅ Contato atualizada (ID {pid})")
        else:
            erros += 1
            print(f"  ❌ Erro {r.status_code}: {r.text[:120]}")
    else:
        erros += 1
        print("  ❌ Página Contato não encontrada")

    # ── 3. Perfil do autor (admin) ───────────────────────────
    print("\n👤 Atualizando perfil do autor...")
    uid = usuario.get("id")
    r = session.post(f"{api}/users/{uid}", json={
        "name":        "Clube 3D",
        "first_name":  "Clube 3D",
        "last_name":   "Brasil",
        "description": BIO_AUTOR,
        "url":         "https://clube3dbrasil.com",
    })
    if r.status_code in (200, 201):
        print(f"  ✅ Perfil atualizado (ID {uid})")
        print(f"     Nome : Clube 3D")
        print(f"     Bio  : {BIO_AUTOR[:80]}...")
    else:
        erros += 1
        print(f"  ❌ Erro {r.status_code}: {r.text[:120]}")

    print(f"""
{'=' * 50}
{'✅ Todas as correções aplicadas!' if erros == 0 else f'⚠️  Concluído com {erros} erro(s)'}
{'=' * 50}
Verifique:
  → https://clube3dbrasil.com/sobre-nos/
  → https://clube3dbrasil.com/contato/
  → https://clube3dbrasil.com/author/admin/
""")


if __name__ == "__main__":
    main()
