"""
corrigir_adsense_compliance.py
Corrige bloqueadores criticos e problemas altos para aprovacao Google AdSense.

Correcoes aplicadas:
  1. [CRITICO] Post ChatGPT fora do nicho → mover para rascunho
  2. [CRITICO] /blog-2/ ainda indexada → deletar pagina
  3. [CRITICO] Post espanhol (18M) → corrigir texto + disclaimer
  4. [CRITICO] Claims de renda excessivas → suavizar linguagem
  5. [ALTO]    Duplicidade ganhar dinheiro → canonical no mais fraco
  6. [ALTO]    Meta descriptions ausentes → preencher em todos os posts
  7. [ALTO]    Disclaimer PI nos posts de personagens → injetar aviso
  8. [MEDIO]   Titulo homepage duplicado → corrigir no Yoast
  9. [MEDIO]   "voce" sem acento no H1 → corrigir

Execute: python corrigir_adsense_compliance.py
"""

import sys
import json
import base64
import time
import re
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WP_URL = "https://clube3dbrasil.com"
ENV_FILE = Path(".env")

# Posts de personagens com PI protegida (Nintendo, Supercell, etc.)
SLUGS_PERSONAGENS_PI = {
    "bowser", "bowser-2", "pekka", "guerreiro-barbaro", "anjo-curador",
    "valquiria-guerreira", "corredor-de-porcos", "quebrador-de-muros-esqueleto",
    "pokebola", "chaveiro-mew", "draco-malfoy", "dragonite",
    "figura-dragonite-impressa-3d-pokemon", "figure-draco-malfoy-impressa-3d-amigurumi",
    "figure-knuckles-superman-impressa-3d", "figure-sonic-flash-impressa-3d",
    "modelo-3d-da-hello-kitty", "flexi-mini-corgi", "flexi-ippo",
    "cranix-clicker-de-fidget-de-cranio-divertido", "mago", "golem-de-pedra",
    "gigante", "morcego-articulado", "anquilossauro-articulado",
    "figura-sonic-flash-impressa-3d", "piu-piu-sem-ams",
    "figure-dragonite-impressa-3d-pokemon", "figure-gamer-impressa-3d-mario-aquaman",
    "figure-wolverine-impressa-3d-estilo-amigurumi", "figure-gamer-impressa-3d-mario-final-fantasy",
    "figure-geek-impressa-3d-mickey-rock", "figure-popeye-impressa-3d-urban-vibes",
    "porta-pipoca-bowser-jr-impressa-3d",
}

DISCLAIMER_PI = (
    '\n<div style="background:#fff3cd;border-left:4px solid #ffc107;padding:12px 16px;'
    'margin:20px 0;font-size:0.9em;">'
    '<strong>⚠️ Aviso de Direitos Autorais:</strong> Este personagem é propriedade intelectual '
    'de seu respectivo detentor de direitos. O modelo STL compartilhado é de uso estritamente '
    'pessoal e não-comercial. Verifique a licença do arquivo original antes de qualquer uso. '
    'O Clube 3D Brasil não possui afiliação com as marcas mencionadas.'
    '</div>\n'
)

