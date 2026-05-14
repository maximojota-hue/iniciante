"""
corrigir_seo_admin.py — Corrige 3 problemas SEO via WP REST API:
  2. H1 homepage: muda de "latest posts" para página estática
  3. Categoria "Impressao 3D" → "Impressão 3D" (com acento)
  4. Página blog-2: adiciona noindex via Yoast

Execução: python corrigir_seo_admin.py
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


def conectar(config: dict) -> tuple[requests.Session, str]:
    wp_url = config["wp_url"].rstrip("/")
    user   = os.environ.get("WP_USER", "")
    senha  = os.environ.get("WP_PASS", "")
    if not user or not senha:
        raise SystemExit("❌ WP_USER / WP_PASS não encontrados no .env")
    api   = f"{wp_url}/wp-json/wp/v2"
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type":  "application/json",
    })
    r = session.get(f"{api}/users/me", timeout=20)
    if r.status_code != 200:
        raise SystemExit(f"❌ Falha na autenticação: {r.status_code} — {r.text[:120]}")
    print(f"✅ Conectado como: {r.json().get('name', '')}\n")
    return session, api


# ─────────────────────────────────────────────────────────────
# TAREFA 2: Homepage estática
# ─────────────────────────────────────────────────────────────

HOME_HTML = """<p>Bem-vindo ao <strong>Clube 3D Brasil</strong> — o maior portal de modelos STL gratuitos do Brasil!</p>

<p>Aqui você encontra modelos 3D prontos para imprimir em casa: figuras, chaveiros, vasos, luminárias, peças decorativas e muito mais. Tudo testado e aprovado pela nossa comunidade de makers.</p>

<h2>Explore nossos modelos</h2>
<ul>
  <li>Figuras e colecionáveis para impressão 3D</li>
  <li>Acessórios e utensílios domésticos</li>
  <li>Peças para cosplay e games</li>
  <li>Modelos educacionais e funcionais</li>
</ul>

