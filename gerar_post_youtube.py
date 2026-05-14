"""
gerar_post_youtube.py — Gera post SEO em portugues a partir de um link do YouTube.
Uso: python gerar_post_youtube.py <URL>
     python gerar_post_youtube.py  (modo interativo)
"""

import sys
import os
import re
import json
import subprocess
import unicodedata
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

import seo_writer
import publisher
from cluster import ClusterManager

sys.stdout.reconfigure(encoding="utf-8")


def extrair_metadados_yt(url: str) -> dict:
    """Retorna titulo e descricao do video via yt-dlp."""
    try:
        r = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True, text=True, timeout=30, encoding="utf-8"
        )
        if r.returncode == 0 and r.stdout:
            data = json.loads(r.stdout)
            return {
                "title":       data.get("title", ""),
                "description": (data.get("description") or "")[:500],
            }
    except Exception as e:
        print(f"  AVISO: nao foi possivel obter metadados: {e}")
    return {"title": "", "description": ""}


_STOPWORDS_LEVE = {
    "testei", "voce", "meu", "minha", "este", "essa", "isso",
    "what", "vs", "versus", "parte", "ep", "ep.",
    "review", "top", "best",
}


def titulo_para_keyword(titulo: str) -> str:
    """Converte titulo do YouTube em keyword SEO limpa em portugues natural."""
    titulo = re.split(r"[.?!|]", titulo)[0].strip()
    titulo = unicodedata.normalize("NFKD", titulo)
    titulo = titulo.encode("ascii", "ignore").decode("ascii")
    titulo = re.sub(r"[^\w\s]", " ", titulo)
    titulo = re.sub(r"\s+", " ", titulo).strip().lower()
    palavras = [p for p in titulo.split() if p not in _STOPWORDS_LEVE and len(p) > 1]
    keyword = " ".join(palavras)
    if len(keyword) > 55:
        keyword = keyword[:55].rsplit(" ", 1)[0]
    return keyword.strip()


def gerar_secondary_kws(keyword: str, titulo: str) -> list:
    """Gera keywords secundarias a partir do titulo."""
    palavras = [p for p in titulo.lower().split() if len(p) > 3]
    kws = []
    if len(palavras) >= 2:
        kws.append(" ".join(palavras[:3]))
    if len(palavras) >= 3:
        kws.append(" ".join(palavras[1:4]))
    kws.append(keyword + " tutorial")
    return list(dict.fromkeys(kws))[:3]


def carregar_config_wp() -> dict:
    cfg = {}
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip(); v = v.strip().strip('"').strip("'")
            if k == "WP_USER":   cfg["wp_user"] = v
            if k == "WP_PASS":   cfg["wp_app_password"] = v
            if k == "WP_URL":    cfg["wp_url"] = v
    if "wp_url" not in cfg:
        cfg["wp_url"] = "https://clube3dbrasil.com"
    cfg["wp_post_status"] = "draft"
    return cfg


def _verificar_e_publicar_pilar(cluster: ClusterManager, tema: str, pub) -> None:
    if cluster.total_posts(tema) < 3:
        return
    pilar = cluster.gerar_pilar(tema)
    if not pilar:
        return
    meta = f"Guia completo sobre {tema} na impressao 3D. Tutoriais, dicas e downloads."
    post_pilar = {
        "titulo":          pilar["titulo"],
        "slug":            pilar["slug"],
        "content":         pilar["conteudo"],
        "excerpt":         meta,
        "status":          "draft",
        "tags":            [tema, "impressao 3d", "guia completo"],
        "categories":      [tema],
        "yoast_keyphrase": f"impressao 3d {tema.lower()}",
        "yoast_title":     f"{tema} — Guia Completo | Clube 3D Brasil",
        "yoast_meta":      meta[:155],
    }
    try:
        result = pub.publicar_post(post_pilar)
        print(f"  Pilar [{tema}]: {result.get('url', result.get('wp_id', ''))}")
    except Exception as e:
        print(f"  Pilar [{tema}] erro: {e}")


