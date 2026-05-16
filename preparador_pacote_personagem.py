"""
Preparador leve de pacote para posts de personagens 3D.

Fluxo:
- O usuario cria uma pasta com fotos do modelo e um atalho .url para a pagina
  onde o visitante deve baixar o arquivo.
- Este script le a pasta localmente, identifica imagens e link de download,
  monta um pacote compacto e copia para o chat do Codex.
- O chat usa o pacote para criar o post sem API externa de conteudo.
"""

from __future__ import annotations

import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
PACOTE_JSON = OUT_DIR / "pacote_codex_personagem.json"
PACOTE_MD = OUT_DIR / "PACOTE_CODEX_PERSONAGEM.md"

BG = "#111827"
BG2 = "#16213a"
BG3 = "#0b1220"
FG = "#f8fafc"
MUTED = "#94a3b8"
GREEN = "#22c55e"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def slug_to_title(text: str) -> str:
    text = re.sub(r"[_+-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:] if text else ""


def read_url_file(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    for line in raw.splitlines():
        if line.lower().startswith("url="):
            return line.split("=", 1)[1].strip()
    match = re.search(r"https?://\S+", raw)
    return match.group(0).strip() if match else ""


def scan_folder(folder: Path) -> dict:
    if not folder.exists() or not folder.is_dir():
        raise ValueError("Selecione uma pasta valida.")

    images = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=lambda p: (0 if "download" in p.name.lower() else 1, p.name.lower()),
    )
    urls = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".url"])

    download_url = ""
    download_label = ""
    if urls:
        download_url = read_url_file(urls[0])
        download_label = urls[0].stem

    title_base = download_label or folder.name
    title = slug_to_title(title_base)

    return {
        "pasta": str(folder),
        "titulo_sugerido": title,
        "download_url": download_url,
        "download_label": download_label,
        "atalho_url": str(urls[0]) if urls else "",
        "imagens": [str(p) for p in images[:8]],
        "foto_capa": str(images[0]) if images else "",
        "foto1": str(images[1]) if len(images) > 1 else "",
        "foto2": str(images[2]) if len(images) > 2 else "",
        "foto3": str(images[3]) if len(images) > 3 else "",
    }


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Clube 3D Brasil - Pacote Personagem 3D")
        self.geometry("980x700")
        self.configure(bg=BG)
        self.var_folder = tk.StringVar()
        self.var_keyword = tk.StringVar()
        self.var_categoria = tk.StringVar(value="Games & Personagens")
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
        tk.Label(header, text="Post de personagem 3D por pasta", bg=BG, fg=FG, font=("Segoe UI", 17, "bold")).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Selecione a pasta com fotos e um arquivo .url. O pacote final tera o CTA para baixar o STL no fim do post.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor=tk.W, pady=(4, 0))

        form = tk.Frame(self, bg=BG2, padx=14, pady=12)
        form.pack(fill=tk.X, padx=18)
        tk.Label(form, text="Pasta do personagem", bg=BG2, fg=MUTED).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.var_folder, width=88).grid(row=0, column=1, sticky="w", pady=5)
        ttk.Button(form, text="Selecionar", command=self._pick_folder).grid(row=0, column=2, padx=8)

        tk.Label(form, text="Keyword alvo", bg=BG2, fg=MUTED).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.var_keyword, width=48).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(form, text="Categoria", bg=BG2, fg=MUTED).grid(row=2, column=0, sticky="w", pady=5)
        ttk.Combobox(
            form,
            textvariable=self.var_categoria,
            width=34,
            values=["Games & Personagens", "STL Geek", "Cosplay Maker", "Impressao 3D para Iniciantes"],
        ).grid(row=2, column=1, sticky="w", pady=5)

        actions = tk.Frame(self, bg=BG, padx=18, pady=12)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Gerar pacote", style="Run.TButton", command=self._generate).pack(side=tk.LEFT)
        ttk.Button(actions, text="Abrir arquivo", command=self._open_output).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Copiar pacote", command=self._copy_output).pack(side=tk.LEFT)
        tk.Label(actions, textvariable=self.var_status, bg=BG, fg=MUTED).pack(side=tk.LEFT, padx=14)

        out_frame = tk.Frame(self, bg=BG3, padx=8, pady=8)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))
        self.output = tk.Text(out_frame, bg="#020617", fg=FG, insertbackground=FG, font=("Consolas", 10), wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _pick_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecionar pasta do personagem 3D")
        if folder:
            self.var_folder.set(folder)

    def _generate(self) -> None:
        try:
            folder = Path(self.var_folder.get().strip())
            data = scan_folder(folder)
            pacote = {
                "versao": "pacote-codex-personagem-v1",
                "gerado_em": datetime.now().isoformat(timespec="seconds"),
                "acao": "criar rascunho wordpress de personagem 3d sem API externa de conteudo",
                "keyword_alvo": self.var_keyword.get().strip() or data["titulo_sugerido"],
                "categoria": self.var_categoria.get().strip(),
                "fonte": {
                    "tipo": "pasta_personagem_3d",
                    "pasta": data["pasta"],
                    "titulo_sugerido": data["titulo_sugerido"],
                    "download_url": data["download_url"],
                    "download_label": data["download_label"],
                    "atalho_url": data["atalho_url"],
                },
                "midia": {
                    "foto_capa": data["foto_capa"],
                    "foto1": data["foto1"],
                    "foto2": data["foto2"],
                    "foto3": data["foto3"],
                    "imagens_disponiveis": data["imagens"],
                },
                "afiliados": [],
                "regras": [
                    "Gerar post em PT-BR para Clube 3D Brasil.",
                    "Nao usar API externa de conteudo no chat.",
                    "Publicar como rascunho no WordPress.",
                    "Criar post de personagem 3D com foco em baixar STL/modelo 3D.",
                    "Usar as fotos da pasta como base visual do post.",
                    "No final do post, inserir um CTA claro para acessar a pagina de download.",
                    "O link de download deve abrir em nova aba com rel noopener noreferrer.",
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
            CRIAR_POST_PERSONAGEM_3D_COM_PASTA

            Use este pacote compacto para criar e publicar um rascunho no WordPress com o fluxo leve.
            Nao use API externa de conteudo no chat. Use as fotos e o link de download abaixo como contexto suficiente.

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
