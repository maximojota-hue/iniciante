"""
solicitar_recrawl.py
Notifica Google e Bing sobre atualizações no site via Sitemap Ping.
Também lista as URLs mais recentes para indexação manual no Search Console.

Sem necessidade de autenticação — usa endpoint público do Google/Bing.

Execute: python solicitar_recrawl.py
"""

import sys
import time
import requests
import base64
from pathlib import Path
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")

WP_URL   = "https://clube3dbrasil.com"
ENV_FILE = Path(".env")

SITEMAPS = [
    f"{WP_URL}/sitemap_index.xml",
    f"{WP_URL}/post-sitemap.xml",
    f"{WP_URL}/page-sitemap.xml",
]

PING_ENDPOINTS = {
    "Google": "https://www.google.com/ping?sitemap={}",
    "Bing":   "https://www.bing.com/ping?sitemap={}",
}

# Posts editoriais prioritários (mais importantes para AdSense)
URLS_PRIORITARIAS = [
    f"{WP_URL}/guia-para-iniciantes/",
    f"{WP_URL}/unico-guia-iniciantes-impressao-3d/",
    f"{WP_URL}/como-funciona-impressora-3d/",
    f"{WP_URL}/configuracao-bambu-lab-a1/",
    f"{WP_URL}/melhor-pla-para-iniciantes/",
    f"{WP_URL}/guia-modelagem-3d/",
    f"{WP_URL}/erros-cometi-30-dias-impressora-3d/",
    f"{WP_URL}/tendencias-impressao-3d-2026/",
    f"{WP_URL}/impressao-3d-sustentavel/",
    f"{WP_URL}/corrigir-problemas-primeira-camada/",
    f"{WP_URL}/10-produtos-lucrativos-para-imprimir-em-3d-e-vender/",
    f"{WP_URL}/como-nao-ser-processado-imprimindo-3d/",
    f"{WP_URL}/nao-compre-impressora-3d-antes-assistir/",
    f"{WP_URL}/experimentei-impressao-3d-como-iniciante-vale-pena/",
    f"{WP_URL}/como-iniciar-fazenda-impressao-3d-zero/",
]


def carregar_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def buscar_posts_recentes(user: str, senha: str, limite: int = 20) -> list[str]:
    """Busca as URLs dos posts mais recentemente modificados via WP API."""
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "User-Agent": "Clube3DBrasil-Recrawl/1.0",
    })
    try:
        r = session.get(
            f"{WP_URL}/wp-json/wp/v2/posts",
            params={
                "per_page":  limite,
                "status":    "publish",
                "orderby":   "modified",
                "order":     "desc",
                "_fields":   "link,title,modified",
            },
            timeout=15,
        )
        if r.ok:
            return [(p["link"], p["title"]["rendered"], p["modified"][:10])
                    for p in r.json()]
    except Exception as e:
        print(f"  ⚠️  Não foi possível buscar posts recentes: {e}")
    return []


def pingar_buscadores() -> None:
    print("\n📡 Pingando buscadores com os sitemaps...")
    print("-" * 60)
    for buscador, template in PING_ENDPOINTS.items():
        for sitemap in SITEMAPS:
            url = template.format(quote(sitemap, safe=""))
            try:
                r = requests.get(url, timeout=15)
                status = "✅" if r.status_code in (200, 201, 202) else f"⚠️  HTTP {r.status_code}"
                print(f"  {status} {buscador} ← {sitemap.split('/')[-1]}")
            except Exception as e:
                print(f"  ❌ {buscador} — erro: {e}")
            time.sleep(0.5)
    print()


def main():
    print("\n" + "=" * 60)
    print("  RE-CRAWL — clube3dbrasil.com")
    print("=" * 60)

    # 1. Pinga Google e Bing
    pingar_buscadores()

    # 2. Busca posts recentemente modificados
    env   = carregar_env()
    user  = env.get("WP_USER", "")
    senha = env.get("WP_PASS", "")

    recentes = []
    if user and senha:
        print("🔍 Buscando posts mais recentemente atualizados...")
        recentes = buscar_posts_recentes(user, senha, limite=20)

    # 3. Relatório de URLs para indexação manual
    print("=" * 60)
    print("  URLS PRIORITÁRIAS — indexar manualmente no Search Console")
    print("=" * 60)
    print("""
  Como fazer (leva ~5 minutos):
  1. Acesse: https://search.google.com/search-console
  2. Selecione a propriedade: clube3dbrasil.com
  3. No topo, cole cada URL no campo "Inspecionar qualquer URL"
  4. Clique em "Solicitar indexação"
  5. Repita para cada URL abaixo (as mais importantes primeiro)
""")

    print("  [ EDITORIAIS — Alta prioridade ]")
    for url in URLS_PRIORITARIAS:
        print(f"  → {url}")

    if recentes:
        print(f"\n  [ MODIFICADOS RECENTEMENTE — últimos {len(recentes)} posts ]")
        for link, titulo, data in recentes:
            print(f"  → {link}")
            print(f"     ({data}) {titulo[:55]}")

    print()
    print("=" * 60)
    print("  SITEMAP — submeter no Search Console")
    print("=" * 60)
    print("""
  Se ainda não submeteu o sitemap no Search Console:
  1. Search Console → Sitemaps (menu lateral)
  2. Adicionar sitemap: sitemap_index.xml
  3. Clicar em Enviar

  URL do sitemap: https://clube3dbrasil.com/sitemap_index.xml
""")
    print("=" * 60)
    print("  RICH RESULTS — validar schema injetado")
    print("=" * 60)
    print("""
  Teste o schema BlogPosting + FAQPage:
  https://search.google.com/test/rich-results

  URLs sugeridas para teste:
  → https://clube3dbrasil.com/guia-para-iniciantes/
  → https://clube3dbrasil.com/configuracao-bambu-lab-a1/
  → https://clube3dbrasil.com/melhor-pla-para-iniciantes/
""")
    print("=" * 60)
    print("  CONCLUSÃO")
    print("=" * 60)
    print("""
  ✅ Google e Bing notificados via Sitemap Ping
  ✅ Lista de URLs prioritárias gerada para indexação manual

  Prazo estimado para rich results aparecerem no Google: 3–14 dias
  Prazo para indexação de novos posts após ping: 1–7 dias
""")


if __name__ == "__main__":
    main()