def main():
    args = sys.argv[1:]

    renda_extra_flag = "--renda-extra" in args
    args = [a for a in args if a != "--renda-extra"]

    if args:
        youtube_url = args[0]
    else:
        youtube_url = input("\nURL do YouTube: ").strip()

    print("\n" + "=" * 60)
    print(f"URL: {youtube_url}")
    print("=" * 60)

    # Metadados do video
    print("\n[1/4] Obtendo titulo do video...")
    meta = extrair_metadados_yt(youtube_url)
    titulo_yt = meta["title"]

    if titulo_yt:
        print(f"  Titulo original: {titulo_yt}")
        titulo_yt = seo_writer.traduzir_titulo_para_pt(titulo_yt, log_fn=print)
        keyword = titulo_para_keyword(titulo_yt)
    else:
        print("  Titulo nao obtido — usando keyword generica.")
        keyword = "impressao 3d"

    secondary = gerar_secondary_kws(keyword, titulo_yt or keyword)
    print(f"  Keyword: {keyword}")
    print(f"  Secundarias: {secondary}")

    # Transcricao (qualquer idioma — Claude escreve em PT-BR)
    print("\n[2/4] Extraindo transcricao...")
    transcript = seo_writer.extrair_transcricao_yt(youtube_url, log_fn=print)
    if not transcript:
        print("  Sem transcricao — continuando so com keyword.")

    # Cluster SEO
    cluster = ClusterManager()
    tema = cluster.detectar_tema(keyword, titulo_yt or keyword)
    print(f"\n  Tema do cluster: {tema} ({cluster.total_posts(tema)} post(s) existentes)")

    # Gerar post PT-BR
    cfg = carregar_config_wp()
    pub = publisher.WordPressPublisher(cfg)

    print("\n[3/4] Gerando post PT-BR via Claude API...")
    try:
        post = seo_writer.gerar_post_seo(
            keyword=keyword,
            secondary_kws=secondary,
            transcript=transcript,
            youtube_url=youtube_url,
            yt_description=meta.get("description", ""),
            categoria="Renda Extra" if renda_extra_flag else "",
        )
        interlinks = cluster.gerar_html_interlinks(tema, excluir_url="")
        if interlinks:
            script_pos = post["content"].find('<script type="application/ld+json">')
            if script_pos >= 0:
                post["content"] = post["content"][:script_pos] + interlinks + "\n" + post["content"][script_pos:]
            else:
                post["content"] += interlinks
    except Exception as e:
        print(f"  ERRO: {e}")
        sys.exit(1)

    # Publicar
    print("\n[4/4] Publicando como draft no WordPress...")
    try:
        result = pub.publicar_post(post)
        wp_id = result["wp_id"]
        wp_url = result.get("url", "")
        print(f"  OK ID: {wp_id} — {wp_url}")
        cluster.adicionar_post(tema, {
            "titulo": post["titulo"],
            "url":    wp_url,
            "wp_id":  wp_id,
        })
        _verificar_e_publicar_pilar(cluster, tema, pub)
        _analisar_post(wp_id, cfg)
    except Exception as e:
        print(f"  Erro: {e}")

    print("\n[CONCLUIDO] Verifique os rascunhos no WP Admin.")
    print("=" * 60)


def _analisar_post(wp_id: int, cfg: dict):
    """Busca o post publicado e exibe analise de qualidade automatica."""
    import base64, requests as req
    try:
        token = base64.b64encode(f"{cfg['wp_user']}:{cfg['wp_app_password']}".encode()).decode()
        headers = {"Authorization": f"Basic {token}"}
        api = f"{cfg['wp_url'].rstrip('/')}/wp-json/wp/v2"
        r = req.get(f"{api}/posts/{wp_id}?context=edit", headers=headers, timeout=20)
        if not r.ok:
            return
        d = r.json()
        content  = d.get("content", {}).get("raw", "")
        focuskw  = d.get("meta", {}).get("_yoast_wpseo_focuskw", "")
        meta     = d.get("meta", {}).get("_yoast_wpseo_metadesc", "")
        titulo   = d.get("title", {}).get("raw", "")
        text     = re.sub(r"<[^>]+>", " ", content)
        text     = re.sub(r"\s+", " ", text).strip()
        words    = len(text.split())
        kw_count = text.lower().count(focuskw.lower()) if focuskw else 0
        has_faq  = "FAQPage" in content
        has_yt   = "wp-block-embed-youtube" in content
        af_match = re.search(r'href="(https?://[^"]+)"[^>]*>([^<]+)</a>', content)
        af_info  = f"{af_match.group(2)} | {af_match.group(1)}" if af_match else "nenhum"

        print(f"\n  Analise do post {wp_id}:")
        print(f"  Titulo   : {titulo[:65]}")
        print(f"  Keyword  : {focuskw}")
        print(f"  Meta     : {len(meta)} chars")
        print(f"  Palavras : {words} {'OK' if words >= 900 else 'abaixo de 900'}")
        print(f"  KW texto : {kw_count}x {'OK' if 2 <= kw_count <= 5 else 'ideal 3-4x'}")
        print(f"  Embed YT : {'sim' if has_yt else 'nao'}")
        print(f"  FAQ schema: {'sim' if has_faq else 'nao'}")
        print(f"  Afiliado : {af_info[:70]}")
    except Exception as e:
        print(f"  Analise nao disponivel: {e}")


if __name__ == "__main__":
    main()