META_EDITORIALS = {
    "segredos-empresa-fatura-18m-impressao-3d": (
        "Descubra as estratégias reais de uma empresa de impressão 3D que escala com produtos "
        "criativos. Análise prática para makers brasileiros."
    ),
    "como-ganhar-dinheiro-impressora-3d": (
        "Aprenda como monetizar sua impressora 3D vendendo peças, prestando serviços e criando "
        "produtos. Guia prático com exemplos reais."
    ),
    "como-ganhar-dinheiro-com-impressao-3d": (
        "Guia completo para gerar renda com impressão 3D: modelos de negócio, produtos mais "
        "vendidos e como precificar corretamente."
    ),
    "10-produtos-lucrativos-para-imprimir-em-3d-e-vender": (
        "Lista com os 10 produtos mais procurados para imprimir em 3D e vender. Dicas de "
        "precificação e onde vender online."
    ),
    "quanto-cobrar-revisao-produtos-3d": (
        "Como precificar produtos impressos em 3D: cálculo de custo de filamento, energia, "
        "tempo e margem de lucro sustentável."
    ),
    "tendencias-impressao-3d-2026": (
        "As principais tendências da impressão 3D para 2026: novos materiais, impressoras "
        "acessíveis e oportunidades de mercado."
    ),
    "impressao-3d-sustentavel": (
        "Impressão 3D sustentável: como escolher filamentos ecológicos, reduzir desperdício "
        "e adotar práticas responsáveis."
    ),
    "top-10-modelos-3d-impressao-3d": (
        "Os 10 modelos 3D mais baixados e impressos em 2026. Selecione os melhores STL "
        "gratuitos para sua impressora."
    ),
}


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


def criar_sessao(user: str, senha: str) -> requests.Session:
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "User-Agent": "Clube3DBrasil-AdSense-Fix/1.0",
    })
    return s


def buscar_todos_posts(session: requests.Session, api: str) -> list[dict]:
    posts = []
    page = 1
    while True:
        r = session.get(f"{api}/posts", params={
            "per_page": 100, "page": page,
            "status": "publish,draft",
            "_fields": "id,slug,title,content,meta,categories,status",
        }, timeout=30)
        if not r.ok:
            break
        lote = r.json()
        if not lote:
            break
        posts.extend(lote)
        total = int(r.headers.get("X-WP-TotalPages", 1))
        print(f"  📄 Página {page}/{total} — {len(lote)} posts")
        if page >= total:
            break
        page += 1
        time.sleep(0.3)
    return posts


def buscar_por_slug(session: requests.Session, api: str, slug: str,
                    tipo: str = "posts") -> dict | None:
    r = session.get(f"{api}/{tipo}", params={"slug": slug, "status": "any"}, timeout=15)
    if r.ok and r.json():
        return r.json()[0]
    return None


def gerar_meta_desc(titulo: str, slug: str = "") -> str:
    titulo = re.sub(r"<[^>]+>", "", titulo).strip()
    titulo = titulo.replace(" STL para Impressão 3D", "").replace("Modelo 3D ", "").strip(" —-")
    if any(w in slug for w in ("figura", "figure", "model", "stl", "flexi", "chaveiro",
                               "porta-pipoca", "luminaria", "escultura", "cranix",
                               "bowser", "pekka", "guerreiro", "anjo", "valquiria",
                               "pokebola", "mew", "draco", "dragonite", "hello-kitty",
                               "corgi", "ippo", "piu-piu", "mago", "golem", "gigante",
                               "morcego", "anquilossauro", "sonic", "knuckles", "popeye",
                               "wolverine", "mickey", "geek", "gamer")):
        desc = f"Baixe o modelo STL de {titulo} gratuitamente. Impressão 3D fácil em casa — Clube 3D Brasil."
    else:
        desc = f"{titulo} — guia prático para makers brasileiros. Dicas, tutoriais e recursos no Clube 3D Brasil."
    return desc[:155]


