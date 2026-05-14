"""
cluster.py v3.0 — ClusterManager persistente
Estado salvo em cluster_seo.json, compartilhado entre Fluxo 1 e Fluxo 2.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

CLUSTER_FILE = Path("cluster_seo.json")

TOPIC_KEYWORDS = {
    "Impressoras 3D":  ["impressora", "printer", "ender", "bambu", "prusa", "creality", "snapmaker", "comprar impressora"],
    "Filamentos":      ["filamento", "pla", "petg", "abs", "tpu", "asa", "material", "filament", "resina"],
    "Modelagem 3D":    ["modelagem", "fusion", "blender", "cad", "design", "model", "escultura"],
    "Monetizacao":     ["vender", "faturar", "dinheiro", "renda", "lucro", "negocio", "money", "ganhar"],
    "Para Iniciantes": ["iniciante", "comecar", "começar", "primeiro", "basico", "beginner", "start", "guia"],
    "STL Geek":        ["pokémon", "pokemon", "naruto", "dragon ball", "marvel", "zelda", "demon slayer",
                        "one piece", "minecraft", "funko pop", "star wars", "anime", "geek", "fandom",
                        "pikachu", "goku", "luffy", "tanjiro", "akatsuki", "triforce", "darth vader",
                        "creeper", "eevee", "homem aranha", "spider man"],
    "Modelos STL":     ["stl", "download", "modelo", "arquivo", "gratis", "free", "figure", "figura", "chaveiro"],
    "Tecnicas":        ["tecnica", "calibracao", "suporte", "retraction", "temperatura", "velocidade", "settings"],
    "Reviews":         ["review", "teste", "analise", "comparativo", "melhor", "vale a pena", "unboxing"],
}


class ClusterManager:

    def __init__(self):
        self.clusters: dict[str, list[dict]] = defaultdict(list)
        self._load()

    # ── Persistência ──────────────────────────────────────────────────────────

    def _load(self):
        if CLUSTER_FILE.exists():
            try:
                data = json.loads(CLUSTER_FILE.read_text(encoding="utf-8"))
                for tema, info in data.items():
                    self.clusters[tema] = info.get("posts", [])
            except Exception:
                pass

    def _save(self):
        data = {}
        for tema, posts in self.clusters.items():
            data[tema] = {
                "posts":      posts,
                "total":      len(posts),
                "atualizado": datetime.now().isoformat(),
            }
        CLUSTER_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ── Detecção de tema ──────────────────────────────────────────────────────

    def detectar_tema(self, keyword: str, titulo: str = "") -> str:
        texto = (keyword + " " + titulo).lower()
        scores = {
            tema: sum(1 for p in palavras if p in texto)
            for tema, palavras in TOPIC_KEYWORDS.items()
        }
        melhor = max(scores, key=scores.get)
        return melhor if scores[melhor] > 0 else "Modelos STL"

    # ── Gestão de posts ───────────────────────────────────────────────────────

    def adicionar_post(self, tema: str, post_info: dict):
        urls_existentes = {p.get("url") for p in self.clusters[tema]}
        ids_existentes  = {p.get("wp_id") for p in self.clusters[tema]}
        if (post_info.get("url") not in urls_existentes and
                post_info.get("wp_id") not in ids_existentes):
            self.clusters[tema].append(post_info)
            self._save()

    def obter_relacionados(self, tema: str, limite: int = 4, excluir_url: str = "") -> list[dict]:
        posts = [p for p in self.clusters.get(tema, []) if p.get("url") != excluir_url]
        return posts[-limite:]

    def total_posts(self, tema: str) -> int:
        return len(self.clusters.get(tema, []))

    def temas_com_pilar_pendente(self, minimo: int = 3) -> list[str]:
        return [t for t, posts in self.clusters.items() if len(posts) >= minimo]

    # ── HTML de interlinks ────────────────────────────────────────────────────

    def gerar_html_interlinks(self, tema: str, pilar_url: str = "", excluir_url: str = "") -> str:
        relacionados = self.obter_relacionados(tema, excluir_url=excluir_url)
        if not relacionados:
            return ""
        html = f'<h2>Leia também sobre {tema}</h2><ul>'
        for p in relacionados:
            url_p = p["url"]; titulo_p = p["titulo"]
            html += f"<li><a href='{url_p}'>{titulo_p}</a></li>"
        html += "</ul>"
        if pilar_url:
            html += f'<p><a href="{pilar_url}">Ver guia completo: {tema}</a></p>'
        return html

    # ── Pilares ───────────────────────────────────────────────────────────────

    def gerar_pilar(self, tema: str) -> dict | None:
        posts = self.clusters.get(tema, [])
        if len(posts) < 3:
            return None

        slug_tema = (tema.lower()
                     .replace(" ", "-")
                     .replace("ã", "a").replace("â", "a").replace("á", "a")
                     .replace("ç", "c").replace("é", "e").replace("ê", "e")
                     .replace("í", "i").replace("ó", "o").replace("ô", "o")
                     .replace("ú", "u"))

        html  = f"<h1>{tema} — Guia Completo de Impressão 3D</h1>\n"
        html += f"<p>Reunimos os melhores conteúdos sobre <strong>{tema}</strong> para makers brasileiros. "
        html += f"Explore os artigos abaixo e aprofunde seu conhecimento.</p>\n<ul>\n"
        for p in posts:
            url_p = p["url"]; titulo_p = p["titulo"]
            html += f"  <li><a href='{url_p}'>{titulo_p}</a></li>\n"
        html += "</ul>\n"
        html += f"<p>Acompanhe o <a href='https://clube3dbrasil.com'>Clube 3D Brasil</a> para novos conteúdos toda semana.</p>"

        return {
            "titulo":   f"{tema} — Guia Completo | Clube 3D Brasil",
            "conteudo": html,
            "slug":     f"guia-{slug_tema}",
            "tipo":     "pilar",
            "tema":     tema,
        }
