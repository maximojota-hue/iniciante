"""
Preparador leve de pacote para posts de personagens 3D.

Fluxo:
- O usuario cria uma pasta com fotos do modelo e um atalho .url para a pagina
  onde o visitante deve baixar o arquivo.
- Este script le uma pasta unica ou varias subpastas, identifica imagens e link
  de download, monta pacote(s) compacto(s) e copia para o chat do Codex.
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
PACOTES_JSON = OUT_DIR / "pacotes_codex_personagens.json"
PACOTES_MD = OUT_DIR / "PACOTES_CODEX_PERSONAGENS.md"

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


def pretty_category(text: str) -> str:
    text = re.sub(r"[_+-]+", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title() if text else ""


def keyword_from_url(url: str) -> str:
    match = re.search(r"/models/\d+-([^/?#]+)", url or "")
    if not match:
        return ""
    slug = match.group(1)
    slug = re.sub(r"[_+-]+", " ", slug)
    slug = re.sub(r"\s+", " ", slug).strip()
    return slug_to_title(slug)


def infer_keyword(download_label: str, download_url: str, folder: Path) -> str:
    label = download_label or ""
    if " - " in label:
        label = label.split(" - ", 1)[0]
    label = re.sub(
        r"\b(modelo|gratuito|gratis|para|impressao|impressão|3d|makerworld|stl)\b",
        "",
        label,
        flags=re.IGNORECASE,
    )
    label = re.sub(r"\s+", " ", label).strip(" -_")
    if label:
        return slug_to_title(label)
    from_url = keyword_from_url(download_url)
    return from_url or slug_to_title(folder.name)


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
    keyword = infer_keyword(download_label, download_url, folder)
    categoria_personagem = pretty_category(folder.parent.name)

    return {
        "pasta": str(folder),
        "titulo_sugerido": title,
        "keyword_sugerida": keyword,
        "categoria_personagem": categoria_personagem,
        "download_url": download_url,
        "download_label": download_label,
        "atalho_url": str(urls[0]) if urls else "",
        "imagens": [str(p) for p in images[:8]],
        "foto_capa": str(images[0]) if images else "",
        "foto1": str(images[1]) if len(images) > 1 else "",
        "foto2": str(images[2]) if len(images) > 2 else "",
        "foto3": str(images[3]) if len(images) > 3 else "",
    }


def folder_has_package(folder: Path) -> bool:
    if not folder.exists() or not folder.is_dir():
        return False
    has_url = any(p.is_file() and p.suffix.lower() == ".url" for p in folder.iterdir())
    has_image = any(p.is_file() and p.suffix.lower() in IMAGE_EXTS for p in folder.iterdir())
    return has_url and has_image


def scan_batch(root_folder: Path) -> list[dict]:
    if not root_folder.exists() or not root_folder.is_dir():
        raise ValueError("Selecione uma pasta valida.")
    folders = [root_folder] if folder_has_package(root_folder) else []
    folders.extend(
        sorted(
            [p for p in root_folder.iterdir() if p.is_dir() and folder_has_package(p)],
            key=lambda p: p.name.lower(),
        )
    )
    if not folders:
        raise ValueError("Nenhuma subpasta com fotos e arquivo .url foi encontrada.")
    return [scan_folder(folder) for folder in folders]


def build_package(data: dict, keyword_override: str, categoria: str) -> dict:
    return {
        "versao": "pacote-codex-personagem-v1",
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "acao": "criar rascunho wordpress de personagem 3d sem API externa de conteudo",
        "keyword_alvo": keyword_override or data["keyword_sugerida"] or data["titulo_sugerido"],
        "categoria": categoria,
        "fonte": {
            "tipo": "pasta_personagem_3d",
            "pasta": data["pasta"],
            "categoria_personagem": data["categoria_personagem"],
            "titulo_sugerido": data["titulo_sugerido"],
            "keyword_sugerida": data["keyword_sugerida"],
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


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Clube 3D Brasil - Pacote Personagem 3D")
        self.geometry("980x700")
        self.configure(bg=BG)
        self.var_folder = tk.StringVar()
        self.var_keyword = tk.StringVar()
        self.var_categoria = tk.StringVar(value="Games & Personagens")
        self.var_batch = tk.BooleanVar(value=True)
        self.var_status = tk.StringVar(value="Pronto.")
        self.last_output_path = PACOTE_MD
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
        tk.Label(header, text="Posts de personagens 3D por pasta", bg=BG, fg=FG, font=("Segoe UI", 17, "bold")).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Selecione uma pasta unica ou uma pasta mae com varias subpastas. Cada subpasta precisa ter fotos e um .url.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor=tk.W, pady=(4, 0))

        form = tk.Frame(self, bg=BG2, padx=14, pady=12)
        form.pack(fill=tk.X, padx=18)
        tk.Label(form, text="Pasta / categoria", bg=BG2, fg=MUTED).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.var_folder, width=88).grid(row=0, column=1, sticky="w", pady=5)
        ttk.Button(form, text="Selecionar", command=self._pick_folder).grid(row=0, column=2, padx=8)

        ttk.Checkbutton(form, text="Ler subpastas e gerar varios pacotes", variable=self.var_batch).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(form, text="Keyword alvo", bg=BG2, fg=MUTED).grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.var_keyword, width=48).grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(form, text="Categoria WP", bg=BG2, fg=MUTED).grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(
            form,
            textvariable=self.var_categoria,
            width=34,
            values=["Games & Personagens", "STL Geek", "Cosplay Maker", "Impressao 3D para Iniciantes"],
        ).grid(row=3, column=1, sticky="w", pady=5)

        actions = tk.Frame(self, bg=BG, padx=18, pady=12)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Gerar pacote(s)", style="Run.TButton", command=self._generate).pack(side=tk.LEFT)
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
            keyword_override = self.var_keyword.get().strip()
            categoria = self.var_categoria.get().strip()
            if self.var_batch.get():
                items = scan_batch(folder)
            else:
                items = [scan_folder(folder)]
            pacotes = [
                build_package(
                    data,
                    keyword_override if len(items) == 1 else "",
                    categoria,
                )
                for data in items
            ]
            md = self._render_md(pacotes[0]) if len(pacotes) == 1 else self._render_batch_md(pacotes, folder)
            OUT_DIR.mkdir(exist_ok=True)
            if len(pacotes) == 1:
                PACOTE_JSON.write_text(json.dumps(pacotes[0], ensure_ascii=False, indent=2), encoding="utf-8")
                PACOTE_MD.write_text(md, encoding="utf-8")
                self.last_output_path = PACOTE_MD
            else:
                PACOTES_JSON.write_text(json.dumps(pacotes, ensure_ascii=False, indent=2), encoding="utf-8")
                PACOTES_MD.write_text(md, encoding="utf-8")
                self._write_individual_files(pacotes)
                self.last_output_path = PACOTES_MD
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", md)
            self._copy_text(md)
            self.var_status.set(f"{len(pacotes)} pacote(s) gerado(s) e copiado(s).")
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

    def _render_batch_md(self, pacotes: list[dict], folder: Path) -> str:
        return textwrap.dedent(
            f"""
            CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS

            Use este pacote compacto para criar rascunhos no WordPress com o fluxo leve.
            Nao use API externa de conteudo no chat. Cada item abaixo representa um post de personagem 3D.
            Pasta categoria: {folder}
            Total de pacotes: {len(pacotes)}

            ```json
            {json.dumps(pacotes, ensure_ascii=False, indent=2)}
            ```
            """
        ).strip()

    def _write_individual_files(self, pacotes: list[dict]) -> None:
        for idx, pacote in enumerate(pacotes, 1):
            keyword = pacote.get("keyword_alvo") or f"personagem-{idx}"
            safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", keyword).strip("-").lower() or f"personagem-{idx}"
            path = OUT_DIR / f"PACOTE_PERSONAGEM_{idx:02d}_{safe}.md"
            path.write_text(self._render_md(pacote), encoding="utf-8")

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
        path = self.last_output_path
        if path.exists():
            import os

            os.startfile(path)
        else:
            messagebox.showinfo("Arquivo", "Gere um pacote primeiro.")


if __name__ == "__main__":
    App().mainloop()
