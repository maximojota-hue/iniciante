"""
atualizar_interlinks.py — Atualiza posts existentes com interlinks do cluster SEO.
Uso: python atualizar_interlinks.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

from cluster import ClusterManager
import publisher

sys.stdout.reconfigure(encoding="utf-8")


def carregar_config() -> dict:
    cfg = {}
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip(); v = v.strip().strip('"').strip("'")
            if k == "WP_USER":  cfg["wp_user"] = v
            if k == "WP_PASS":  cfg["wp_app_password"] = v
            if k == "WP_URL":   cfg["wp_url"] = v
    if "wp_url" not in cfg:
        cfg["wp_url"] = "https://clube3dbrasil.com"
    return cfg


def buscar_todos_posts(pub) -> list[dict]:
    todos = []
    page = 1
    while True:
        posts = pub._request(
            "GET",
            f"posts?per_page=100&page={page}&status=publish,draft&context=edit",
        )
        if not posts or not isinstance(posts, list):
            break
        todos.extend(posts)
        if len(posts) < 100:
            break
        page += 1
    return todos


def main():
    cfg = carregar_config()
    pub = publisher.WordPressPublisher(cfg)
    cluster = ClusterManager()

    if not pub.testar_conexao():
        print("❌ Falha de conexão")
        return

    print("\nBuscando posts do WordPress...")
    posts_wp = buscar_todos_posts(pub)
    print(f"  {len(posts_wp)} posts encontrados")

    # Popula cluster com todos os posts existentes (dedup interno)
    print("\nPopulando cluster com posts existentes...")
    for wp_post in posts_wp:
        titulo  = wp_post.get("title", {}).get("raw", "")
        url     = wp_post.get("link", "")
        wp_id   = wp_post.get("id")
        slug    = wp_post.get("slug", "")
        focuskw = (wp_post.get("meta") or {}).get("_yoast_wpseo_focuskw", "")
        if url and titulo and not slug.startswith("guia-"):
            tema = cluster.detectar_tema(focuskw or titulo, titulo)
            cluster.adicionar_post(tema, {"titulo": titulo, "url": url, "wp_id": wp_id})

    total_no_cluster = sum(len(v) for v in cluster.clusters.values())
    print(f"  Cluster: {total_no_cluster} posts em {len(cluster.clusters)} temas")

    if total_no_cluster == 0:
        print("⚠️  Cluster vazio — nenhum post para interlinkar.")
        return

    # Atualiza cada post com interlinks
    print("\nInjetando interlinks nos posts...")
    atualizados = 0
    pulados = 0
    erros = 0

    for wp_post in posts_wp:
        wp_id    = wp_post.get("id")
        titulo   = wp_post.get("title", {}).get("raw", "")
        conteudo = wp_post.get("content", {}).get("raw", "")
        slug     = wp_post.get("slug", "")
        focuskw  = (wp_post.get("meta") or {}).get("_yoast_wpseo_focuskw", "")
        url      = wp_post.get("link", "")

        # Pula páginas pilares
        if slug.startswith("guia-"):
            pulados += 1
            continue

        # Pula posts que já têm interlinks
        if "Leia também sobre" in conteudo or "Modelos relacionados" in conteudo:
            pulados += 1
            continue

        tema = cluster.detectar_tema(focuskw or titulo, titulo)
        interlinks = cluster.gerar_html_interlinks(tema, excluir_url=url)
        if not interlinks:
            pulados += 1
            continue

        # Insere antes do FAQ schema (se existir), senão no final
        if '<script type="application/ld+json">' in conteudo:
            novo_conteudo = conteudo.replace(
                '<script type="application/ld+json">',
                interlinks + '\n<script type="application/ld+json">',
                1,
            )
        else:
            novo_conteudo = conteudo + "\n" + interlinks

        try:
            pub._request("POST", f"posts/{wp_id}", json={"content": novo_conteudo})
            print(f"  ✅ [{wp_id}] {titulo[:55]}")
            atualizados += 1
        except Exception as e:
            print(f"  ❌ [{wp_id}] {titulo[:40]}: {e}")
            erros += 1

    # Publica pilares para temas com 3+ posts
    print("\nVerificando páginas pilares...")
    for tema in list(cluster.clusters.keys()):
        if cluster.total_posts(tema) >= 3:
            pilar = cluster.gerar_pilar(tema)
            if not pilar:
                continue
            meta_pilar = f"Guia completo sobre {tema} na impressão 3D. Tutoriais, dicas e downloads."
            post_pilar = {
                "titulo":          pilar["titulo"],
                "slug":            pilar["slug"],
                "content":         pilar["conteudo"],
                "excerpt":         meta_pilar,
                "status":          "draft",
                "tags":            [tema, "impressao 3d", "guia completo"],
                "categories":      [tema],
                "yoast_keyphrase": f"impressão 3d {tema.lower()}",
                "yoast_title":     f"{tema} — Guia Completo | Clube 3D Brasil",
                "yoast_meta":      meta_pilar[:155],
            }
            try:
                result = pub.publicar_post(post_pilar)
                status = result.get("status", "")
                url_p  = result.get("url", "")
                if status == "existente":
                    print(f"  ⏭️  Pilar já existe: {tema}")
                else:
                    print(f"  🏛️  Pilar criado [{tema}]: {url_p}")
            except Exception as e:
                print(f"  ❌ Pilar [{tema}]: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ Atualizados: {atualizados} | ⏭️  Já tinham: {pulados} | ❌ Erros: {erros}")


if __name__ == "__main__":
    main()
