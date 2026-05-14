"""
teste_seo_flow.py — Teste completo: seo_writer → publisher (draft)
Uso: python teste_seo_flow.py
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

import seo_writer
import publisher

KEYWORD     = "ganhar dinheiro com impressora 3d em casa"
KEYWORD_EN  = "make money with 3d printer at home"
SECONDARY   = ["quanto faturar com impressora 3d", "renda extra impressao 3d", "vender impressao 3d"]
YOUTUBE_URL = "https://www.youtube.com/watch?v=xiQVIR45sKQ"
LANG        = "both"  # "pt-BR" | "en-US" | "both"

print("=" * 60)
print(f"TESTE SEO FLOW — {LANG}")
print(f"Keyword PT: {KEYWORD}")
if LANG in ("en-US", "both"):
    print(f"Keyword EN: {KEYWORD_EN}")
print("=" * 60)

posts_para_publicar = []

# 0. Extrair transcrição (se URL fornecida)
transcript = ""
if YOUTUBE_URL:
    print("\n[YT] Extraindo transcrição do YouTube...")
    transcript = seo_writer.extrair_transcricao_yt(YOUTUBE_URL, log_fn=print)
    if transcript:
        print(f"  Transcrição extraída: {len(transcript)} chars")
    else:
        print("  Sem transcrição — gerando só com keyword.")

# 1. Gerar posts
if LANG in ("pt-BR", "both"):
    print("\n[PT-BR] Gerando post SEO...")
    try:
        post_pt = seo_writer.gerar_post_seo(
            keyword=KEYWORD, secondary_kws=SECONDARY,
            transcript=transcript, youtube_url=YOUTUBE_URL, lang="pt-BR",
        )
        print(f"  Titulo: {post_pt['titulo']}")
        print(f"  Meta:   {post_pt['yoast_meta']}")
        posts_para_publicar.append(("PT", post_pt))
    except Exception as e:
        print(f"  ERRO: {e}"); sys.exit(1)

if LANG in ("en-US", "both"):
    print("\n[EN-US] Gerando post SEO...")
    try:
        post_en = seo_writer.gerar_post_seo(
            keyword=KEYWORD_EN, secondary_kws=SECONDARY,
            youtube_url=YOUTUBE_URL, lang="en-US",
        )
        print(f"  Title: {post_en['titulo']}")
        print(f"  Meta:  {post_en['yoast_meta']}")
        posts_para_publicar.append(("EN", post_en))
    except Exception as e:
        print(f"  ERRO: {e}"); sys.exit(1)

# 2. Publicar como draft
cfg = {
    "wp_url":          os.environ.get("WP_URL", "https://clube3dbrasil.com"),
    "wp_user":         os.environ.get("WP_USER", ""),
    "wp_app_password": os.environ.get("WP_PASS", ""),
    "wp_post_status":  "draft",
}
pub = publisher.WordPressPublisher(cfg)

for lang_label, post in posts_para_publicar:
    print(f"\n[{lang_label}] Publicando como draft...")
    try:
        result = pub.publicar_post(post)
        print(f"  OK! ID: {result['wp_id']} — {result['url']}")
    except Exception as e:
        print(f"  ERRO ao publicar: {e}"); sys.exit(1)

print("\n[CONCLUIDO] Verifique os rascunhos no WP admin.")
