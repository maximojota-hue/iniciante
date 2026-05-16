"""
Preparador leve de pacote para posts do Clube 3D Brasil.

Objetivo:
- Fazer localmente a parte repetitiva e barata: URL, titulo, transcricao/conteudo,
  afiliados, capa e fotos.
- Gerar um bloco compacto para colar no chat do Codex.
- Evitar gastar tokens com logs longos, transcricoes enormes e reexplicacoes.

Ferramentas gratuitas usadas:
- yt-dlp, quando disponivel, para metadados e legendas do YouTube.
- requests + BeautifulSoup para paginas web.
- tkinter/clipboard local para copiar a saida.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import textwrap
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - interface mostra erro se faltar
    requests = None
    BeautifulSoup = None


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
PACOTE_JSON = OUT_DIR / "pacote_codex_post.json"
PACOTE_MD = OUT_DIR / "PACOTE_CODEX_POST.md"
AFILIADOS_MD = ROOT / "CONTROLE_AFILIADOS.md"

BG = "#111827"
BG2 = "#16213a"
BG3 = "#0b1220"
FG = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#0ea5e9"
GREEN = "#22c55e"
ORANGE = "#f97316"


@dataclass
class Afiliado:
    id: int
    nome: str
    link: str
    foto: str
    observacoes: str = ""


def compact_text(text: str, limit: int = 3600) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    head = text[: int(limit * 0.72)].rsplit(" ", 1)[0]
    tail = text[-int(limit * 0.24) :].split(" ", 1)[-1]
    return f"{head}\n\n[...conteudo compactado localmente...]\n\n{tail}"


def clean_vtt(raw: str, limit: int = 4200) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        if re.match(r"^\d{2}:\d{2}", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    return compact_text(" ".join(lines), limit)


def carregar_afiliados() -> list[Afiliado]:
    if not AFILIADOS_MD.exists():
        return []
    afiliados: list[Afiliado] = []
    for line in AFILIADOS_MD.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("| ") or "| #" in line or "Nome curto" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 6:
            continue
        raw_id = cols[0].strip().lstrip("#")
        if not raw_id.isdigit():
            continue
        afiliados.append(
            Afiliado(
                id=int(raw_id),
                nome=cols[1],
                link=cols[2].strip("`"),
                foto=cols[3].strip("`"),
                observacoes=cols[5],
            )
        )
    return afiliados


def yt_metadata(url: str) -> dict:
    cmd = ["yt-dlp", "--dump-json", "--no-playlist", url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=45, encoding="utf-8")
    if result.returncode != 0 or not result.stdout.strip():
        return {"erro": (result.stderr or "yt-dlp nao retornou metadados")[:600]}
    data = json.loads(result.stdout)
    chapters = [
        {"inicio": c.get("start_time"), "titulo": c.get("title", "")}
        for c in data.get("chapters") or []
    ][:12]
    return {
        "video_id": data.get("id", ""),
        "titulo_original": data.get("title", ""),
        "canal": data.get("channel") or data.get("uploader", ""),
        "data_upload": data.get("upload_date", ""),
        "duracao": data.get("duration_string", ""),
        "descricao": compact_text(data.get("description") or "", 900),
        "capitulos": chapters,
    }


def yt_transcript(url: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        for idx, langs in enumerate(("pt,pt-BR,pt-br,en,en-US,en-orig", "es,es-US,es-orig", "all"), 1):
            prefix = str(Path(tmp) / f"video_{idx}")
            cmd = [
                "yt-dlp",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                langs,
                "--sub-format",
                "vtt",
                "--skip-download",
                "--no-playlist",
                "-o",
                prefix,
                url,
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=90, encoding="utf-8")
            vtts = sorted(Path(tmp).glob("*.vtt"))
            if vtts:
                return clean_vtt(vtts[0].read_text(encoding="utf-8", errors="ignore"))
        return ""


def web_extract(url: str) -> dict:
    if requests is None or BeautifulSoup is None:
        return {"erro": "Instale requests e beautifulsoup4 para extrair paginas web."}
    headers = {"User-Agent": "Mozilla/5.0 Clube3DBrasilBot/1.0"}
    resp = requests.get(url, headers=headers, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "aside"]):
        tag.decompose()
    title = (soup.title.get_text(" ", strip=True) if soup.title else "").strip()
    meta = soup.find("meta", attrs={"name": "description"})
    desc = meta.get("content", "").strip() if meta else ""
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2"])][:14]
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 45]
    return {
        "titulo_original": title,
        "descricao": desc,
        "headings": headings,
        "conteudo": compact_text("\n".join(paragraphs), 4300),
    }


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Clube 3D Brasil - Preparador Leve de Post")
        self.geometry("1040x760")
        self.configure(bg=BG)
        self.afiliados = carregar_afiliados()
        self.vars_afiliados: dict[int, tk.BooleanVar] = {}
        self.var_tipo = tk.StringVar(value="youtube")
        self.var_url = tk.StringVar()
        self.var_keyword = tk.StringVar()
        self.var_categoria = tk.StringVar(value="STL Geek")
        self.var_capa = tk.StringVar()
        self.var_foto1 = tk.StringVar()
        self.var_foto2 = tk.StringVar()
        self.var_foto3 = tk.StringVar()
        self.var_status = tk.StringVar(value="Pronto.")
        self._build()

    def _build(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton", padding=8)
        style.configure("Run.TButton", background=GREEN, foreground="white")

        header = tk.Frame(self, bg=BG, padx=18, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="Preparador leve de pacote para o Codex", bg=BG, fg=FG, font=("Segoe UI", 17, "bold")).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Extraia dados localmente, selecione fotos/afiliados e copie um pacote curto para o chat.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor=tk.W, pady=(4, 0))

        body = tk.Frame(self, bg=BG, padx=18)
        body.pack(fill=tk.BOTH, expand=True)

        form = tk.Frame(body, bg=BG2, padx=14, pady=12)
        form.pack(fill=tk.X)
        self._radio(form, "YouTube", "youtube", 0, 0)
        self._radio(form, "Pagina web", "web", 0, 1)
        self._entry(form, "URL", self.var_url, 1, width=92)
        self._entry(form, "Keyword alvo", self.var_keyword, 2, width=48)
        self._combo(form, "Categoria", self.var_categoria, 3)

        photos = tk.Frame(body, bg=BG2, padx=14, pady=12)
        photos.pack(fill=tk.X, pady=(10, 0))
        self._file_row(photos, "Foto capa", self.var_capa, 0)
        self._file_row(photos, "Foto 1", self.var_foto1, 1)
        self._file_row(photos, "Foto 2", self.var_foto2, 2)
        self._file_row(photos, "Foto 3", self.var_foto3, 3)

        af_box = tk.Frame(body, bg=BG2, padx=14, pady=12)
        af_box.pack(fill=tk.X, pady=(10, 0))
        tk.Label(af_box, text="Afiliados cadastrados (maximo 3 por post)", bg=BG2, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        grid = tk.Frame(af_box, bg=BG2)
        grid.pack(fill=tk.X, pady=(8, 0))
        for i, af in enumerate(self.afiliados):
            var = tk.BooleanVar(value=False)
            self.vars_afiliados[af.id] = var
            label = f"#{af.id} {af.nome}"
            cb = ttk.Checkbutton(grid, text=label, variable=var, command=self._limit_afiliados)
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 22), pady=3)

        actions = tk.Frame(body, bg=BG, pady=12)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Gerar pacote", style="Run.TButton", command=self._run_thread).pack(side=tk.LEFT)
        ttk.Button(actions, text="Abrir arquivo", command=self._open_output).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Copiar pacote", command=self._copy_output).pack(side=tk.LEFT)
        tk.Label(actions, textvariable=self.var_status, bg=BG, fg=MUTED).pack(side=tk.LEFT, padx=14)

        out_frame = tk.Frame(body, bg=BG3, padx=8, pady=8)
        out_frame.pack(fill=tk.BOTH, expand=True)
        self.output = tk.Text(out_frame, bg="#020617", fg=FG, insertbackground=FG, font=("Consolas", 10), wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _radio(self, parent, text: str, value: str, row: int, col: int) -> None:
        ttk.Radiobutton(parent, text=text, value=value, variable=self.var_tipo).grid(row=row, column=col, sticky="w", padx=(0, 16))

    def _entry(self, parent, label: str, var: tk.StringVar, row: int, width: int = 60) -> None:
        tk.Label(parent, text=label, bg=BG2, fg=MUTED).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=var, width=width).grid(row=row, column=1, columnspan=5, sticky="w", pady=5)

    def _combo(self, parent, label: str, var: tk.StringVar, row: int) -> None:
        tk.Label(parent, text=label, bg=BG2, fg=MUTED).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Combobox(
            parent,
            textvariable=var,
            width=34,
            values=["STL Geek", "Impressao 3D para Iniciantes", "Cosplay Maker", "Impressoras e Reviews", "Ganhar Dinheiro com Impressao 3D", "Games & Personagens"],
        ).grid(row=row, column=1, sticky="w", pady=5)

    def _file_row(self, parent, label: str, var: tk.StringVar, row: int) -> None:
        tk.Label(parent, text=label, bg=BG2, fg=MUTED, width=12, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=var, width=88).grid(row=row, column=1, sticky="w", pady=4)
        ttk.Button(parent, text="Selecionar", command=lambda: self._pick_file(var)).grid(row=row, column=2, padx=8)

    def _pick_file(self, var: tk.StringVar) -> None:
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")])
        if path:
            var.set(path)

    def _limit_afiliados(self) -> None:
        selected = [i for i, v in self.vars_afiliados.items() if v.get()]
        if len(selected) > 3:
            self.vars_afiliados[selected[-1]].set(False)
            messagebox.showinfo("Limite", "Use no maximo 3 afiliados por post.")

    def _run_thread(self) -> None:
        threading.Thread(target=self._generate, daemon=True).start()

    def _generate(self) -> None:
        try:
            url = self.var_url.get().strip()
            if not url:
                messagebox.showwarning("URL", "Informe a URL.")
                return
            self.var_status.set("Extraindo dados localmente...")
            if self.var_tipo.get() == "youtube":
                source = yt_metadata(url)
                source["transcricao_compacta"] = yt_transcript(url)
                source["tipo"] = "youtube"
            else:
                source = web_extract(url)
                source["tipo"] = "web"
            source["url"] = url

            selected_ids = [i for i, v in self.vars_afiliados.items() if v.get()]
            afiliados = [asdict(a) for a in self.afiliados if a.id in selected_ids]
            pacote = {
                "versao": "pacote-codex-post-v1",
                "gerado_em": datetime.now().isoformat(timespec="seconds"),
                "acao": "criar rascunho wordpress sem API externa de conteudo",
                "keyword_alvo": self.var_keyword.get().strip(),
                "categoria": self.var_categoria.get().strip(),
                "fonte": source,
                "midia": {
                    "foto_capa": self.var_capa.get().strip(),
                    "foto1": self.var_foto1.get().strip(),
                    "foto2": self.var_foto2.get().strip(),
                    "foto3": self.var_foto3.get().strip(),
                },
                "afiliados": afiliados,
                "regras": [
                    "Gerar post em PT-BR para Clube 3D Brasil.",
                    "Nao usar API externa de conteudo no chat.",
                    "Publicar como rascunho no WordPress.",
                    "Usar foto_capa como base da capa; se vazia, criar capa nova.",
                    "Inserir afiliados com imagem clicavel, nova aba e rel sponsored.",
                    "Atualizar CONTROLE_POSTS.md apos publicar.",
                ],
            }
            md = self._render_md(pacote)
            OUT_DIR.mkdir(exist_ok=True)
            PACOTE_JSON.write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
            PACOTE_MD.write_text(md, encoding="utf-8")
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", md)
            self._copy_text(md)
            self.var_status.set(f"Pacote gerado e copiado: {PACOTE_MD}")
        except Exception as exc:
            self.var_status.set("Erro ao gerar pacote.")
            messagebox.showerror("Erro", str(exc))

    def _render_md(self, pacote: dict) -> str:
        return textwrap.dedent(
            f"""
            CRIAR_POST_CLUBE3D_COM_PACOTE

            Use este pacote compacto para criar e publicar um rascunho no WordPress com o fluxo leve.
            Nao use API externa de conteudo no chat. Use os dados abaixo como contexto suficiente.

            ```json
            {json.dumps(pacote, ensure_ascii=False, indent=2)}
            ```
            """
        ).strip()

    def _copy_text(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _copy_output(self) -> None:
        text = self.output.get("1.0", tk.END).strip()
        if text:
            self._copy_text(text)
            self.var_status.set("Pacote copiado para a area de transferencia.")

    def _open_output(self) -> None:
        if PACOTE_MD.exists():
            import os

            os.startfile(PACOTE_MD)
        else:
            messagebox.showinfo("Arquivo", "Gere um pacote primeiro.")


if __name__ == "__main__":
    App().mainloop()
