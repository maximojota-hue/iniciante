"""
gerar_cluster1_geek.py — Cluster 1 STL Geek (20 posts)
Calendário: 12 mai–17 jul 2026, 2x/semana (seg + qui)

Execute: python gerar_cluster1_geek.py
Depois:  python main.py --so-publicar
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from seo_writer import gerar_post_seo

POSTS = [
    # ── SEMANA 1 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-05-12", "tipo": "pilar", "fandom": "Pokémon",
        "keyword": "pokémon stl grátis impressão 3d",
        "secondary": ["pikachu stl grátis", "pokemon modelos 3d", "pokemon impressão 3d brasil"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-05-15", "tipo": "pilar", "fandom": "Minecraft",
        "keyword": "minecraft stl grátis impressão 3d",
        "secondary": ["creeper stl grátis", "minecraft modelos 3d", "steve impressão 3d"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 2 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-05-19", "tipo": "pilar", "fandom": "Naruto",
        "keyword": "naruto stl grátis impressão 3d",
        "secondary": ["naruto uzumaki stl", "naruto modelos 3d", "download naruto 3d"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-05-22", "tipo": "pilar", "fandom": "Dragon Ball",
        "keyword": "dragon ball stl grátis impressão 3d",
        "secondary": ["goku stl grátis", "vegeta stl impressão 3d", "dragon ball modelos 3d"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 3 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-05-26", "tipo": "suporte", "fandom": "Pokémon",
        "keyword": "como imprimir pikachu 3d",
        "secondary": ["pikachu stl configuração impressão", "pikachu impressão 3d filamento", "pokemon impressão 3d dicas"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-05-29", "tipo": "pilar", "fandom": "Marvel",
        "keyword": "marvel stl grátis impressão 3d",
        "secondary": ["homem aranha stl grátis", "marvel modelos 3d", "super heroi stl grátis download"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 4 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-06-02", "tipo": "pilar", "fandom": "One Piece",
        "keyword": "one piece stl grátis impressão 3d",
        "secondary": ["luffy stl grátis", "zoro stl impressão 3d", "one piece modelos 3d download"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-06-05", "tipo": "suporte", "fandom": "Naruto",
        "keyword": "akatsuki impressão 3d stl grátis",
        "secondary": ["itachi stl grátis", "pain stl naruto impressão 3d", "tobi stl download"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 5 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-06-09", "tipo": "pilar", "fandom": "Demon Slayer",
        "keyword": "demon slayer stl grátis impressão 3d",
        "secondary": ["tanjiro stl grátis", "nezuko stl impressão 3d", "kimetsu no yaiba modelos 3d"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-06-12", "tipo": "suporte", "fandom": "Dragon Ball",
        "keyword": "como imprimir goku super sayajin 3d",
        "secondary": ["goku super sayajin stl impressão", "goku 3d filamento recomendado", "dragon ball impressão 3d dicas"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 6 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-06-16", "tipo": "pilar", "fandom": "Star Wars",
        "keyword": "star wars stl grátis impressão 3d",
        "secondary": ["darth vader stl grátis", "yoda stl impressão 3d", "star wars modelos 3d download"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-06-19", "tipo": "suporte", "fandom": "Marvel",
        "keyword": "como imprimir homem aranha 3d",
        "secondary": ["homem aranha stl impressão 3d", "spider man 3d filamento", "marvel impressão 3d configuração"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 7 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-06-23", "tipo": "pilar", "fandom": "Zelda",
        "keyword": "zelda stl grátis impressão 3d",
        "secondary": ["link stl grátis zelda", "master sword stl impressão 3d", "zelda modelos 3d download"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-06-26", "tipo": "suporte", "fandom": "One Piece",
        "keyword": "chapéu de palha luffy impressão 3d stl",
        "secondary": ["luffy chapeu stl grátis", "one piece stl download gratuito", "luffy impressão 3d dicas acabamento"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 8 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-06-30", "tipo": "pilar", "fandom": "Funko Pop",
        "keyword": "como fazer funko pop impressão 3d stl grátis",
        "secondary": ["funko pop 3d stl download", "funko pop personalizado impressão 3d", "funko pop como imprimir pla"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-07-03", "tipo": "suporte", "fandom": "Demon Slayer",
        "keyword": "como imprimir máscara tanjiro 3d",
        "secondary": ["tanjiro mascara stl grátis", "demon slayer impressão 3d pintura", "tanjiro acabamento colorido 3d"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 9 ──────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-07-07", "tipo": "suporte", "fandom": "Minecraft",
        "keyword": "como imprimir creeper 3d iniciante",
        "secondary": ["creeper stl grátis download", "minecraft impressão 3d configuração cura", "creeper pla filamento cor"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-07-10", "tipo": "suporte", "fandom": "Star Wars",
        "keyword": "capacete darth vader impressão 3d stl grátis",
        "secondary": ["darth vader capacete stl download", "star wars impressão 3d acabamento pintura", "darth vader 3d filamento preto"],
        "categoria": "STL Geek",
    },
    # ── SEMANA 10 ─────────────────────────────────────────────────────────────
    {
        "data_pub": "2026-07-14", "tipo": "suporte", "fandom": "Zelda",
        "keyword": "triforce zelda impressão 3d stl grátis",
        "secondary": ["triforce stl download gratuito", "zelda impressão 3d como montar", "triforce 3d acabamento dourado"],
        "categoria": "STL Geek",
    },
    {
        "data_pub": "2026-07-17", "tipo": "suporte", "fandom": "Pokémon",
        "keyword": "eevee evoluções impressão 3d stl grátis",
        "secondary": ["eevee stl grátis printables", "pokemon evoluções 3d download", "eevee acabamento pintura impressão 3d"],
        "categoria": "STL Geek",
    },
]


def main():
    print()
    print("=" * 65)
    print("  CLUSTER 1 — STL GEEK | 20 posts | 12 mai–17 jul 2026")
    print("=" * 65)
    print()

    posts_gerados = []
    erros = []

    for i, p in enumerate(POSTS, 1):
        print(f"[{i:02d}/20] {p['fandom']:12s} ({p['tipo']:7s}) — {p['keyword']}")
        try:
            post = gerar_post_seo(
                keyword=p["keyword"],
                secondary_kws=p["secondary"],
                categoria=p["categoria"],
            )
            post["data_publicacao"] = p["data_pub"]
            post["cluster"]         = "STL Geek"
            post["fandom"]          = p["fandom"]
            post["tipo_post"]       = p["tipo"]
            posts_gerados.append(post)
            print(f"  OK: {post['titulo'][:60]}")
        except Exception as e:
            print(f"  ERRO: {e}")
            erros.append({"index": i, "keyword": p["keyword"], "erro": str(e)})

    out = Path("posts_gerados.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(posts_gerados, f, indent=2, ensure_ascii=False)

    print()
    print(f"  {len(posts_gerados)}/20 posts salvos em {out}")
    if erros:
        print(f"  {len(erros)} erros:")
        for e in erros:
            print(f"    [{e['index']:02d}] {e['keyword']}: {e['erro']}")
    print()
    print("  Proximo passo: python main.py --so-publicar")
    print()


if __name__ == "__main__":
    main()