<p>Use o menu acima para navegar pelas categorias ou veja os posts mais recentes abaixo.</p>"""


def corrigir_homepage(session: requests.Session, api: str, wp_url: str):
    print("=" * 55)
    print("TAREFA 2: Corrigir H1 da homepage (página estática)")
    print("=" * 55)

    # 1. Verificar configuração atual
    r = session.get(f"{api.replace('/wp/v2', '')}/wp-site-health/v1/tests/page-cache", timeout=20)
    r_cfg = session.get(f"{api}/settings", timeout=20)

    if r_cfg.status_code != 200:
        print(f"⚠️  Sem acesso à API de settings (status {r_cfg.status_code}).")
        print("   Acesse WP Admin → Configurações → Leitura → marque 'Uma página estática'")
        print("   e selecione uma página como Página inicial.\n")
        return

    cfg = r_cfg.json()
    show_on_front = cfg.get("show_on_front", "posts")
    page_on_front = cfg.get("page_on_front", 0)

    if show_on_front == "page" and page_on_front:
        print(f"✅ Homepage já está configurada como página estática (ID {page_on_front}). Nada a fazer.\n")
        return

    print(f"   Configuração atual: show_on_front='{show_on_front}' — vou criar/localizar página Home.\n")

    # 2. Procurar página existente com slug home/inicio
    candidatos = []
    for slug in ("home", "inicio", "pagina-inicial", "principal"):
        r = session.get(f"{api}/pages", params={"slug": slug, "per_page": 1}, timeout=20)
        if r.status_code == 200 and r.json():
            p = r.json()[0]
            candidatos.append(p)
            print(f"   Página encontrada: ID={p['id']}  slug='{p['slug']}'  título='{p['title']['rendered']}'")
            break

    if not candidatos:
        # 3. Criar nova página Home
        print("   Nenhuma página Home encontrada. Criando...")
        payload = {
            "title":   "Home",
            "slug":    "home",
            "content": HOME_HTML,
            "status":  "publish",
            "meta": {
                "_yoast_wpseo_title":    "Clube 3D Brasil — Modelos STL Gratuitos para Impressão 3D",
                "_yoast_wpseo_metadesc": "Baixe modelos STL gratuitos para impressão 3D. Figuras, chaveiros, vasos e muito mais. Clube 3D Brasil — comunidade makers.",
            },
        }
        r = session.post(f"{api}/pages", json=payload, timeout=30)
        if r.status_code not in (200, 201):
            print(f"❌ Falha ao criar página: {r.status_code} — {r.text[:120]}\n")
            return
        pagina_id = r.json()["id"]
        print(f"   ✅ Página Home criada com ID={pagina_id}")
    else:
        pagina_id = candidatos[0]["id"]

    # 4. Definir como front page
    r = session.post(f"{api}/settings", json={
        "show_on_front": "page",
        "page_on_front": pagina_id,
    }, timeout=20)

    if r.status_code == 200:
        print(f"✅ Homepage configurada como página estática (ID {pagina_id}).\n")
    else:
        print(f"❌ Falha ao salvar setting: {r.status_code} — {r.text[:200]}")
        print("   Acesse WP Admin → Configurações → Leitura → selecione a página manualmente.\n")


# ─────────────────────────────────────────────────────────────
# TAREFA 3: Renomear categoria
# ─────────────────────────────────────────────────────────────

def corrigir_categoria(session: requests.Session, api: str):
    print("=" * 55)
    print("TAREFA 3: Renomear 'Impressao 3D' → 'Impressão 3D'")
    print("=" * 55)

    encontradas = []
    page = 1
    while True:
        r = session.get(f"{api}/categories", params={"per_page": 100, "page": page}, timeout=20)
        if r.status_code != 200 or not r.json():
            break
        for cat in r.json():
            nome = cat.get("name", "")
            # Captura nomes sem acento (Impressao, impressao, IMPRESSAO)
            if "mpressao" in nome and "3D" in nome.upper() and "ã" not in nome:
                encontradas.append(cat)
        page += 1

    if not encontradas:
        print("✅ Nenhuma categoria sem acento encontrada. Verificando se já existe 'Impressão 3D'...")
        r = session.get(f"{api}/categories", params={"search": "Impressão 3D"}, timeout=20)
        if r.status_code == 200 and r.json():
            print(f"✅ Categoria 'Impressão 3D' já existe (ID {r.json()[0]['id']}). Nada a fazer.\n")
        else:
            print("   Categoria não encontrada — verifique manualmente no WP Admin.\n")
        return

    for cat in encontradas:
        cat_id = cat["id"]
        nome_atual = cat["name"]
        slug_atual = cat["slug"]
        print(f"   Encontrada: ID={cat_id}  nome='{nome_atual}'  slug='{slug_atual}'")

        r = session.post(f"{api}/categories/{cat_id}", json={
            "name": "Impressão 3D",
            "slug": "impressao-3d",
        }, timeout=20)

        if r.status_code == 200:
            novo = r.json()
            print(f"   ✅ Renomeada para '{novo['name']}'  slug='{novo['slug']}'\n")
        else:
            print(f"   ❌ Erro {r.status_code}: {r.text[:120]}\n")


# ─────────────────────────────────────────────────────────────
# TAREFA 4: Noindex em blog-2
# ─────────────────────────────────────────────────────────────

def corrigir_blog2(session: requests.Session, api: str):
    print("=" * 55)
    print("TAREFA 4: Noindex/excluir página 'blog-2'")
    print("=" * 55)

    # Procurar tanto em pages quanto em posts (pode ser qualquer tipo)
    candidatos = []
    for endpoint in ("pages", "posts"):
        for slug in ("blog-2", "blog"):
            r = session.get(f"{api}/{endpoint}", params={"slug": slug, "status": "any", "per_page": 5}, timeout=20)
            if r.status_code == 200:
                for item in r.json():
                    if item["slug"] in ("blog-2", "blog") and item not in candidatos:
                        candidatos.append((endpoint, item))

    if not candidatos:
        print("   Página 'blog-2' não encontrada via API (pode ter sido deletada ou tem outro slug).")
        print("   Verifique em WP Admin → Páginas → e procure por 'blog'.\n")
        return

    for endpoint, item in candidatos:
        item_id   = item["id"]
        item_slug = item["slug"]
        titulo    = item.get("title", {}).get("rendered", "")
        status    = item.get("status", "")
        print(f"   Encontrado em /{endpoint}: ID={item_id}  slug='{item_slug}'  status='{status}'  título='{titulo}'")

        if item_slug == "blog-2":
            # Aplica noindex via Yoast e muda para draft
            r = session.post(f"{api}/{endpoint}/{item_id}", json={
                "status": "draft",
                "meta": {
                    "_yoast_wpseo_meta-robots-noindex": "1",
                    "_yoast_wpseo_meta-robots-nofollow": "1",
                },
            }, timeout=20)
            if r.status_code == 200:
                print(f"   ✅ Página '{item_slug}' movida para rascunho + noindex/nofollow aplicado.\n")
            else:
                print(f"   ❌ Erro {r.status_code}: {r.text[:120]}\n")
        else:
            print(f"   ℹ️  Slug '{item_slug}' não é exatamente 'blog-2' — ignorando.\n")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    carregar_env()

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    session, api = conectar(config)
    wp_url = config["wp_url"].rstrip("/")

    corrigir_homepage(session, api, wp_url)
    corrigir_categoria(session, api)
    corrigir_blog2(session, api)

    print("=" * 55)
    print("Concluído. Verifique o blog e limpe o cache do WordPress.")
    print("=" * 55)


if __name__ == "__main__":
    main()