def corrigir_claims_renda(content: str) -> tuple[str, int]:
    """Suaviza afirmações de ganho irreais que violam política AdSense."""
    substituicoes = [
        # Claims exatas de R$ 240/dia
        (r"ganhos de até R\$\s*240\s*diári[ao]s", "possibilidade de geração de renda"),
        (r"R\$\s*240\s*diári[ao]s", "renda variável conforme dedicação e mercado"),
        (r"Vários usuários relatam ganhos de até R\$ 240", "Alguns usuários relatam resultados positivos"),
        (r"R\$\s*3[.,]000\s*e\s*R\$\s*4[.,]000\s*mensai[s]", "valores que variam amplamente por região e dedicação"),
        (r"pode gerar entre R\$\s*3[.,]000 e R\$\s*4[.,]000 mensai[s]",
         "pode gerar renda extra — os valores variam conforme dedicação, localidade e mercado"),
        (r"gerando R\$\s*3[.,]000\s*mensai[s]", "gerando renda extra mensal"),
        (r"margem que varia entre 150% a 300%", "margem variável conforme produto e mercado"),
        (r"trabalhe com margem de 250% a 400%", "trabalhe com margens sustentáveis para seu mercado"),
        (r"1,5 milhões de unidades", "grande volume de unidades"),
        (r"Funciona 100%\s*grátis", "Utiliza ferramentas gratuitas disponíveis"),
        (r"alguns usuários relatam ganhos em uma ou duas semanas",
         "os resultados variam e dependem de dedicação e contexto"),
    ]
    alteracoes = 0
    for padrao, substituto in substituicoes:
        novo, n = re.subn(padrao, substituto, content, flags=re.IGNORECASE)
        if n > 0:
            content = novo
            alteracoes += n
    return content, alteracoes


def remover_texto_espanhol(content: str) -> tuple[str, int]:
    """Remove ou substitui palavras em espanhol por equivalentes em PT-BR."""
    sub_espanhol = [
        (r"\bcuchillos\b", "facas"),
        (r"\bllaveritos\b", "chaveirinhos"),
        (r"\bmuñequitos\b", "bonecos"),
        (r"\bmuñecos\b", "bonecos"),
        (r"\bllaveros\b", "chaveiros"),
        (r"\bfigurinhas\b", "figuras"),
    ]
    alteracoes = 0
    for padrao, sub in sub_espanhol:
        novo, n = re.subn(padrao, sub, content, flags=re.IGNORECASE)
        if n > 0:
            content = novo
            alteracoes += n
    return content, alteracoes


def main():
    print("\n" + "=" * 65)
    print("  CORREÇÃO AdSense COMPLIANCE — clube3dbrasil.com")
    print("=" * 65 + "\n")

    env = carregar_env()
    user = env.get("WP_USER", "")
    senha = env.get("WP_PASS", "")
    if not user or not senha:
        print("❌ WP_USER/WP_PASS não encontrados no .env")
        return

    api = f"{WP_URL}/wp-json/wp/v2"
    session = criar_sessao(user, senha)

    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print(f"❌ Autenticação falhou: {r.status_code}")
        return
    print(f"✅ Conectado como: {r.json().get('name', '')} (ID {r.json().get('id', '')})\n")

    resultados = {"ok": 0, "erros": 0, "pulados": 0}

    # ────────────────────────────────────────────────────────────
    # 1. [CRÍTICO] Post ChatGPT fora do nicho → rascunho
    # ────────────────────────────────────────────────────────────
    print("─" * 65)
    print("1. [CRÍTICO] Movendo post ChatGPT para rascunho...")
    slug_chatgpt = "ganhe-dinheiro-chatgpt-gratuitamente-celular"
    post_chatgpt = buscar_por_slug(session, api, slug_chatgpt)
    if post_chatgpt:
        pid = post_chatgpt["id"]
        titulo_chatgpt = post_chatgpt.get("title", {}).get("rendered", "")
        r = session.post(f"{api}/posts/{pid}", json={"status": "draft"}, timeout=15)
        if r.ok:
            print(f"  ✅ [{pid}] '{titulo_chatgpt[:55]}' → rascunho")
            resultados["ok"] += 1
        else:
            print(f"  ❌ Erro {r.status_code}: {r.text[:100]}")
            resultados["erros"] += 1
    else:
        print(f"  ⚠️  Post '{slug_chatgpt}' não encontrado (pode já estar deletado)")
        resultados["pulados"] += 1

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 2. [CRÍTICO] /blog-2/ ainda indexada → deletar
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("2. [CRÍTICO] Localizando e deletando /blog-2/...")
    for tipo in ("posts", "pages"):
        item = buscar_por_slug(session, api, "blog-2", tipo)
        if item:
            pid = item["id"]
            status_atual = item.get("status", "?")
            r = session.delete(f"{api}/{tipo}/{pid}", params={"force": True}, timeout=15)
            if r.ok:
                print(f"  ✅ [{pid}] blog-2 ({tipo}, status={status_atual}) deletado permanentemente")
                resultados["ok"] += 1
            else:
                # Se nao puder deletar, pelo menos mover para rascunho
                r2 = session.post(f"{api}/{tipo}/{pid}", json={"status": "draft"}, timeout=15)
                if r2.ok:
                    print(f"  ⚠️  [{pid}] blog-2 movido para rascunho (deleção falhou: {r.status_code})")
                    resultados["ok"] += 1
                else:
                    print(f"  ❌ Não foi possível deletar nem rascunhar blog-2: {r.status_code}")
                    resultados["erros"] += 1
            break
    else:
        print("  ⚠️  /blog-2/ não encontrada como post nem página — pode ser URL de categoria/arquivo")
        resultados["pulados"] += 1

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 3. [CRÍTICO] Post espanhol (18M) → corrigir texto
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("3. [CRÍTICO] Corrigindo texto espanhol no post 18M...")
    slug_18m = "segredos-empresa-fatura-18m-impressao-3d"
    post_18m = buscar_por_slug(session, api, slug_18m)
    if post_18m:
        pid = post_18m["id"]
        content_atual = post_18m.get("content", {}).get("rendered", "")
        content_novo, n_es = remover_texto_espanhol(content_atual)
        content_novo, n_claims = corrigir_claims_renda(content_novo)
        total_fixes = n_es + n_claims
        if total_fixes > 0:
            r = session.post(f"{api}/posts/{pid}", json={"content": content_novo}, timeout=20)
            if r.ok:
                print(f"  ✅ [{pid}] {n_es} palavra(s) espanhol + {n_claims} claim(s) corrigidos")
                resultados["ok"] += 1
            else:
                print(f"  ❌ Erro {r.status_code}: {r.text[:100]}")
                resultados["erros"] += 1
        else:
            print(f"  ⚠️  Nenhuma correção automática possível — revisar manualmente")
            resultados["pulados"] += 1
    else:
        print(f"  ⚠️  Post '{slug_18m}' não encontrado")
        resultados["pulados"] += 1

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 4. [CRÍTICO] Claims de renda → suavizar
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("4. [CRÍTICO] Suavizando claims de renda em posts de monetização...")
    slugs_renda = [
        "como-ganhar-dinheiro-impressora-3d",
        "como-ganhar-dinheiro-com-impressao-3d",
        "quanto-cobrar-revisao-produtos-3d",
        "10-produtos-lucrativos-para-imprimir-em-3d-e-vender",
        "como-iniciar-fazenda-impressao-3d-zero",
        "segredos-empresa-fatura-18m-impressao-3d",
    ]
    for slug in slugs_renda:
        post = buscar_por_slug(session, api, slug)
        if not post:
            print(f"  ⚠️  '{slug}' não encontrado")
            continue
        pid = post["id"]
        content_atual = post.get("content", {}).get("rendered", "")
        content_novo, n = corrigir_claims_renda(content_atual)
        if n == 0:
            print(f"  ⏭️  [{pid}] sem claims detectadas: {slug[:45]}")
            resultados["pulados"] += 1
            continue
        r = session.post(f"{api}/posts/{pid}", json={"content": content_novo}, timeout=20)
        if r.ok:
            print(f"  ✅ [{pid}] {n} substituição(ões) — {slug[:45]}")
            resultados["ok"] += 1
        else:
            print(f"  ❌ [{pid}] Erro {r.status_code} — {slug[:45]}")
            resultados["erros"] += 1
        time.sleep(0.8)

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 5. [ALTO] Canonical no post duplicado mais fraco
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("5. [ALTO] Configurando canonical no post duplicado mais fraco...")
    # O post mais novo/fraco aponta canonical para o mais forte
    slug_fraco = "como-ganhar-dinheiro-com-impressao-3d"
    url_canonico = f"{WP_URL}/como-ganhar-dinheiro-impressora-3d/"
    post_fraco = buscar_por_slug(session, api, slug_fraco)
    if post_fraco:
        pid = post_fraco["id"]
        r = session.post(f"{api}/posts/{pid}", json={
            "meta": {"_yoast_wpseo_canonical": url_canonico}
        }, timeout=15)
        if r.ok:
            print(f"  ✅ [{pid}] canonical → {url_canonico}")
            resultados["ok"] += 1
        else:
            print(f"  ❌ Erro {r.status_code}: {r.text[:100]}")
            resultados["erros"] += 1
    else:
        print(f"  ⚠️  Post '{slug_fraco}' não encontrado")
        resultados["pulados"] += 1

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 6. [ALTO] Meta descriptions em todos os posts sem descrição
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("6. [ALTO] Preenchendo meta descriptions ausentes...")
    todos_posts = buscar_todos_posts(session, api)
    print(f"  Total: {len(todos_posts)} posts\n")

    sem_meta = [p for p in todos_posts
                if not p.get("meta", {}).get("_yoast_wpseo_metadesc", "").strip()]
    print(f"  Sem meta description: {len(sem_meta)} posts\n")

    for post in sem_meta:
        pid = post["id"]
        slug = post.get("slug", "")
        titulo = post.get("title", {}).get("rendered", "")

        # Usar descrição específica se disponível
        if slug in META_EDITORIALS:
            nova_meta = META_EDITORIALS[slug]
        else:
            nova_meta = gerar_meta_desc(titulo, slug)

        r = session.post(f"{api}/posts/{pid}", json={
            "meta": {"_yoast_wpseo_metadesc": nova_meta}
        }, timeout=15)
        if r.ok:
            print(f"  ✅ [{pid}] {titulo[:45]}")
            print(f"      → {nova_meta[:80]}")
            resultados["ok"] += 1
        else:
            print(f"  ❌ [{pid}] Erro {r.status_code}")
            resultados["erros"] += 1
        time.sleep(0.5)

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 7. [ALTO] Disclaimer PI nos posts de personagens
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("7. [ALTO] Injetando disclaimer de propriedade intelectual...")
    posts_personagens = [p for p in todos_posts if p.get("slug", "") in SLUGS_PERSONAGENS_PI]
    print(f"  Posts de personagens identificados: {len(posts_personagens)}\n")

    for post in posts_personagens:
        pid = post["id"]
        titulo = post.get("title", {}).get("rendered", "")
        content = post.get("content", {}).get("rendered", "")

        if "Aviso de Direitos Autorais" in content:
            print(f"  ⏭️  [{pid}] já tem disclaimer: {titulo[:45]}")
            resultados["pulados"] += 1
            continue

        novo_content = DISCLAIMER_PI + content
        r = session.post(f"{api}/posts/{pid}", json={"content": novo_content}, timeout=20)
        if r.ok:
            print(f"  ✅ [{pid}] disclaimer adicionado — {titulo[:45]}")
            resultados["ok"] += 1
        else:
            print(f"  ❌ [{pid}] Erro {r.status_code} — {titulo[:45]}")
            resultados["erros"] += 1
        time.sleep(0.7)

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 8. [MÉDIO] Corrigir "voce" sem acento no H1
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("8. [MÉDIO] Corrigindo 'voce' sem acento...")
    slug_guia = "unico-guia-iniciantes-impressao-3d"
    post_guia = buscar_por_slug(session, api, slug_guia)
    if post_guia:
        pid = post_guia["id"]
        titulo_atual = post_guia.get("title", {}).get("rendered", "")
        titulo_novo = titulo_atual.replace("voce", "você").replace("Voce", "Você")
        content_atual = post_guia.get("content", {}).get("rendered", "")
        content_novo = content_atual.replace(" voce ", " você ").replace(" Voce ", " Você ")
        payload = {}
        if titulo_novo != titulo_atual:
            payload["title"] = titulo_novo
        if content_novo != content_atual:
            payload["content"] = content_novo
        if payload:
            r = session.post(f"{api}/posts/{pid}", json=payload, timeout=15)
            if r.ok:
                print(f"  ✅ [{pid}] título/conteúdo corrigido")
                resultados["ok"] += 1
            else:
                print(f"  ❌ [{pid}] Erro {r.status_code}: {r.text[:100]}")
                resultados["erros"] += 1
        else:
            print(f"  ⏭️  Nenhuma ocorrência de 'voce' encontrada")
            resultados["pulados"] += 1
    else:
        print(f"  ⚠️  Post '{slug_guia}' não encontrado")
        resultados["pulados"] += 1

    time.sleep(1)

    # ────────────────────────────────────────────────────────────
    # 9. [MÉDIO] Corrigir título da homepage (duplicado)
    # ────────────────────────────────────────────────────────────
    print("\n─" * 2)
    print("9. [MÉDIO] Corrigindo título da homepage no Yoast...")
    # Busca a página com slug "home" ou ID da homepage
    r_home = session.get(f"{api}/pages", params={"slug": "home", "per_page": 5}, timeout=15)
    paginas_home = []
    if r_home.ok:
        paginas_home = r_home.json()

    if not paginas_home:
        # Tenta page_on_front via settings
        r_set = session.get(f"{WP_URL}/wp-json/wp/v2/settings", timeout=10)
        if r_set.ok:
            pid_home = r_set.json().get("page_on_front")
            if pid_home:
                r_pg = session.get(f"{api}/pages/{pid_home}", timeout=10)
                if r_pg.ok:
                    paginas_home = [r_pg.json()]

    if paginas_home:
        pid = paginas_home[0]["id"]
        r = session.post(f"{api}/pages/{pid}", json={
            "meta": {
                "_yoast_wpseo_title": "Clube 3D Brasil — Impressão 3D, Modelos STL e Dicas"
            }
        }, timeout=15)
        if r.ok:
            print(f"  ✅ [{pid}] Título Yoast da homepage corrigido (sem duplicação)")
            resultados["ok"] += 1
        else:
            print(f"  ❌ Erro {r.status_code}: {r.text[:120]}")
            print("     → Corrija manualmente: WP Admin > Yoast > Homepage > SEO Title")
            resultados["erros"] += 1
    else:
        print("  ⚠️  Homepage não localizada via API — corrigir manualmente no Yoast")
        resultados["pulados"] += 1

    # ────────────────────────────────────────────────────────────
    # RESUMO FINAL
    # ────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  RESUMO FINAL")
    print("=" * 65)
    print(f"  ✅ Correções aplicadas : {resultados['ok']}")
    print(f"  ⏭️  Pulados/já ok       : {resultados['pulados']}")
    print(f"  ❌ Erros               : {resultados['erros']}")
    print("=" * 65)
    print("""
  AÇÕES MANUAIS RESTANTES (não automatizáveis via API):
  ─────────────────────────────────────────────────────
  1. WP Admin > Configurações > Leitura → verificar se /blog-2/
     foi realmente removido do sitemap
  2. Yoast > Social > Facebook → confirmar og:type=article ativo
  3. Plugins > instalar "WP Cerber Security" ou "Login No Captcha"
     para proteger wp-login.php com CAPTCHA
  4. Google Search Console → solicitar re-crawl após as correções
  5. Revisar post /segredos-empresa-fatura-18m-impressao-3d/
     manualmente para confirmar que não restou espanhol
  6. Checar /robots.txt e adicionar: Disallow: /wp-admin/
     (via cPanel > File Manager > public_html/.htaccess)
""")


if __name__ == "__main__":
    main()
