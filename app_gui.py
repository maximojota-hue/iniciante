"""
app_gui.py — Interface Gráfica do Clube 3D Brasil Automação
Execute: python app_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import sys
import io
import os
import importlib
import webbrowser
from pathlib import Path
from datetime import datetime

os.chdir(Path(__file__).parent)

# ── Cores do tema ─────────────────────────────────────────────────────────────
BG         = "#1a1a2e"
BG2        = "#16213e"
BG3        = "#0f3460"
ACCENT     = "#1800ac"
ACCENT2    = "#0073aa"
TEXT       = "#e0e0e0"
TEXT_DIM   = "#888888"
SUCCESS    = "#4caf50"
WARNING    = "#ff9800"
ERROR      = "#f44336"
WHITE      = "#ffffff"
FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_MONO  = ("Consolas", 9)

PROFILES = {
    "Clube 3D Brasil": {
        "wp_url":          "https://clube3dbrasil.com",
        "wp_user":         "",   # sobrescrito pelo .env
        "wp_app_password": "",   # sobrescrito pelo .env
        "env_user_key":    "WP_USER",
        "env_pass_key":    "WP_PASS",
    },
}


class QueueWriter(io.TextIOBase):
    def __init__(self, q: queue.Queue):
        self._q = q

    def write(self, text: str) -> int:
        if text:
            self._q.put(text)
        return len(text)

    def flush(self):
        pass


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Clube 3D Brasil — Automação de Posts")
        self.geometry("1050x720")
        self.minsize(800, 600)
        self.configure(bg=BG)

        self.log_queue     = queue.Queue()
        self.seo_log_queue = queue.Queue()
        self.web_log_queue = queue.Queue()
        self.config_data   = {}
        self.running       = False
        self.seo_running        = False
        self.seo_post_gerado:       dict | None = None
        self.afiliados_carregados:  list        = []
        self.web_running              = False
        self.web_post_gerado: dict | None = None
        self.web_afiliados_carregados: list = []
        self.web_imagens_selecionadas: list = []

        self.yt_log_queue  = queue.Queue()
        self.yt_running    = False
        self.yt_result_url = ""


        self._build_styles()
        self._build_header()
        self._build_notebook()
        self._load_config()
        self._load_posts_tab()
        self._recarregar_afiliados_tree()
        self._poll_log()
        self._poll_seo_log()
        self._poll_web_log()
        self._poll_yt_log()

    # ── Estilos ───────────────────────────────────────────────────────────────

    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=TEXT, font=FONT,
                     fieldbackground=BG2, bordercolor=BG3, troughcolor=BG2)
        s.configure("TNotebook",        background=BG,  borderwidth=0)
        s.configure("TNotebook.Tab",    background=BG2, foreground=TEXT_DIM,
                     padding=[14, 6],   font=FONT_BOLD)
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", WHITE)])
        s.configure("TFrame",           background=BG)
        s.configure("TLabel",           background=BG,  foreground=TEXT, font=FONT)
        s.configure("TEntry",           fieldbackground=BG2, foreground=TEXT,
                     bordercolor=BG3,   insertcolor=TEXT)
        s.configure("TButton",          background=ACCENT2, foreground=WHITE,
                     font=FONT_BOLD,    padding=[10, 5], relief="flat")
        s.map("TButton",
              background=[("active", BG3), ("disabled", BG2)],
              foreground=[("disabled", TEXT_DIM)])
        s.configure("Run.TButton",      background="#2e7d32", foreground=WHITE)
        s.map("Run.TButton",            background=[("active", "#1b5e20"), ("disabled", BG2)])
        s.configure("Danger.TButton",   background="#b71c1c", foreground=WHITE)
        s.map("Danger.TButton",         background=[("active", "#7f0000")])
        s.configure("TProgressbar",     troughcolor=BG2, background=ACCENT2,
                     bordercolor=BG3,   lightcolor=ACCENT2, darkcolor=ACCENT2)
        s.configure("TCheckbutton",     background=BG, foreground=TEXT)
        s.configure("TSpinbox",         fieldbackground=BG2, foreground=TEXT, bordercolor=BG3)
        s.configure("TCombobox",        fieldbackground=BG2, foreground=TEXT,
                     selectbackground=ACCENT, selectforeground=WHITE)
        s.map("TCombobox",              fieldbackground=[("readonly", BG2)])
        s.configure("Treeview",         background=BG2, foreground=TEXT,
                     fieldbackground=BG2, bordercolor=BG3, rowheight=24)
        s.configure("Treeview.Heading", background=BG3, foreground=WHITE, font=FONT_BOLD)
        s.map("Treeview",               background=[("selected", ACCENT)])
        s.configure("TSeparator",       background=BG3)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill=tk.X)

        self.var_perfil = tk.StringVar(value="Clube 3D Brasil")
        self.lbl_header = tk.Label(
            hdr, text="🤖  Clube 3D Brasil — Automação de Posts WordPress",
            bg=ACCENT, fg=WHITE, font=FONT_TITLE)
        self.lbl_header.pack(side=tk.LEFT, padx=16)

        # Seletor de perfil (lado direito)
        perfil_frame = tk.Frame(hdr, bg=ACCENT)
        perfil_frame.pack(side=tk.RIGHT, padx=16)
        tk.Label(perfil_frame, text="Blog:", bg=ACCENT, fg="#aaaaff", font=FONT).pack(side=tk.LEFT, padx=(0, 6))
        perfil_cb = ttk.Combobox(
            perfil_frame, textvariable=self.var_perfil,
            values=list(PROFILES.keys()), state="readonly", width=20,
        )
        perfil_cb.pack(side=tk.LEFT)
        perfil_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_perfil_change())

    def _on_perfil_change(self):
        nome = self.var_perfil.get()
        p = PROFILES.get(nome, {})
        self._carregar_env()

        # Preenche credenciais: tenta .env primeiro, cai para padrão do perfil
        user = os.environ.get(p.get("env_user_key", ""), p.get("wp_user", ""))
        pw   = os.environ.get(p.get("env_pass_key", ""), p.get("wp_app_password", ""))

        self._cfg_vars["wp_url"].set(p.get("wp_url", ""))
        self._cfg_vars["wp_user"].set(user)
        self._cfg_vars["wp_app_password"].set(pw)

        self.lbl_header.config(text=f"🤖  {nome} — Automação de Posts WordPress")

    # ── Notebook ──────────────────────────────────────────────────────────────

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tab_dash      = ttk.Frame(self.nb)
        self.tab_config    = ttk.Frame(self.nb)
        self.tab_afiliados = ttk.Frame(self.nb)
        self.tab_pipeline  = ttk.Frame(self.nb)
        self.tab_seo       = ttk.Frame(self.nb)
        self.tab_web       = ttk.Frame(self.nb)
        self.tab_yt        = ttk.Frame(self.nb)
        self.tab_posts     = ttk.Frame(self.nb)

        self.nb.add(self.tab_dash,      text="  📊  Dashboard  ")
        self.nb.add(self.tab_config,    text="  ⚙️  Configurações  ")
        self.nb.add(self.tab_afiliados, text="  💰  Afiliados  ")
        self.nb.add(self.tab_pipeline,  text="  🚀  Pipeline  ")
        self.nb.add(self.tab_seo,       text="  ✍️  Post SEO  ")
        self.nb.add(self.tab_web,       text="  🌐  Post Web  ")
        self.nb.add(self.tab_yt,        text="  🎬  YouTube  ")
        self.nb.add(self.tab_posts,     text="  📋  Posts Publicados  ")

        self._build_dashboard_tab()
        self._build_config_tab()
        self._build_afiliados_tab()
        self._build_pipeline_tab()
        self._build_seo_tab()
        self._build_web_tab()
        self._build_yt_tab()
        self._build_posts_tab_ui()
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    # ────────────────────────────────────────────────────────────────────────
    # ABA: CONFIGURAÇÕES
    # ────────────────────────────────────────────────────────────────────────

    def _build_config_tab(self):
        # Banner no tab_config (pack), frame abaixo usa grid — sem conflito
        self._tab_info_banner(
            self.tab_config,
            "⚙️  Configurações do WordPress",
            "Defina as credenciais do WordPress (URL, usuário e Application Password), "
            "a planilha de modelos e o número de posts por dia. "
            "Salve aqui antes de usar qualquer outra aba.",
        )

        frame = tk.Frame(self.tab_config, bg=BG, padx=24, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        self._cfg_vars = {}

        fields = [
            ("wp_url",          "URL do WordPress",          "https://clube3dbrasil.com"),
            ("wp_user",         "Usuário WordPress",          "email@exemplo.com"),
            ("wp_app_password", "Application Password",       "xxxx xxxx xxxx xxxx xxxx xxxx"),
            ("ml_afiliado_url", "Link Afiliado MercadoLivre", "https://meli.la/..."),
        ]

        for row_i, (key, label, placeholder) in enumerate(fields):
            tk.Label(frame, text=label, bg=BG, fg=TEXT_DIM, font=FONT).grid(
                row=row_i, column=0, sticky=tk.W, pady=6)
            var = tk.StringVar()
            ttk.Entry(frame, textvariable=var, width=55,
                      show="*" if "password" in key else "").grid(
                row=row_i, column=1, sticky=tk.EW, padx=(12, 0), pady=6)
            self._cfg_vars[key] = var

        # Planilha modelos
        row_i += 1
        tk.Label(frame, text="Planilha de Modelos", bg=BG, fg=TEXT_DIM, font=FONT).grid(
            row=row_i, column=0, sticky=tk.W, pady=6)
        pf = tk.Frame(frame, bg=BG)
        pf.grid(row=row_i, column=1, sticky=tk.EW, padx=(12, 0), pady=6)
        var_planilha = tk.StringVar()
        ttk.Entry(pf, textvariable=var_planilha, width=44).pack(side=tk.LEFT)
        ttk.Button(pf, text="📂", width=3,
                   command=lambda: self._browse_file(var_planilha)).pack(side=tk.LEFT, padx=(4, 0))
        self._cfg_vars["planilha_path"] = var_planilha

        row_i += 1
        tk.Label(frame, text="Posts por dia (padrão)", bg=BG, fg=TEXT_DIM, font=FONT).grid(
            row=row_i, column=0, sticky=tk.W, pady=6)
        var_posts = tk.StringVar(value="10")
        ttk.Spinbox(frame, from_=1, to=50, textvariable=var_posts, width=8).grid(
            row=row_i, column=1, sticky=tk.W, padx=(12, 0), pady=6)
        self._cfg_vars["posts_por_dia"] = var_posts

        row_i += 1
        tk.Label(frame, text="Status do post", bg=BG, fg=TEXT_DIM, font=FONT).grid(
            row=row_i, column=0, sticky=tk.W, pady=6)
        var_status = tk.StringVar(value="draft")
        ttk.Combobox(frame, textvariable=var_status,
                     values=["draft", "publish"], state="readonly", width=15).grid(
            row=row_i, column=1, sticky=tk.W, padx=(12, 0), pady=6)
        self._cfg_vars["wp_post_status"] = var_status

        frame.columnconfigure(1, weight=1)

        row_i += 1
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=row_i, column=0, columnspan=2, sticky=tk.EW, pady=14)

        row_i += 1
        bf = tk.Frame(frame, bg=BG)
        bf.grid(row=row_i, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(bf, text="💾  Salvar Configurações",
                   command=lambda: self._save_config(notify=True)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(bf, text="🔌  Testar Conexão WP",
                   command=self._testar_conexao).pack(side=tk.LEFT)

    def _browse_file(self, var: tk.StringVar, filetypes=None):
        if filetypes is None:
            filetypes = [("Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
        path = filedialog.askopenfilename(title="Selecionar arquivo", filetypes=filetypes)
        if path:
            var.set(path)

    # ────────────────────────────────────────────────────────────────────────
    # ABA: AFILIADOS
    # ────────────────────────────────────────────────────────────────────────

    def _build_afiliados_tab(self):
        outer = tk.Frame(self.tab_afiliados, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._tab_info_banner(
            outer,
            "💰  Afiliados — Produtos para Monetização",
            "Carregue sua planilha de produtos afiliados (colunas: nome, link, tipo) ou adicione manualmente. "
            "Os dados são salvos em afiliados.json e inseridos automaticamente em todos os posts gerados pelo Pipeline e pelo Post SEO.",
            ["Carregar planilha Excel", "Revisar / adicionar produtos", "Salvar afiliados.json"],
        )

        # Seleção de planilha
        file_frame = tk.Frame(outer, bg=BG2, padx=12, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(file_frame, text="Planilha de Afiliados:", bg=BG2, fg=TEXT, font=FONT).pack(side=tk.LEFT)
        self.var_afiliados_planilha = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.var_afiliados_planilha, width=42).pack(
            side=tk.LEFT, padx=(8, 4))
        ttk.Button(file_frame, text="📂", width=3,
                   command=lambda: self._browse_file(self.var_afiliados_planilha)).pack(
            side=tk.LEFT, padx=(0, 8))
        ttk.Button(file_frame, text="📥 Carregar Planilha",
                   command=self._carregar_afiliados_planilha).pack(side=tk.LEFT)

        tk.Label(outer,
                 text="Colunas esperadas na planilha: nome (ou nome_produto)  |  link  |  tipo",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 6))

        # Treeview de afiliados
        tree_frame = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols = ("nome", "link", "tipo")
        self.tree_af = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_af.heading("nome", text="Nome do Produto")
        self.tree_af.heading("link", text="Link Afiliado")
        self.tree_af.heading("tipo", text="Tipo")
        self.tree_af.column("nome", width=210)
        self.tree_af.column("link", width=380)
        self.tree_af.column("tipo", width=110, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_af.yview)
        self.tree_af.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_af.pack(fill=tk.BOTH, expand=True)

        # Formulário de adição manual
        add_frame = tk.Frame(outer, bg=BG2, padx=12, pady=8)
        add_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(add_frame, text="Nome:", bg=BG2, fg=TEXT, font=FONT).grid(
            row=0, column=0, padx=(0, 4), sticky=tk.W)
        self.var_af_nome = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.var_af_nome, width=22).grid(
            row=0, column=1, padx=(0, 12))

        tk.Label(add_frame, text="Link:", bg=BG2, fg=TEXT, font=FONT).grid(
            row=0, column=2, padx=(0, 4), sticky=tk.W)
        self.var_af_link = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.var_af_link, width=38).grid(
            row=0, column=3, padx=(0, 12))

        tk.Label(add_frame, text="Tipo:", bg=BG2, fg=TEXT, font=FONT).grid(
            row=0, column=4, padx=(0, 4), sticky=tk.W)
        self.var_af_tipo = tk.StringVar(value="impressora")
        ttk.Combobox(add_frame, textvariable=self.var_af_tipo,
                     values=["impressora", "filamento", "acessorio", "outro"],
                     width=11, state="readonly").grid(row=0, column=5, padx=(0, 12))

        ttk.Button(add_frame, text="➕ Adicionar",
                   command=self._adicionar_afiliado).grid(row=0, column=6)

        # Botões
        btn_frame = tk.Frame(outer, bg=BG)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="🗑️  Remover Selecionado",
                   command=self._remover_afiliado,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="💾  Salvar afiliados.json",
                   command=self._salvar_afiliados,
                   style="Run.TButton").pack(side=tk.LEFT)
        tk.Label(btn_frame, text="← salvo na raiz do projeto e usado automaticamente pelo gerador",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=12)

    def _carregar_afiliados_planilha(self):
        path = self.var_afiliados_planilha.get().strip()
        if not path or not Path(path).exists():
            messagebox.showerror("Erro", "Selecione uma planilha Excel válida.")
            return
        try:
            import pandas as pd
            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]

            # Normaliza nomes de colunas flexíveis
            if "nome_produto" in df.columns and "nome" not in df.columns:
                df.rename(columns={"nome_produto": "nome"}, inplace=True)
            if "keyword" in df.columns and "tipo" not in df.columns:
                df.rename(columns={"keyword": "tipo"}, inplace=True)

            for col in ("nome", "link", "tipo"):
                if col not in df.columns:
                    df[col] = ""

            # Limpa treeview e recarrega
            for row in self.tree_af.get_children():
                self.tree_af.delete(row)

            for _, row in df.iterrows():
                nome = str(row.get("nome", "")).strip()
                link = str(row.get("link", "")).strip()
                tipo = str(row.get("tipo", "")).strip()
                if nome and link and link != "nan":
                    self.tree_af.insert("", tk.END, values=(nome, link, tipo))

            total = len(self.tree_af.get_children())
            messagebox.showinfo("Carregado", f"{total} afiliado(s) carregado(s) da planilha.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler planilha:\n{e}")

    def _recarregar_afiliados_tree(self):
        for row in self.tree_af.get_children():
            self.tree_af.delete(row)
        af_path = Path("afiliados.json")
        if not af_path.exists():
            return
        try:
            with open(af_path, encoding="utf-8") as f:
                dados = json.load(f)
            for item in dados:
                nome = item.get("nome") or item.get("nome_produto", "")
                link = item.get("link", "")
                tipo = item.get("tipo") or item.get("keyword", "")
                self.tree_af.insert("", tk.END, values=(nome, link, tipo))
        except Exception:
            pass

    def _adicionar_afiliado(self):
        nome = self.var_af_nome.get().strip()
        link = self.var_af_link.get().strip()
        tipo = self.var_af_tipo.get().strip()
        if not nome or not link:
            messagebox.showwarning("Aviso", "Preencha pelo menos Nome e Link.")
            return
        self.tree_af.insert("", tk.END, values=(nome, link, tipo))
        self.var_af_nome.set("")
        self.var_af_link.set("")

    def _remover_afiliado(self):
        sel = self.tree_af.selection()
        if sel:
            self.tree_af.delete(sel[0])

    def _salvar_afiliados(self):
        dados = []
        for iid in self.tree_af.get_children():
            nome, link, tipo = self.tree_af.item(iid, "values")
            dados.append({"nome_produto": nome, "link": link, "tipo": tipo, "imagem": ""})
        with open("afiliados.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Salvo", f"{len(dados)} afiliado(s) salvos em afiliados.json")

    # ────────────────────────────────────────────────────────────────────────
    # ABA: PIPELINE
    # ────────────────────────────────────────────────────────────────────────

    def _build_pipeline_tab(self):
        outer = tk.Frame(self.tab_pipeline, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._tab_info_banner(
            outer,
            "🚀  Pipeline MakerWorld → WordPress",
            "Automação em lote: coleta modelos do MakerWorld via scraping, gera HTML otimizado para SEO "
            "com blocos de monetização, permite selecionar imagens e publica no WordPress. "
            "Ideal para produção de 10+ posts/dia com conteúdo de modelos 3D.",
            ["Coletar modelos (scraping)", "Gerar posts HTML", "Selecionar imagens", "Publicar no WP"],
        )

        ctrl = tk.Frame(outer, bg=BG2, padx=12, pady=10)
        ctrl.pack(fill=tk.X, pady=(0, 10))

        tk.Label(ctrl, text="Limite:", bg=BG2, fg=TEXT, font=FONT).pack(side=tk.LEFT)
        self.var_limite = tk.StringVar(value="10")
        ttk.Spinbox(ctrl, from_=1, to=100, textvariable=self.var_limite,
                    width=6).pack(side=tk.LEFT, padx=(4, 16))

        self.var_top10 = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl, text="Gerar Top 10", variable=self.var_top10).pack(
            side=tk.LEFT, padx=(0, 16))

        tk.Label(ctrl, text="Status:", bg=BG2, fg=TEXT, font=FONT).pack(side=tk.LEFT)
        self.var_status_run = tk.StringVar(value="draft")
        ttk.Combobox(ctrl, textvariable=self.var_status_run,
                     values=["draft", "publish"], state="readonly", width=10).pack(
            side=tk.LEFT, padx=(4, 0))

        # Botões de ação
        btns = tk.Frame(outer, bg=BG)
        btns.pack(fill=tk.X, pady=(0, 10))

        self.btn_coletar = ttk.Button(btns, text="📥  Coletar",
                                       command=lambda: self._run("coletar"))
        self.btn_coletar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_gerar = ttk.Button(btns, text="📝  Gerar Posts",
                                     command=lambda: self._run("gerar"))
        self.btn_gerar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_imagens = ttk.Button(btns, text="📸  Imagens",
                                       command=self._selecionar_imagens)
        self.btn_imagens.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_publicar = ttk.Button(btns, text="🚀  Publicar",
                                        command=lambda: self._run("publicar"),
                                        style="Run.TButton")
        self.btn_publicar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_pipeline = ttk.Button(btns, text="▶  Pipeline Completo",
                                        command=lambda: self._run("completo"),
                                        style="Run.TButton")
        self.btn_pipeline.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_manuais = ttk.Button(btns, text="✍️  Posts Manuais",
                                       command=lambda: self._run("manuais"))
        self.btn_manuais.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(btns, text="🧹  Limpar Log",
                   command=self._clear_log).pack(side=tk.RIGHT)

        # Área de log
        log_frame = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, bg="#0d0d1a", fg="#c8ffc8",
                                 font=FONT_MONO, wrap=tk.WORD,
                                 state=tk.DISABLED, relief=tk.FLAT)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config("ok",      foreground="#69ff69")
        self.log_text.tag_config("err",     foreground="#ff6969")
        self.log_text.tag_config("warn",    foreground="#ffcc00")
        self.log_text.tag_config("info",    foreground="#69c8ff")
        self.log_text.tag_config("heading", foreground=WHITE, font=("Consolas", 9, "bold"))

        bottom = tk.Frame(outer, bg=BG)
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.progress = ttk.Progressbar(bottom, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_status = tk.Label(bottom, text="Pronto.", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_status.pack(side=tk.LEFT)

    # ── Seleção manual de imagens ─────────────────────────────────────────────

    def _selecionar_imagens(self):
        pub_path = Path("posts_gerados.json")
        if not pub_path.exists():
            messagebox.showwarning("Aviso", "Nenhum post gerado. Execute 'Gerar Posts' primeiro.")
            return
        with open(pub_path, encoding="utf-8") as f:
            posts = json.load(f)
        if not posts:
            messagebox.showinfo("Info", "posts_gerados.json está vazio.")
            return
        status = self._carregar_status()
        pendentes = [p for p in posts if status.get(p.get("slug")) != "publicado"]
        if not pendentes:
            messagebox.showinfo("Info", "Todos os posts já foram publicados.")
            return
        self._abrir_dialog_imagens(pendentes, pub_path)

    def _abrir_dialog_imagens(self, posts: list, pub_path: Path):
        dlg = tk.Toplevel(self)
        dlg.title(f"Imagens para {len(posts)} post(s)")
        dlg.geometry("800x600")
        dlg.configure(bg=BG)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="📸  Selecione as imagens para cada post",
                 bg=BG, fg=WHITE, font=FONT_TITLE).pack(pady=(14, 2), padx=16, anchor=tk.W)
        tk.Label(dlg, text="Foto 1 será a imagem destacada. Adicione mais fotos para distribuir no post.",
                 bg=BG, fg=TEXT_DIM, font=FONT).pack(pady=(0, 10), padx=16, anchor=tk.W)

        wrapper = tk.Frame(dlg, bg=BG)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=16)

        canvas = tk.Canvas(wrapper, bg=BG2, highlightthickness=0)
        vsb = ttk.Scrollbar(wrapper, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG2)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        img_lists = []

        for i, post in enumerate(posts):
            bg_row = BG2 if i % 2 == 0 else BG3
            row = tk.Frame(inner, bg=bg_row, pady=7, padx=10)
            row.pack(fill=tk.X)

            titulo = post.get("titulo", post.get("slug", ""))[:60]
            tk.Label(row, text=f"{i+1}. {titulo}",
                     bg=bg_row, fg=WHITE, font=FONT_BOLD, anchor=tk.W).pack(fill=tk.X)

            imagens_atuais = post.get("imagens_lista", [])
            if post.get("featured_image_path") and not imagens_atuais:
                imagens_atuais = [post.get("featured_image_path")]

            vars_imagens = []
            frame_imagens = tk.Frame(row, bg=bg_row)
            frame_imagens.pack(fill=tk.X, pady=(3, 0))

            def add_field_img(frame, vars_list, idx, caminho=""):
                inp = tk.Frame(frame, bg=bg_row)
                inp.pack(fill=tk.X, pady=(2, 0))

                lbl_num = "Foto 1 (destaque + corpo)" if idx == 0 else f"Foto {idx + 1}"
                tk.Label(inp, text=lbl_num, bg=bg_row, fg=TEXT_DIM, font=("Segoe UI", 8),
                         width=18, anchor=tk.W).pack(side=tk.LEFT)

                var = tk.StringVar(value=caminho)
                vars_list.append(var)

                ttk.Entry(inp, textvariable=var, width=45).pack(side=tk.LEFT)

                def browse_img_inner(v=var):
                    path = filedialog.askopenfilename(
                        title="Selecionar imagem",
                        filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")])
                    if path:
                        v.set(path)

                ttk.Button(inp, text="📂", width=3, command=browse_img_inner).pack(side=tk.LEFT, padx=(4, 2))
                ttk.Button(inp, text="✕", width=2,
                           command=lambda v=var: v.set("")).pack(side=tk.LEFT)

            for j, caminho in enumerate(imagens_atuais):
                add_field_img(frame_imagens, vars_imagens, j, caminho)

            btn_add = tk.Frame(row, bg=bg_row)
            btn_add.pack(fill=tk.X, pady=(2, 0))
            ttk.Button(btn_add, text="➕ Adicionar foto",
                       command=lambda f=frame_imagens, vl=vars_imagens: add_field_img(f, vl, len(vl))).pack(side=tk.LEFT)

            img_lists.append((post.get("slug"), vars_imagens))

        footer = tk.Frame(dlg, bg=BG, pady=12)
        footer.pack(fill=tk.X, padx=16)

        def salvar():
            with open(pub_path, encoding="utf-8") as f:
                todos = json.load(f)

            mapa = {}
            for slug, vars_imagens in img_lists:
                imgs = [v.get().strip() for v in vars_imagens if v.get().strip()]
                mapa[slug] = imgs

            for p in todos:
                slug = p.get("slug", "")
                imgs = mapa.get(slug, [])

                if imgs:
                    p["imagens_lista"] = imgs
                    p["featured_image_path"] = imgs[0]
                else:
                    if "imagens_lista" in p:
                        del p["imagens_lista"]
                    if "featured_image_path" in p:
                        del p["featured_image_path"]

            with open(pub_path, "w", encoding="utf-8") as f:
                json.dump(todos, f, indent=2, ensure_ascii=False)

            n_posts = sum(1 for _, imgs in mapa.items() if imgs)
            total_imgs = sum(len(imgs) for imgs in mapa.values())
            messagebox.showinfo("Salvo", f"Imagens definidas para {n_posts} post(s) ({total_imgs} total).\nClique em Publicar para enviar.")
            dlg.destroy()

        ttk.Button(footer, text="💾  Salvar Seleção",
                   command=salvar, style="Run.TButton").pack(side=tk.LEFT)
        ttk.Button(footer, text="Cancelar",
                   command=dlg.destroy).pack(side=tk.LEFT, padx=10)

    # ────────────────────────────────────────────────────────────────────────
    # ABA: POSTS PUBLICADOS
    # ────────────────────────────────────────────────────────────────────────

    def _build_posts_tab_ui(self):
        outer = tk.Frame(self.tab_posts, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(outer, bg=BG)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(toolbar, text="🔄  Atualizar",
                   command=self._load_posts_tab).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="🌐  Abrir Blog",
                   command=lambda: webbrowser.open("https://clube3dbrasil.com")).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="🗑️  Apagar selecionados",
                   command=self._apagar_post_selecionado).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="🧹  Limpar tudo",
                   command=self._limpar_lista_posts).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_total = tk.Label(toolbar, text="", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_total.pack(side=tk.RIGHT)

        cols = ("wp_id", "titulo", "status", "url", "gerado_em")
        self.tree = ttk.Treeview(outer, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("wp_id",     text="ID WP")
        self.tree.heading("titulo",    text="Título")
        self.tree.heading("status",    text="Status")
        self.tree.heading("url",       text="URL")
        self.tree.heading("gerado_em", text="Publicado em")
        self.tree.column("wp_id",     width=60,  anchor=tk.CENTER)
        self.tree.column("titulo",    width=340)
        self.tree.column("status",    width=70,  anchor=tk.CENTER)
        self.tree.column("url",       width=300)
        self.tree.column("gerado_em", width=130, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self._abrir_post_url)

    # ── Config ────────────────────────────────────────────────────────────────

    def _carregar_env(self):
        env_path = Path(".env")
        if not env_path.exists():
            return
        for linha in env_path.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            os.environ[chave.strip()] = valor.strip()

    def _load_config(self):
        self._carregar_env()
        cfg_path = Path("config.json")
        if cfg_path.exists():
            with open(cfg_path, encoding="utf-8") as f:
                self.config_data = json.load(f)
        else:
            self.config_data = {}

        self.config_data["wp_user"]         = os.environ.get("WP_USER", self.config_data.get("wp_user", ""))
        self.config_data["wp_app_password"] = os.environ.get("WP_PASS",  self.config_data.get("wp_app_password", ""))

        defaults = {
            "wp_url": "https://clube3dbrasil.com", "wp_user": "",
            "wp_app_password": "", "ml_afiliado_url": "",
            "planilha_path": "", "posts_por_dia": 10, "wp_post_status": "draft",
        }
        for k, v in defaults.items():
            self.config_data.setdefault(k, v)

        for key, var in self._cfg_vars.items():
            val = self.config_data.get(key, "")
            var.set(str(val))

    def _save_config(self, notify: bool = False):
        CRED_KEYS = {"wp_user", "wp_app_password"}
        for key, var in self._cfg_vars.items():
            val = var.get().strip()
            if key == "posts_por_dia":
                self.config_data[key] = int(val) if val else 1
            else:
                self.config_data[key] = val

        env_path = Path(".env")
        linhas = [l for l in (env_path.read_text(encoding="utf-8").splitlines()
                               if env_path.exists() else [])
                  if l.split("=")[0].strip() not in ("WP_USER", "WP_PASS")]
        linhas += [f"WP_USER={self.config_data.get('wp_user','')}",
                   f"WP_PASS={self.config_data.get('wp_app_password','')}"]
        env_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")

        config_sem_creds = {k: v for k, v in self.config_data.items() if k not in CRED_KEYS}
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config_sem_creds, f, indent=2, ensure_ascii=False)

        if notify:
            messagebox.showinfo("Salvo", "Configurações salvas com sucesso!")

    def _load_posts_tab(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        pub_path = Path("posts_publicados.json")
        if not pub_path.exists():
            self.lbl_total.config(text="Nenhum post publicado ainda.")
            return
        with open(pub_path, encoding="utf-8") as f:
            posts = json.load(f)
        for p in reversed(posts):
            self.tree.insert("", tk.END, values=(
                p.get("wp_id", "—"), p.get("titulo", "")[:60],
                p.get("status", "draft"), p.get("url", ""),
                p.get("gerado_em", "")[:16] if p.get("gerado_em") else "—",
            ))
        self.lbl_total.config(text=f"Total: {len(posts)} post(s)")

    def _abrir_post_url(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        url = self.tree.item(sel[0], "values")[3]
        if url and url.startswith("http"):
            webbrowser.open(url)

    def _apagar_post_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um ou mais posts na lista.")
            return
        qtd = len(sel)
        if not messagebox.askyesno("Confirmar", f"Remover {qtd} post(s) do historico?\n\n(O post no WordPress nao sera afetado.)"):
            return
        ids = {self.tree.item(item, "values")[0] for item in sel}
        pub_path = Path("posts_publicados.json")
        if pub_path.exists():
            posts = json.loads(pub_path.read_text(encoding="utf-8"))
            posts = [p for p in posts if str(p.get("wp_id", "")) not in ids]
            pub_path.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
        self._load_posts_tab()

    def _limpar_lista_posts(self):
        if not messagebox.askyesno("Confirmar", "Limpar todo o historico de posts?\n\n(Os posts no WordPress nao serao afetados.)"):
            return
        pub_path = Path("posts_publicados.json")
        pub_path.write_text("[]", encoding="utf-8")
        self._load_posts_tab()

    # ── Pipeline ──────────────────────────────────────────────────────────────

    def _testar_conexao(self):
        self._save_config()
        self.nb.select(self.tab_pipeline)
        self._run("testar")

    def _run(self, mode: str):
        if self.running:
            messagebox.showwarning("Aguarde", "Uma operação já está em andamento.")
            return
        self._save_config()
        self.nb.select(self.tab_pipeline)
        self.running = True
        self._set_buttons(False)
        self.progress.start(12)
        self.lbl_status.config(text=f"Executando: {mode}...")
        threading.Thread(target=self._worker, args=(mode,), daemon=True).start()

    def _worker(self, mode: str):
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)
        try:
            self._log_heading(f"{'=' * 55}")
            self._log_heading(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}  —  Modo: {mode.upper()}")
            self._log_heading(f"{'=' * 55}")

            cfg = self._ler_config_atual()

            if mode == "testar":
                self._testar_wp(cfg)

            elif mode == "coletar":
                from scraper import MakerWorldScraper
                scraper = MakerWorldScraper(cfg)
                scraper.run(limite=int(self.var_limite.get() or 10))

            elif mode == "gerar":
                self._etapa_gerar(cfg)

            elif mode == "publicar":
                self._etapa_publicar(cfg)

            elif mode == "manuais":
                import gerar_posts_manuais, importlib
                importlib.reload(gerar_posts_manuais)
                gerar_posts_manuais.main()

            elif mode == "completo":
                from scraper import MakerWorldScraper
                limite = int(self.var_limite.get() or 10)

                print("📥 ETAPA 1 — Coletando modelos...")
                modelos = MakerWorldScraper(cfg).run(limite=limite)
                if not modelos:
                    modelos = self._carregar_modelos_pendentes(cfg, limite)
                    if modelos:
                        print(f"  ℹ️  Usando {len(modelos)} modelo(s) já coletado(s).")

                if not modelos:
                    print("⚠️  Nenhum modelo disponível. Verifique a planilha.")
                else:
                    print(f"\n✅ {len(modelos)} modelo(s)\n")
                    print("📝 ETAPA 2 — Gerando posts...")
                    from gerador import GeradorPostsV2 as GeradorPosts
                    cfg["wp_post_status"] = self.var_status_run.get()
                    posts = GeradorPosts(cfg).processar_lote(modelos, gerar_top10=self.var_top10.get())
                    with open("posts_gerados.json", "w", encoding="utf-8") as f:
                        json.dump(posts, f, indent=2, ensure_ascii=False)
                    print(f"\n✅ {len(posts)} post(s) gerado(s)")
                    print("\nℹ️  Use o botão 📸 Imagens para selecionar imagens antes de publicar.")

        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            self.running = False
            self.after(0, self._on_done)

    def _testar_wp(self, cfg: dict):
        from publisher import WordPressPublisher
        WordPressPublisher(cfg).testar_conexao()

    def _etapa_gerar(self, cfg: dict):
        from gerador import GeradorPostsV2 as GeradorPosts
        modelos = self._carregar_modelos_pendentes(cfg, int(self.var_limite.get() or 10))
        if not modelos:
            print("⚠️  Nenhum modelo coletado para gerar posts.")
            return
        cfg["wp_post_status"] = self.var_status_run.get()
        posts = GeradorPosts(cfg).processar_lote(modelos, gerar_top10=self.var_top10.get())
        with open("posts_gerados.json", "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"\n✅ {len(posts)} post(s) salvo(s) em posts_gerados.json")
        print("ℹ️  Use o botão 📸 Imagens para selecionar imagens antes de publicar.")

    def _etapa_publicar(self, cfg: dict, posts: list = None):
        from publisher import WordPressPublisher

        if posts is None:
            pub_path = Path("posts_gerados.json")
            if not pub_path.exists():
                print("⚠️  posts_gerados.json não encontrado.")
                return
            with open(pub_path, encoding="utf-8") as f:
                todos = json.load(f)
            status_data = self._carregar_status()
            posts = [p for p in todos if status_data.get(p.get("slug")) != "publicado"]

        if not posts:
            print("⚠️  Nenhum post pendente de publicação.")
            return

        cfg["wp_post_status"] = self.var_status_run.get()
        publicados = WordPressPublisher(cfg).publicar_lote(posts)

        if publicados:
            hist_path = Path("posts_publicados.json")
            historico = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else []
            for p in publicados:
                p["gerado_em"] = datetime.now().isoformat()
            historico.extend(publicados)
            hist_path.write_text(json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8")

            status_data = self._carregar_status()
            for p in publicados:
                status_data[p["slug"]] = "publicado"
            Path("status.json").write_text(
                json.dumps(status_data, indent=2, ensure_ascii=False), encoding="utf-8")

            self.after(0, self._load_posts_tab)

    def _carregar_modelos_pendentes(self, cfg: dict, limite: int) -> list[dict]:
        downloads_dir = Path(cfg.get("downloads_dir", "./downloads"))
        status = self._carregar_status()
        modelos = []
        for meta_file in sorted(downloads_dir.glob("*/meta.json")):
            slug = meta_file.parent.name
            if status.get(slug) in ("coletado", "erro_geracao"):
                with open(meta_file, encoding="utf-8") as f:
                    modelos.append(json.load(f))
            if len(modelos) >= limite:
                break
        return modelos

    def _carregar_status(self) -> dict:
        p = Path("status.json")
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    def _ler_config_atual(self) -> dict:
        self._carregar_env()
        cfg_path = Path("config.json")
        config = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else self.config_data.copy()
        config["wp_user"]         = os.environ.get("WP_USER", config.get("wp_user", ""))
        config["wp_app_password"] = os.environ.get("WP_PASS",  config.get("wp_app_password", ""))
        return config

    # ── Log ───────────────────────────────────────────────────────────────────

    def _log_heading(self, text: str):
        self.log_queue.put(("__heading__", text))

    def _poll_log(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                if isinstance(item, tuple) and item[0] == "__heading__":
                    self.log_text.insert(tk.END, item[1] + "\n", "heading")
                else:
                    tag = "ok"
                    lo = item.lower()
                    if "❌" in item or "erro" in lo or "error" in lo:
                        tag = "err"
                    elif "⚠️" in item or "aviso" in lo or "warn" in lo:
                        tag = "warn"
                    elif "ℹ️" in item or "etapa" in lo or "==" in item:
                        tag = "info"
                    self.log_text.insert(tk.END, item, tag)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(80, self._poll_log)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _set_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self.btn_coletar, self.btn_gerar, self.btn_imagens,
                    self.btn_publicar, self.btn_pipeline, self.btn_manuais):
            btn.config(state=state)

    def _on_done(self):
        self.progress.stop()
        self.lbl_status.config(text="Concluído.")
        self._set_buttons(True)
        self._load_posts_tab()
        self._dashboard_refresh()

    def _on_tab_change(self, _event=None):
        try:
            selected = self.nb.tab(self.nb.select(), "text")
            if "Dashboard" in selected:
                self._dashboard_refresh()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────────────────
    # BANNER RESUMO DE ABA
    # ────────────────────────────────────────────────────────────────────────

    def _tab_info_banner(self, parent, titulo: str, descricao: str, passos=None):
        """Faixa informativa no topo de cada aba: borda ACCENT2 + título + descrição + passos opcionais."""
        wrapper = tk.Frame(parent, bg=ACCENT2, padx=3, pady=0)
        wrapper.pack(fill=tk.X, pady=(0, 12))
        inner = tk.Frame(wrapper, bg=BG2, padx=14, pady=10)
        inner.pack(fill=tk.X)
        tk.Label(inner, text=titulo, bg=BG2, fg=WHITE,
                 font=FONT_BOLD, anchor=tk.W).pack(anchor=tk.W)
        tk.Label(inner, text=descricao, bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9), wraplength=960,
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(3, 0))
        if passos:
            nums = "①②③④⑤⑥"
            txt = "   →   ".join(f"{nums[i]} {p}" for i, p in enumerate(passos))
            tk.Label(inner, text=txt, bg=BG2, fg=ACCENT2,
                     font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(6, 0))

    # ────────────────────────────────────────────────────────────────────────
    # ABA: DASHBOARD
    # ────────────────────────────────────────────────────────────────────────

    ORANGE = "#FF6200"

    _CLUSTERS_DEF = [
        ("01", "STL Geek",    "Anime · Games · Filmes · Funko Pop",            20),
        ("02", "Iniciantes",  "Cura · Orca · Configurações · Primeiros passos", 20),
        ("03", "Filamentos",  "PLA · PETG · ABS · TPU · Resina",               20),
        ("04", "Renda Extra", "Shopee · Elo7 · Afiliados · Monetização",        20),
    ]

    def _build_dashboard_tab(self):
        outer = tk.Frame(self.tab_dash, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        # Barra superior
        act = tk.Frame(outer, bg=BG)
        act.pack(fill=tk.X, pady=(0, 14))
        tk.Label(act, text="Pipeline Overview — clube3dbrasil.com",
                 bg=BG, fg=WHITE, font=FONT_TITLE).pack(side=tk.LEFT)
        ttk.Button(act, text="🌐  Dashboard HTML",
                   command=self._dashboard_abrir_html).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(act, text="🔄  Atualizar",
                   command=self._dashboard_refresh).pack(side=tk.RIGHT)

        # KPIs
        kpi_row = tk.Frame(outer, bg=BG)
        kpi_row.pack(fill=tk.X, pady=(0, 14))

        self._dash_kpis = {}
        for key, label, color in [
            ("publicados", "Posts Publicados", SUCCESS),
            ("imagens",    "Imagens Geradas",  SUCCESS),
            ("pendentes",  "Posts Pendentes",  WARNING),
            ("clusters",   "Clusters Ativos",  ACCENT2),
        ]:
            card = tk.Frame(kpi_row, bg=BG2, padx=16, pady=12)
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
            tk.Label(card, text=label, bg=BG2, fg=TEXT_DIM,
                     font=("Segoe UI", 9)).pack(anchor=tk.W)
            lbl = tk.Label(card, text="—", bg=BG2, fg=color,
                           font=("Segoe UI", 28, "bold"))
            lbl.pack(anchor=tk.W)
            self._dash_kpis[key] = lbl

        # Cluster cards
        tk.Label(outer, text="CLUSTERS DE CONTEÚDO", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8)).pack(anchor=tk.W, pady=(0, 6))

        grid = tk.Frame(outer, bg=BG)
        grid.pack(fill=tk.X, pady=(0, 14))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._dash_clusters = {}
        for i, (num, name, desc, total) in enumerate(self._CLUSTERS_DEF):
            row, col = divmod(i, 2)
            card = tk.Frame(grid, bg=BG2, padx=14, pady=10)
            card.grid(row=row, column=col, sticky=tk.EW,
                      padx=(0 if col == 0 else 8, 0), pady=(0, 8))

            tk.Label(card, text=f"CLUSTER {num}", bg=BG2, fg=TEXT_DIM,
                     font=("Segoe UI", 8)).pack(anchor=tk.W)
            tk.Label(card, text=name, bg=BG2, fg=WHITE,
                     font=FONT_BOLD).pack(anchor=tk.W, pady=(3, 1))
            tk.Label(card, text=desc, bg=BG2, fg=TEXT_DIM,
                     font=("Segoe UI", 8)).pack(anchor=tk.W)

            pb = ttk.Progressbar(card, maximum=total, mode="determinate")
            pb.pack(fill=tk.X, pady=(8, 3))

            lbl_p = tk.Label(card, text=f"0/{total}", bg=BG2,
                             fg=TEXT_DIM, font=("Segoe UI", 9))
            lbl_p.pack(anchor=tk.W)
            self._dash_clusters[num] = {"pb": pb, "lbl": lbl_p, "total": total}

        # Tabela últimos posts
        tk.Label(outer, text="ÚLTIMOS POSTS PUBLICADOS", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8)).pack(anchor=tk.W, pady=(0, 6))

        tbl_wrap = tk.Frame(outer, bg=BG3, padx=1, pady=1)
        tbl_wrap.pack(fill=tk.BOTH, expand=True)

        cols = ("wp_id", "titulo", "cluster", "data")
        self.dash_tree = ttk.Treeview(tbl_wrap, columns=cols,
                                       show="headings", selectmode="browse", height=7)
        self.dash_tree.heading("wp_id",   text="ID WP")
        self.dash_tree.heading("titulo",  text="Título")
        self.dash_tree.heading("cluster", text="Cluster")
        self.dash_tree.heading("data",    text="Publicado em")
        self.dash_tree.column("wp_id",   width=65,  anchor=tk.CENTER)
        self.dash_tree.column("titulo",  width=400)
        self.dash_tree.column("cluster", width=100, anchor=tk.CENTER)
        self.dash_tree.column("data",    width=120, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tbl_wrap, orient=tk.VERTICAL, command=self.dash_tree.yview)
        self.dash_tree.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.dash_tree.pack(fill=tk.BOTH, expand=True)
        self.dash_tree.bind("<Double-1>", self._dash_open_url)

    def _dashboard_refresh(self):
        pub_path = Path("posts_publicados.json")
        publicados = (json.loads(pub_path.read_text(encoding="utf-8"))
                      if pub_path.exists() else [])

        total = len(publicados)
        c1 = sum(1 for p in publicados
                 if p.get("cluster") == "STL Geek"
                 or (isinstance(p.get("wp_id"), int) and 2764 <= p["wp_id"] <= 2802))

        clusters_ativos = 1 if c1 > 0 else 0

        self._dash_kpis["publicados"].config(text=str(total))
        self._dash_kpis["imagens"].config(text=str(c1))
        self._dash_kpis["pendentes"].config(text=str(max(0, 80 - total)))
        self._dash_kpis["clusters"].config(text=str(clusters_ativos))

        # Cluster 1
        self._dash_clusters["01"]["pb"]["value"] = c1
        self._dash_clusters["01"]["lbl"].config(
            text=f"{c1}/20",
            fg=SUCCESS if c1 >= 20 else WARNING)

        # Clusters 2-4 sem dados ainda
        for num in ("02", "03", "04"):
            self._dash_clusters[num]["pb"]["value"] = 0
            self._dash_clusters[num]["lbl"].config(text="0/20", fg=TEXT_DIM)

        # Tabela
        for row in self.dash_tree.get_children():
            self.dash_tree.delete(row)
        for p in list(reversed(publicados))[:25]:
            cluster = p.get("cluster", "—")
            data    = (p.get("gerado_em", "")[:10] if p.get("gerado_em") else "—")
            self.dash_tree.insert("", tk.END, values=(
                p.get("wp_id", "—"),
                p.get("titulo", "")[:60],
                cluster,
                data,
            ))

    def _dash_open_url(self, _event=None):
        sel = self.dash_tree.selection()
        if not sel:
            return
        wp_id = str(self.dash_tree.item(sel[0], "values")[0])
        pub_path = Path("posts_publicados.json")
        if not pub_path.exists():
            return
        for p in json.loads(pub_path.read_text(encoding="utf-8")):
            if str(p.get("wp_id", "")) == wp_id:
                url = p.get("url", "")
                if url:
                    webbrowser.open(url)
                break

    def _dashboard_abrir_html(self):
        dash_path = Path("dashboard.html")
        if dash_path.exists():
            webbrowser.open(dash_path.resolve().as_uri())
        else:
            messagebox.showwarning("Aviso", "dashboard.html não encontrado na pasta do projeto.")

    # ────────────────────────────────────────────────────────────────────────
    # ABA: POST SEO (Claude API)
    # ────────────────────────────────────────────────────────────────────────

    def _build_seo_tab(self):
        outer = tk.Frame(self.tab_seo, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._tab_info_banner(
            outer,
            "✍️  Post SEO — Artigo Editorial via Claude AI",
            "Gera artigo editorial completo em PT-BR via Claude API (modelo Haiku). "
            "Extrai título e transcrição do YouTube, detecta o tema do cluster SEO, injeta interlinks automáticos "
            "de posts relacionados e cria bloco FAQ com JSON-LD. Custo médio: ~$0,008 por post.",
            ["Colar URL do YouTube", "Extrair transcrição", "Gerar post PT-BR (Claude)", "Selecionar imagem", "Publicar"],
        )

        # --- Inputs ---
        inputs = tk.Frame(outer, bg=BG2, padx=12, pady=10)
        inputs.pack(fill=tk.X, pady=(0, 8))

        row0 = tk.Frame(inputs, bg=BG2)
        row0.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row0, text="YouTube URL:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_seo_url = tk.StringVar()
        ttk.Entry(row0, textvariable=self.var_seo_url, width=48).pack(side=tk.LEFT, padx=(0, 8))
        self.btn_seo_auto = ttk.Button(row0, text="🤖  Gerar Automático",
                                        command=self._seo_gerar_automatico,
                                        style="Run.TButton")
        self.btn_seo_auto.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_seo_extrair = ttk.Button(row0, text="📥  Extrair Transcrição",
                                           command=self._seo_extrair_transcricao)
        self.btn_seo_extrair.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_seo_colar = ttk.Button(row0, text="📋  Colar Transcrição",
                                         command=self._seo_colar_transcricao)
        self.btn_seo_colar.pack(side=tk.LEFT)

        # Linha de comando pronto para terminal
        row_cmd = tk.Frame(inputs, bg=BG2)
        row_cmd.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row_cmd, text="Comando terminal:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_seo_cmd = tk.StringVar()
        cmd_entry = ttk.Entry(row_cmd, textvariable=self.var_seo_cmd, width=52,
                              state="readonly", font=FONT_MONO)
        cmd_entry.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(row_cmd, text="⚡ Gerar",
                   command=self._seo_gerar_comando).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(row_cmd, text="📋 Copiar",
                   command=self._seo_copiar_comando).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(row_cmd, text="✕ Apagar",
                   command=self._seo_apagar_comando).pack(side=tk.LEFT)

        row1 = tk.Frame(inputs, bg=BG2)
        row1.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row1, text="Keyword alvo:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_seo_keyword = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_seo_keyword, width=44).pack(side=tk.LEFT)

        row2 = tk.Frame(inputs, bg=BG2)
        row2.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row2, text="Keywords sec.:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_seo_secondary = tk.StringVar()
        ttk.Entry(row2, textvariable=self.var_seo_secondary, width=44).pack(side=tk.LEFT)
        tk.Label(row2, text="(separadas por vírgula)", bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 0))

        row_cat = tk.Frame(inputs, bg=BG2)
        row_cat.pack(fill=tk.X, pady=(0, 2))
        tk.Label(row_cat, text="Categoria:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_seo_categoria = tk.StringVar(value="STL Geek")
        cat_combo = ttk.Combobox(
            row_cat, textvariable=self.var_seo_categoria, width=30,
            values=["STL Geek", "Impressao 3D", "Renda Extra", "Filamentos",
                    "Para Iniciantes", "Impressoras 3D", "Modelagem 3D",
                    "Tecnicas", "Reviews", "Financas", "Marketing Digital",
                    "Ganhar Dinheiro Online"],
            state="readonly",
        )
        cat_combo.pack(side=tk.LEFT)
        tk.Label(row_cat, text="(Financas / Marketing Digital / Ganhar Dinheiro Online: post sem impressao 3D)",
                 bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 0))

        # Idioma fixo: PT-BR
        row_lang = tk.Frame(inputs, bg=BG2)
        row_lang.pack(fill=tk.X, pady=(6, 2))
        tk.Label(row_lang, text="Idioma:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(row_lang, text="Portugues Brasileiro (PT-BR)", bg=BG2, fg=TEXT, font=FONT_BOLD).pack(side=tk.LEFT)

        # Afiliados
        row_af = tk.Frame(inputs, bg=BG2)
        row_af.pack(fill=tk.X, pady=(4, 2))
        tk.Label(row_af, text="Afiliados:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Button(row_af, text="📂 Carregar Planilha",
                   command=self._seo_carregar_planilha_afiliados).pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_seo_af_status = tk.Label(row_af, text="Nenhuma planilha carregada",
                                           bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9))
        self.lbl_seo_af_status.pack(side=tk.LEFT)

        # Transcrição manual
        tk.Label(outer,
                 text="Transcrição (opcional — cole manualmente ou use o botão acima):",
                 bg=BG, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W, pady=(0, 4))
        tf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        tf.pack(fill=tk.X, pady=(0, 8))
        self.seo_transcript = tk.Text(tf, bg=BG2, fg=TEXT, font=FONT_MONO,
                                       height=5, wrap=tk.WORD, relief=tk.FLAT)
        ts = ttk.Scrollbar(tf, command=self.seo_transcript.yview)
        self.seo_transcript.configure(yscrollcommand=ts.set)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.seo_transcript.pack(fill=tk.X)

        # Botões de ação
        btns = tk.Frame(outer, bg=BG)
        btns.pack(fill=tk.X, pady=(0, 8))

        self.btn_seo_gerar = ttk.Button(btns, text="🤖  Gerar Post SEO",
                                         command=self._seo_gerar,
                                         style="Run.TButton")
        self.btn_seo_gerar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_seo_imagem = ttk.Button(btns, text="🖼️  Imagem",
                                          command=self._seo_selecionar_imagem)
        self.btn_seo_imagem.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_seo_publicar = ttk.Button(btns, text="🚀  Publicar",
                                            command=self._seo_publicar,
                                            style="Run.TButton")
        self.btn_seo_publicar.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btns, text="🧹  Limpar",
                   command=self._seo_limpar).pack(side=tk.RIGHT)

        # Preview do resultado
        pf = tk.Frame(outer, bg=BG2, padx=10, pady=8)
        pf.pack(fill=tk.X, pady=(0, 8))
        tk.Label(pf, text="Resultado:", bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W)
        self.lbl_seo_titulo = tk.Label(pf, text="—", bg=BG2, fg=WHITE,
                                        font=FONT_BOLD, wraplength=700, justify=tk.LEFT)
        self.lbl_seo_titulo.pack(anchor=tk.W)
        self.lbl_seo_meta = tk.Label(pf, text="", bg=BG2, fg=TEXT_DIM,
                                      font=FONT, wraplength=700, justify=tk.LEFT)
        self.lbl_seo_meta.pack(anchor=tk.W)
        self.lbl_seo_imagem = tk.Label(pf, text="Imagem: nenhuma selecionada",
                                        bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9))
        self.lbl_seo_imagem.pack(anchor=tk.W, pady=(4, 0))

        # Log
        lf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        lf.pack(fill=tk.BOTH, expand=True)
        self.seo_log_text = tk.Text(lf, bg="#0d0d1a", fg="#c8ffc8",
                                     font=FONT_MONO, wrap=tk.WORD,
                                     state=tk.DISABLED, relief=tk.FLAT)
        seo_vsb = ttk.Scrollbar(lf, command=self.seo_log_text.yview)
        self.seo_log_text.configure(yscrollcommand=seo_vsb.set)
        self.seo_log_text.tag_config("ok",      foreground="#69ff69")
        self.seo_log_text.tag_config("err",     foreground="#ff6969")
        self.seo_log_text.tag_config("warn",    foreground="#ffcc00")
        self.seo_log_text.tag_config("info",    foreground="#69c8ff")
        self.seo_log_text.tag_config("heading", foreground=WHITE, font=("Consolas", 9, "bold"))
        seo_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.seo_log_text.pack(fill=tk.BOTH, expand=True)

        bot = tk.Frame(outer, bg=BG)
        bot.pack(fill=tk.X, pady=(8, 0))
        self.seo_progress = ttk.Progressbar(bot, mode="indeterminate", length=200)
        self.seo_progress.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_seo_status = tk.Label(bot, text="Pronto.", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_seo_status.pack(side=tk.LEFT)

    # ── Helpers SEO ────────────────────────────────────────────────────────────

    def _seo_log_append(self, msg: str):
        """Envia mensagem para a fila de log da aba SEO."""
        self.seo_log_queue.put(msg)

    def _poll_seo_log(self):
        try:
            while True:
                item = self.seo_log_queue.get_nowait()
                self.seo_log_text.config(state=tk.NORMAL)
                tag = "ok"
                lo = item.lower()
                if "❌" in item or "erro" in lo or "error" in lo or "falha" in lo:
                    tag = "err"
                elif "⚠️" in item or "aviso" in lo or "warn" in lo:
                    tag = "warn"
                elif "ℹ️" in item or "==" in item or "etapa" in lo:
                    tag = "info"
                self.seo_log_text.insert(tk.END, item + "\n", tag)
                self.seo_log_text.see(tk.END)
                self.seo_log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(80, self._poll_seo_log)

    def _seo_set_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self.btn_seo_auto, self.btn_seo_extrair, self.btn_seo_colar,
                    self.btn_seo_gerar, self.btn_seo_imagem, self.btn_seo_publicar):
            btn.config(state=state)

    def _seo_on_done(self):
        self.seo_progress.stop()
        self.lbl_seo_status.config(text="Concluído.")
        self._seo_set_buttons(True)

    # ── Extrair Transcrição ────────────────────────────────────────────────────

    def _seo_extrair_transcricao(self):
        url = self.var_seo_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Informe a URL do YouTube.")
            return
        if self.seo_running:
            return
        self.seo_running = True
        self._seo_set_buttons(False)
        self.seo_progress.start(12)
        self.lbl_seo_status.config(text="Extraindo transcrição...")
        threading.Thread(target=self._seo_extrair_worker, args=(url,), daemon=True).start()

    def _seo_extrair_worker(self, url: str):
        try:
            import seo_writer
            importlib.reload(seo_writer)
            transcript = seo_writer.extrair_transcricao_yt(url, log_fn=self._seo_log_append)
            if transcript:
                def update():
                    self.seo_transcript.delete("1.0", tk.END)
                    self.seo_transcript.insert("1.0", transcript)
                self.after(0, update)
            else:
                self._seo_log_append("  ⚠️  Sem transcrição automática. Cole o texto manualmente.")
        except Exception as e:
            self._seo_log_append(f"  ❌ Erro: {e}")
        finally:
            self.seo_running = False
            self.after(0, self._seo_on_done)

    # ── Gerar Post ─────────────────────────────────────────────────────────────

    def _seo_gerar(self):
        keyword = self.var_seo_keyword.get().strip()
        if not keyword:
            messagebox.showwarning("Aviso", "Informe a keyword alvo.")
            return
        if self.seo_running:
            return

        afiliados_sel = self._seo_selecionar_afiliados_dialog()
        if afiliados_sel is None and self.afiliados_carregados:
            return  # usuário cancelou o dialog

        self._carregar_env()
        self.seo_running = True
        self._seo_set_buttons(False)
        self.seo_progress.start(12)
        self.lbl_seo_status.config(text="Gerando post SEO via Claude API...")

        url        = self.var_seo_url.get().strip()
        sec_raw    = self.var_seo_secondary.get().strip()
        sec_kws    = [k.strip() for k in sec_raw.split(",") if k.strip()]
        transcript = self.seo_transcript.get("1.0", tk.END).strip()

        threading.Thread(
            target=self._seo_gerar_worker,
            args=(keyword, sec_kws, transcript, url, afiliados_sel),
            daemon=True,
        ).start()

    def _seo_gerar_worker(self, keyword, secondary_kws, transcript, youtube_url, afiliados_sel=None):
        try:
            import seo_writer
            importlib.reload(seo_writer)

            sep = "=" * 50
            self._seo_log_append(sep)
            self._seo_log_append(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')} — Gerando post SEO [PT-BR]")
            self._seo_log_append(sep)

            self.seo_post_gerado = None
            self._seo_log_append(f"  Keyword: {keyword}")

            post = seo_writer.gerar_post_seo(
                keyword=keyword,
                secondary_kws=secondary_kws,
                transcript=transcript,
                youtube_url=youtube_url,
                afiliados_override=afiliados_sel,
                log_fn=self._seo_log_append,
                categoria=self.var_seo_categoria.get(),
            )

            # Cluster SEO: detecta tema e injeta interlinks (ignorado para Financas)
            if self.var_seo_categoria.get().lower() not in ("financas", "finanças", "marketing digital", "ganhar dinheiro online"):
                from cluster import ClusterManager
                cluster = ClusterManager()
                tema = cluster.detectar_tema(keyword)
                post["_cluster_tema"] = tema
                interlinks = cluster.gerar_html_interlinks(tema, excluir_url="")
                if interlinks:
                    content = post.get("content", "")
                    script_pos = content.find('<script type="application/ld+json">')
                    if script_pos >= 0:
                        content = content[:script_pos] + interlinks + "\n" + content[script_pos:]
                    else:
                        content += interlinks
                    post["content"] = content
                    self._seo_log_append(f"  Interlinks injetados (tema: {tema})")
                else:
                    self._seo_log_append(f"  Tema: {tema} (sem posts relacionados ainda)")

            self.seo_post_gerado = post

            def update_preview():
                self.lbl_seo_titulo.config(text=post.get("titulo", ""))
                meta = post.get("yoast_meta", "")
                self.lbl_seo_meta.config(text=f"Meta ({len(meta)} chars): {meta}")
            self.after(0, update_preview)

            self._seo_log_append("\n  Post gerado. Selecione uma imagem e clique em Publicar.")
        except Exception as e:
            self._seo_log_append(f"\n  Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.seo_running = False
            self.after(0, self._seo_on_done)

    # ── Imagem ─────────────────────────────────────────────────────────────────

    def _seo_selecionar_imagem(self):
        if not self.seo_post_gerado:
            messagebox.showwarning("Aviso", "Gere o post antes de selecionar a imagem.")
            return
        path = filedialog.askopenfilename(
            title="Selecionar imagem destacada",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")],
        )
        if path:
            self.seo_post_gerado["featured_image_path"] = path
            self.lbl_seo_imagem.config(text=f"Imagem: {Path(path).name}")

    # ── Publicar ───────────────────────────────────────────────────────────────

    def _seo_publicar(self):
        if not self.seo_post_gerado:
            messagebox.showwarning("Aviso", "Nenhum post gerado. Clique em 'Gerar Post SEO' primeiro.")
            return
        if self.seo_running:
            return
        cfg = self._ler_config_atual()
        status = cfg.get("wp_post_status", "draft")
        titulo = self.seo_post_gerado.get("titulo", "")
        if not messagebox.askyesno("Confirmar", f"Publicar como '{status}'?\n\n{titulo}"):
            return
        self.seo_running = True
        self._seo_set_buttons(False)
        self.seo_progress.start(12)
        self.lbl_seo_status.config(text="Publicando no WordPress...")
        threading.Thread(target=self._seo_publicar_worker, daemon=True).start()

    def _seo_publicar_worker(self):
        try:
            from publisher import WordPressPublisher
            cfg    = self._ler_config_atual()
            status = cfg.get("wp_post_status", "draft")
            pub    = WordPressPublisher(cfg)

            hist_path = Path("posts_publicados.json")
            historico = (json.loads(hist_path.read_text(encoding="utf-8"))
                         if hist_path.exists() else [])

            p = dict(self.seo_post_gerado)
            p["status"] = status
            self._seo_log_append(f"  Publicando: {p.get('titulo','')[:55]}...")
            resultado = pub.publicar_post(p)
            if resultado:
                wp_id     = resultado.get("wp_id", "")
                post_url  = resultado.get("url", "")
                self._seo_log_append(f"  OK ID: {wp_id} — {post_url}")
                resultado["gerado_em"] = datetime.now().isoformat()
                resultado["titulo"]    = p.get("titulo", "")
                historico.append(resultado)

                # Cluster SEO: registrar post e verificar pilar
                tema = p.get("_cluster_tema", "")
                if tema:
                    from cluster import ClusterManager
                    cluster = ClusterManager()
                    cluster.adicionar_post(tema, {
                        "titulo": p.get("titulo", ""),
                        "url":    post_url,
                        "wp_id":  wp_id,
                    })
                    total = cluster.total_posts(tema)
                    self._seo_log_append(f"  Cluster '{tema}': {total} post(s) registrado(s)")
                    if total >= 3:
                        pilar = cluster.gerar_pilar(tema)
                        if pilar:
                            meta_pilar = f"Guia completo sobre {tema} na impressao 3D."
                            post_pilar = {
                                "titulo":          pilar["titulo"],
                                "slug":            pilar["slug"],
                                "content":         pilar["conteudo"],
                                "excerpt":         meta_pilar,
                                "status":          "draft",
                                "tags":            [tema, "impressao 3d", "guia completo"],
                                "categories":      [tema],
                                "yoast_keyphrase": f"impressao 3d {tema.lower()}",
                                "yoast_title":     pilar["titulo"],
                                "yoast_meta":      meta_pilar[:155],
                            }
                            try:
                                r_pilar = pub.publicar_post(post_pilar)
                                self._seo_log_append(
                                    f"  Pilar criado: {r_pilar.get('url', r_pilar.get('wp_id', ''))}")
                            except Exception as ep:
                                self._seo_log_append(f"  Pilar erro: {ep}")

            hist_path.write_text(
                json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            self.after(0, self._load_posts_tab)
        except Exception as e:
            self._seo_log_append(f"  Erro ao publicar: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.seo_running = False
            self.after(0, self._seo_on_done)

    # ── Comando Terminal ───────────────────────────────────────────────────────

    def _seo_gerar_comando(self):
        url = self.var_seo_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole a URL do YouTube primeiro.")
            return
        self.var_seo_cmd.set(f'python gerar_post_youtube.py "{url}"')

    def _seo_apagar_comando(self):
        self.var_seo_cmd.set("")

    def _seo_copiar_comando(self):
        cmd = self.var_seo_cmd.get().strip()
        if not cmd:
            self._seo_gerar_comando()
            cmd = self.var_seo_cmd.get().strip()
        if cmd:
            self.clipboard_clear()
            self.clipboard_append(cmd)
            messagebox.showinfo("Copiado", "Comando copiado para a área de transferência!")

    # ── Gerar Automático (só URL) ──────────────────────────────────────────────

    def _seo_gerar_automatico(self):
        url = self.var_seo_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole a URL do YouTube primeiro.")
            return
        if self.seo_running:
            return

        # Dialog de afiliados antes de travar os botões
        afiliados_sel = self._seo_selecionar_afiliados_dialog()
        if afiliados_sel is None and self.afiliados_carregados:
            return  # usuário cancelou

        self._carregar_env()
        self.seo_running = True
        self._seo_set_buttons(False)
        self.seo_progress.start(12)
        self.lbl_seo_status.config(text="Processando automaticamente...")
        manual_transcript = self.seo_transcript.get("1.0", tk.END).strip()
        threading.Thread(
            target=self._seo_auto_worker,
            args=(url, manual_transcript, afiliados_sel),
            daemon=True,
        ).start()

    def _seo_auto_worker(self, url: str, manual_transcript: str = "", afiliados_sel=None):
        try:
            from gerar_post_youtube import extrair_metadados_yt, titulo_para_keyword, gerar_secondary_kws
            import seo_writer
            importlib.reload(seo_writer)

            # 1. Metadados
            self._seo_log_append("  [1/3] Obtendo titulo e descricao do video...")
            meta = extrair_metadados_yt(url)
            titulo_yt      = meta.get("title", "")
            yt_description = meta.get("description", "")
            if titulo_yt:
                self._seo_log_append(f"  Titulo original: {titulo_yt}")
                titulo_yt = seo_writer.traduzir_titulo_para_pt(titulo_yt, log_fn=self._seo_log_append)
            else:
                self._seo_log_append("  Titulo nao obtido — usando keyword generica.")
                titulo_yt = "impressao 3d"
            if yt_description:
                self._seo_log_append(f"  Descricao: {len(yt_description)} chars obtidos")

            keyword   = titulo_para_keyword(titulo_yt)
            secondary = gerar_secondary_kws(keyword, titulo_yt)

            self._seo_log_append(f"  Keyword: {keyword}")
            self._seo_log_append(f"  Secundarias: {', '.join(secondary)}")

            def update_fields():
                self.var_seo_keyword.set(keyword)
                self.var_seo_secondary.set(", ".join(secondary))
            self.after(0, update_fields)

            # 2. Transcricao (qualquer idioma — Claude escreve em PT-BR)
            self._seo_log_append("\n  [2/3] Extraindo transcricao...")
            transcript = seo_writer.extrair_transcricao_yt(url, log_fn=self._seo_log_append)
            if transcript:
                def update_transcript():
                    self.seo_transcript.delete("1.0", tk.END)
                    self.seo_transcript.insert("1.0", transcript)
                self.after(0, update_transcript)
            elif manual_transcript:
                transcript = manual_transcript
                self._seo_log_append("  Sem transcricao automatica — usando transcricao colada manualmente.")
            else:
                self._seo_log_append("  Sem transcricao — usando descricao como contexto.")

            # 3. Gerar post PT-BR
            self._seo_log_append("\n  [3/3] Gerando post SEO [PT-BR]...")
            self.seo_post_gerado = None

            post = seo_writer.gerar_post_seo(
                keyword=keyword, secondary_kws=secondary,
                transcript=transcript, youtube_url=url,
                yt_description=yt_description,
                afiliados_override=afiliados_sel,
                log_fn=self._seo_log_append,
                categoria=self.var_seo_categoria.get(),
            )

            # Cluster SEO: detecta tema e injeta interlinks (ignorado para Financas)
            if self.var_seo_categoria.get().lower() not in ("financas", "finanças", "marketing digital", "ganhar dinheiro online"):
                from cluster import ClusterManager
                cluster = ClusterManager()
                tema = cluster.detectar_tema(keyword, titulo_yt)
                post["_cluster_tema"] = tema
                interlinks = cluster.gerar_html_interlinks(tema, excluir_url="")
                if interlinks:
                    content = post.get("content", "")
                    script_pos = content.find('<script type="application/ld+json">')
                    if script_pos >= 0:
                        content = content[:script_pos] + interlinks + "\n" + content[script_pos:]
                    else:
                        content += interlinks
                    post["content"] = content
                    self._seo_log_append(f"  Interlinks injetados (tema: {tema})")
                else:
                    self._seo_log_append(f"  Tema: {tema} (sem posts relacionados ainda)")

            self.seo_post_gerado = post

            def update_preview():
                self.lbl_seo_titulo.config(text=post.get("titulo", ""))
                m = post.get("yoast_meta", "")
                self.lbl_seo_meta.config(text=f"Meta ({len(m)} chars): {m}")
            self.after(0, update_preview)

            self._seo_log_append("\n  Post pronto. Selecione imagem e clique em Publicar.")

        except Exception as e:
            self._seo_log_append(f"\n  Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.seo_running = False
            self.after(0, self._seo_on_done)

    # ── Planilha e Seleção de Afiliados ───────────────────────────────────────

    def _seo_carregar_planilha_afiliados(self):
        path = filedialog.askopenfilename(
            title="Selecionar planilha de afiliados",
            filetypes=[("Excel", "*.xlsx *.xls"), ("JSON", "*.json"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            if path.endswith(".json"):
                with open(path, encoding="utf-8") as f:
                    dados = json.load(f)
            else:
                import pandas as pd
                df = pd.read_excel(path)
                df.columns = [c.strip().lower() for c in df.columns]
                if "nome_produto" in df.columns and "nome" not in df.columns:
                    df.rename(columns={"nome_produto": "nome"}, inplace=True)
                dados = []
                for _, row in df.iterrows():
                    nome = str(row.get("nome", "")).strip()
                    link = str(row.get("link", "")).strip()
                    tipo = str(row.get("tipo", "")).strip()
                    if nome and link and link.lower() != "nan":
                        dados.append({"nome": nome, "link": link, "tipo": tipo})

            self.afiliados_carregados = dados
            n = len(dados)
            self.lbl_seo_af_status.config(
                text=f"{n} produto(s) carregado(s)", fg=SUCCESS)
            messagebox.showinfo("Afiliados", f"{n} produto(s) carregado(s) com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar planilha:\n{e}")

    def _seo_selecionar_afiliados_dialog(self) -> list | None:
        """
        Exibe dialog de seleção de afiliados.
        Retorna: lista de afiliados selecionados, [] para 'sem afiliado', None se cancelou.
        """
        if not self.afiliados_carregados:
            return None  # sem planilha carregada → deixa seo_writer escolher automaticamente

        resultado = [None]

        dlg = tk.Toplevel(self)
        dlg.title("Selecionar Produto(s) Afiliado(s)")
        dlg.geometry("560x420")
        dlg.configure(bg=BG)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, True)

        tk.Label(dlg, text="Selecione o(s) produto(s) para este post:",
                 bg=BG, fg=WHITE, font=FONT_BOLD).pack(pady=(14, 2), padx=16, anchor=tk.W)
        tk.Label(dlg, text="Ctrl+Click ou Shift+Click para multiplos. Deixe sem selecao para 'sem afiliado'.",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(padx=16, anchor=tk.W, pady=(0, 8))

        frame = tk.Frame(dlg, bg=BG3, padx=2, pady=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=16)

        lb = tk.Listbox(
            frame, bg=BG2, fg=TEXT, font=FONT,
            selectmode=tk.EXTENDED,
            selectbackground=ACCENT, selectforeground=WHITE,
            activestyle="none", borderwidth=0, highlightthickness=0,
        )
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=lb.yview)
        lb.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(fill=tk.BOTH, expand=True)

        for af in self.afiliados_carregados:
            nome = af.get("nome") or af.get("nome_produto", "")
            tipo = af.get("tipo", "")
            lb.insert(tk.END, f"  {nome}  [{tipo}]")

        footer = tk.Frame(dlg, bg=BG, pady=12)
        footer.pack(fill=tk.X, padx=16)

        def confirmar():
            indices = lb.curselection()
            resultado[0] = [self.afiliados_carregados[i] for i in indices]
            dlg.destroy()

        def sem_afiliado():
            resultado[0] = []
            dlg.destroy()

        def cancelar():
            resultado[0] = None
            dlg.destroy()

        ttk.Button(footer, text="✅  Confirmar",
                   command=confirmar, style="Run.TButton").pack(side=tk.LEFT)
        ttk.Button(footer, text="🚫  Sem Afiliado",
                   command=sem_afiliado).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(footer, text="Cancelar",
                   command=cancelar).pack(side=tk.LEFT, padx=(8, 0))

        dlg.wait_window()
        return resultado[0]

    # ── Colar Transcrição ──────────────────────────────────────────────────────

    def _seo_colar_transcricao(self):
        try:
            texto = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("Aviso", "Nada encontrado na área de transferência.")
            return
        if not texto or not texto.strip():
            messagebox.showwarning("Aviso", "Área de transferência está vazia.")
            return
        self.seo_transcript.delete("1.0", tk.END)
        self.seo_transcript.insert("1.0", texto.strip())

    # ── Limpar ─────────────────────────────────────────────────────────────────

    def _seo_limpar(self):
        self.var_seo_url.set("")
        self.var_seo_keyword.set("")
        self.var_seo_secondary.set("")
        self.var_seo_cmd.set("")
        self.seo_transcript.delete("1.0", tk.END)
        self.seo_post_gerado = None
        self.lbl_seo_titulo.config(text="—")
        self.lbl_seo_meta.config(text="")
        self.lbl_seo_imagem.config(text="Imagem: nenhuma selecionada")
        self.seo_log_text.config(state=tk.NORMAL)
        self.seo_log_text.delete("1.0", tk.END)
        self.seo_log_text.config(state=tk.DISABLED)

    # ────────────────────────────────────────────────────────────────────────
    # ABA: POST WEB (scraping de pagina + Claude API)
    # ────────────────────────────────────────────────────────────────────────

    def _build_web_tab(self):
        outer = tk.Frame(self.tab_web, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._tab_info_banner(
            outer,
            "🌐  Post Web — Reescrever Conteúdo de Página",
            "Extrai o conteúdo de qualquer URL da web (artigo, tutorial, página de produto) e usa o Claude "
            "para reescrever como artigo SEO original e otimizado para o blog. "
            "Útil para referenciar fontes externas, criar reviews ou adaptar conteúdo técnico.",
            ["Colar URL da página", "Extrair conteúdo", "Gerar artigo SEO (Claude)", "Publicar"],
        )

        # --- Inputs ---
        inputs = tk.Frame(outer, bg=BG2, padx=12, pady=10)
        inputs.pack(fill=tk.X, pady=(0, 8))

        row0 = tk.Frame(inputs, bg=BG2)
        row0.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row0, text="URL da página:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_web_url = tk.StringVar()
        ttk.Entry(row0, textvariable=self.var_web_url, width=52).pack(side=tk.LEFT, padx=(0, 8))
        self.btn_web_extrair = ttk.Button(row0, text="🌐  Extrair Conteúdo",
                                           command=self._web_extrair)
        self.btn_web_extrair.pack(side=tk.LEFT)

        row1 = tk.Frame(inputs, bg=BG2)
        row1.pack(fill=tk.X, pady=(0, 4))
        tk.Label(row1, text="Keyword alvo:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_web_keyword = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_web_keyword, width=44).pack(side=tk.LEFT)

        row2 = tk.Frame(inputs, bg=BG2)
        row2.pack(fill=tk.X, pady=(0, 4))
        tk.Label(row2, text="Keywords sec.:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_web_secondary = tk.StringVar()
        ttk.Entry(row2, textvariable=self.var_web_secondary, width=44).pack(side=tk.LEFT)
        tk.Label(row2, text="(separadas por vírgula)", bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 0))

        row_cat = tk.Frame(inputs, bg=BG2)
        row_cat.pack(fill=tk.X, pady=(0, 4))
        tk.Label(row_cat, text="Categoria:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.var_web_categoria = tk.StringVar(value="STL Geek")
        ttk.Combobox(
            row_cat, textvariable=self.var_web_categoria, width=30,
            values=["STL Geek", "Personagens", "Chaveiros", "Vasos", "Flexivel",
                    "Croche", "Impressoras 3D", "Filamentos", "Para Iniciantes",
                    "Modelagem 3D", "Tecnicas", "Reviews", "Outros"],
            state="readonly",
        ).pack(side=tk.LEFT)

        # Afiliados
        row_af = tk.Frame(inputs, bg=BG2)
        row_af.pack(fill=tk.X, pady=(4, 0))
        tk.Label(row_af, text="Afiliados:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=18, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Button(row_af, text="📂 Carregar Planilha",
                   command=self._web_carregar_planilha_afiliados).pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_web_af_status = tk.Label(row_af, text="Nenhuma planilha carregada",
                                           bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9))
        self.lbl_web_af_status.pack(side=tk.LEFT)

        # Conteudo extraido
        tk.Label(outer, text="Conteúdo extraído da página (edite se necessário):",
                 bg=BG, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W, pady=(0, 4))
        tf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        tf.pack(fill=tk.X, pady=(0, 6))
        self.web_content_text = tk.Text(tf, bg=BG2, fg=TEXT, font=FONT_MONO,
                                         height=5, wrap=tk.WORD, relief=tk.FLAT)
        ts = ttk.Scrollbar(tf, command=self.web_content_text.yview)
        self.web_content_text.configure(yscrollcommand=ts.set)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.web_content_text.pack(fill=tk.X)

        # Fotos
        foto_frame = tk.Frame(outer, bg=BG2, padx=10, pady=8)
        foto_frame.pack(fill=tk.X, pady=(0, 6))

        foto_top = tk.Frame(foto_frame, bg=BG2)
        foto_top.pack(fill=tk.X)
        tk.Label(foto_top, text="Fotos:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_web_fotos = ttk.Button(foto_top, text="🖼️  Selecionar Fotos",
                                         command=self._web_selecionar_fotos)
        self.btn_web_fotos.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_web_fotos = tk.Label(foto_top, text="Nenhuma foto selecionada",
                                       bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9))
        self.lbl_web_fotos.pack(side=tk.LEFT)

        foto_list_frame = tk.Frame(foto_frame, bg=BG3, padx=2, pady=2)
        foto_list_frame.pack(fill=tk.X, pady=(6, 0))
        self.web_fotos_lb = tk.Listbox(
            foto_list_frame, bg=BG2, fg=TEXT, font=("Segoe UI", 9),
            height=3, selectmode=tk.EXTENDED, borderwidth=0,
            highlightthickness=0, activestyle="none",
        )
        self.web_fotos_lb.pack(fill=tk.X)

        # Botões de ação
        btns = tk.Frame(outer, bg=BG)
        btns.pack(fill=tk.X, pady=(0, 8))

        self.btn_web_gerar = ttk.Button(btns, text="🤖  Gerar Post Web",
                                         command=self._web_gerar,
                                         style="Run.TButton")
        self.btn_web_gerar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_web_publicar = ttk.Button(btns, text="🚀  Publicar",
                                            command=self._web_publicar,
                                            style="Run.TButton")
        self.btn_web_publicar.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btns, text="🧹  Limpar",
                   command=self._web_limpar).pack(side=tk.RIGHT)

        # Preview
        pf = tk.Frame(outer, bg=BG2, padx=10, pady=8)
        pf.pack(fill=tk.X, pady=(0, 8))
        tk.Label(pf, text="Resultado:", bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W)
        self.lbl_web_titulo = tk.Label(pf, text="—", bg=BG2, fg=WHITE,
                                        font=FONT_BOLD, wraplength=700, justify=tk.LEFT)
        self.lbl_web_titulo.pack(anchor=tk.W)
        self.lbl_web_meta = tk.Label(pf, text="", bg=BG2, fg=TEXT_DIM,
                                      font=FONT, wraplength=700, justify=tk.LEFT)
        self.lbl_web_meta.pack(anchor=tk.W)

        # Log
        lf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        lf.pack(fill=tk.BOTH, expand=True)
        self.web_log_text = tk.Text(lf, bg="#0d0d1a", fg="#c8ffc8",
                                     font=FONT_MONO, wrap=tk.WORD,
                                     state=tk.DISABLED, relief=tk.FLAT)
        web_vsb = ttk.Scrollbar(lf, command=self.web_log_text.yview)
        self.web_log_text.configure(yscrollcommand=web_vsb.set)
        self.web_log_text.tag_config("ok",      foreground="#69ff69")
        self.web_log_text.tag_config("err",     foreground="#ff6969")
        self.web_log_text.tag_config("warn",    foreground="#ffcc00")
        self.web_log_text.tag_config("info",    foreground="#69c8ff")
        web_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.web_log_text.pack(fill=tk.BOTH, expand=True)

        bot = tk.Frame(outer, bg=BG)
        bot.pack(fill=tk.X, pady=(8, 0))
        self.web_progress = ttk.Progressbar(bot, mode="indeterminate", length=200)
        self.web_progress.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_web_status = tk.Label(bot, text="Pronto.", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_web_status.pack(side=tk.LEFT)

    # ── Helpers Web Log ────────────────────────────────────────────────────────

    def _web_log_append(self, msg: str):
        self.web_log_queue.put(msg)

    def _poll_web_log(self):
        try:
            while True:
                item = self.web_log_queue.get_nowait()
                self.web_log_text.config(state=tk.NORMAL)
                lo = item.lower()
                if "❌" in item or "erro" in lo or "error" in lo or "falha" in lo:
                    tag = "err"
                elif "⚠️" in item or "aviso" in lo or "warn" in lo:
                    tag = "warn"
                elif "ℹ️" in item or "==" in item or "etapa" in lo:
                    tag = "info"
                else:
                    tag = "ok"
                self.web_log_text.insert(tk.END, item + "\n", tag)
                self.web_log_text.see(tk.END)
                self.web_log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(80, self._poll_web_log)

    def _web_set_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self.btn_web_extrair, self.btn_web_fotos,
                    self.btn_web_gerar, self.btn_web_publicar):
            btn.config(state=state)

    def _web_on_done(self):
        self.web_progress.stop()
        self.lbl_web_status.config(text="Concluído.")
        self._web_set_buttons(True)

    # ── Extrair conteúdo da página ────────────────────────────────────────────

    def _web_extrair(self):
        url = self.var_web_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Informe a URL da página web.")
            return
        if self.web_running:
            return
        self.web_running = True
        self._web_set_buttons(False)
        self.web_progress.start(12)
        self.lbl_web_status.config(text="Extraindo conteúdo da página...")
        threading.Thread(target=self._web_extrair_worker, args=(url,), daemon=True).start()

    def _web_extrair_worker(self, url: str):
        try:
            import seo_writer
            importlib.reload(seo_writer)
            dados = seo_writer.extrair_conteudo_web(url, log_fn=self._web_log_append)
            titulo = dados.get("titulo", "")
            conteudo = dados.get("conteudo", "")
            def update():
                self.web_content_text.delete("1.0", tk.END)
                self.web_content_text.insert("1.0", conteudo)
                if titulo and not self.var_web_keyword.get().strip():
                    import re
                    kw = re.sub(r"\s*[|\-–—].*$", "", titulo).strip().lower()
                    self.var_web_keyword.set(kw[:80])
            self.after(0, update)
            if not conteudo:
                self._web_log_append("  ⚠️ Sem conteúdo extraído — cole o texto manualmente.")
        except Exception as e:
            self._web_log_append(f"  ❌ Erro: {e}")
        finally:
            self.web_running = False
            self.after(0, self._web_on_done)

    # ── Afiliados Web ──────────────────────────────────────────────────────────

    def _web_carregar_planilha_afiliados(self):
        path = filedialog.askopenfilename(
            title="Planilha de Afiliados",
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            import pandas as pd
            if path.endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            df.columns = [c.lower().strip() for c in df.columns]
            if "nome_produto" in df.columns and "nome" not in df.columns:
                df.rename(columns={"nome_produto": "nome"}, inplace=True)
            dados = []
            for _, row in df.iterrows():
                nome = str(row.get("nome", "")).strip()
                link = str(row.get("link", "")).strip()
                tipo = str(row.get("tipo", "")).strip()
                if nome and link and link.lower() != "nan":
                    dados.append({"nome": nome, "link": link, "tipo": tipo})
            self.web_afiliados_carregados = dados
            n = len(dados)
            self.lbl_web_af_status.config(text=f"{n} produto(s) carregado(s)", fg=SUCCESS)
            messagebox.showinfo("Afiliados", f"{n} produto(s) carregado(s).")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar planilha:\n{e}")

    def _web_selecionar_afiliados_dialog(self) -> list | None:
        if not self.web_afiliados_carregados:
            return None
        resultado = [None]
        dlg = tk.Toplevel(self)
        dlg.title("Selecionar Produto(s) Afiliado(s)")
        dlg.geometry("560x420")
        dlg.configure(bg=BG)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, True)
        tk.Label(dlg, text="Selecione o(s) produto(s) para este post:",
                 bg=BG, fg=WHITE, font=FONT_BOLD).pack(pady=(14, 2), padx=16, anchor=tk.W)
        tk.Label(dlg, text="Ctrl+Click para múltiplos. Sem seleção = sem afiliado.",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(padx=16, anchor=tk.W, pady=(0, 8))
        frame = tk.Frame(dlg, bg=BG3, padx=2, pady=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=16)
        lb = tk.Listbox(frame, bg=BG2, fg=TEXT, font=FONT, selectmode=tk.EXTENDED,
                        selectbackground=ACCENT, selectforeground=WHITE,
                        activestyle="none", borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=lb.yview)
        lb.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(fill=tk.BOTH, expand=True)
        for af in self.web_afiliados_carregados:
            nome = af.get("nome") or af.get("nome_produto", "")
            tipo = af.get("tipo", "")
            lb.insert(tk.END, f"  {nome}  [{tipo}]")
        footer = tk.Frame(dlg, bg=BG, pady=12)
        footer.pack(fill=tk.X, padx=16)
        def confirmar():
            resultado[0] = [self.web_afiliados_carregados[i] for i in lb.curselection()]
            dlg.destroy()
        def sem_afiliado():
            resultado[0] = []
            dlg.destroy()
        def cancelar():
            resultado[0] = None
            dlg.destroy()
        ttk.Button(footer, text="✅  Confirmar", command=confirmar,
                   style="Run.TButton").pack(side=tk.LEFT)
        ttk.Button(footer, text="🚫  Sem Afiliado", command=sem_afiliado).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(footer, text="Cancelar", command=cancelar).pack(side=tk.LEFT, padx=(8, 0))
        dlg.wait_window()
        return resultado[0]

    # ── Fotos ──────────────────────────────────────────────────────────────────

    def _web_selecionar_fotos(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar fotos para o post",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")],
        )
        if not paths:
            return
        self.web_imagens_selecionadas = list(paths)
        n = len(paths)
        self.lbl_web_fotos.config(
            text=f"{n} foto(s) selecionada(s) — 1ª = destaque",
            fg=SUCCESS,
        )
        self.web_fotos_lb.delete(0, tk.END)
        for p in paths:
            self.web_fotos_lb.insert(tk.END, f"  {Path(p).name}")

    # ── Gerar Post ─────────────────────────────────────────────────────────────

    def _web_gerar(self):
        keyword = self.var_web_keyword.get().strip()
        if not keyword:
            messagebox.showwarning("Aviso", "Informe a keyword alvo.")
            return
        if self.web_running:
            return
        afiliados_sel = self._web_selecionar_afiliados_dialog()
        if afiliados_sel is None and self.web_afiliados_carregados:
            return
        self._carregar_env()
        self.web_running = True
        self._web_set_buttons(False)
        self.web_progress.start(12)
        self.lbl_web_status.config(text="Gerando post via Claude API...")
        sec_raw  = self.var_web_secondary.get().strip()
        sec_kws  = [k.strip() for k in sec_raw.split(",") if k.strip()]
        conteudo = self.web_content_text.get("1.0", tk.END).strip()
        url      = self.var_web_url.get().strip()
        threading.Thread(
            target=self._web_gerar_worker,
            args=(keyword, sec_kws, url, conteudo, afiliados_sel),
            daemon=True,
        ).start()

    def _web_gerar_worker(self, keyword, secondary_kws, page_url, page_content, afiliados_sel=None):
        try:
            import seo_writer
            importlib.reload(seo_writer)
            sep = "=" * 50
            self._web_log_append(sep)
            self._web_log_append(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')} — Gerando Post Web [PT-BR]")
            self._web_log_append(sep)
            self._web_log_append(f"  Keyword: {keyword}")
            self._web_log_append(f"  Fonte: {page_url or '(sem URL)'}")

            post = seo_writer.gerar_post_web(
                keyword=keyword,
                secondary_kws=secondary_kws,
                page_url=page_url,
                page_title="",
                page_content=page_content,
                categoria=self.var_web_categoria.get(),
                afiliados_override=afiliados_sel,
                log_fn=self._web_log_append,
            )

            if self.web_imagens_selecionadas:
                post["featured_image_path"] = self.web_imagens_selecionadas[0]

            self.web_post_gerado = post

            def update_preview():
                self.lbl_web_titulo.config(text=post.get("titulo", ""))
                meta = post.get("yoast_meta", "")
                self.lbl_web_meta.config(text=f"Meta ({len(meta)} chars): {meta}")
            self.after(0, update_preview)
            self._web_log_append("\n  Post gerado. Confirme as fotos e clique em Publicar.")
        except Exception as e:
            self._web_log_append(f"\n  ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.web_running = False
            self.after(0, self._web_on_done)

    # ── Publicar ───────────────────────────────────────────────────────────────

    def _web_publicar(self):
        if not self.web_post_gerado:
            messagebox.showwarning("Aviso", "Gere o post antes de publicar.")
            return
        if not self.web_imagens_selecionadas:
            if not messagebox.askyesno("Sem fotos", "Nenhuma foto selecionada. Publicar mesmo assim?"):
                return
        if self.web_running:
            return
        cfg    = self._ler_config_atual()
        status = cfg.get("wp_post_status", "draft")
        titulo = self.web_post_gerado.get("titulo", "")
        if not messagebox.askyesno("Confirmar", f"Publicar como '{status}'?\n\n{titulo}"):
            return
        self.web_running = True
        self._web_set_buttons(False)
        self.web_progress.start(12)
        self.lbl_web_status.config(text="Publicando no WordPress...")
        threading.Thread(target=self._web_publicar_worker, daemon=True).start()

    def _web_publicar_worker(self):
        try:
            import seo_writer
            importlib.reload(seo_writer)
            from publisher import WordPressPublisher
            cfg    = self._ler_config_atual()
            status = cfg.get("wp_post_status", "draft")
            pub    = WordPressPublisher(cfg)

            hist_path = Path("posts_publicados.json")
            historico = (json.loads(hist_path.read_text(encoding="utf-8"))
                         if hist_path.exists() else [])

            p       = dict(self.web_post_gerado)
            p["status"] = status
            fotos   = self.web_imagens_selecionadas
            titulo  = p.get("titulo", "")

            # ── 1. Upload antecipado de todas as fotos ────────────────────────
            media_list = []  # lista de {"id": int, "url": str, "alt": str}
            if fotos:
                n_fotos = len(fotos)
                self._web_log_append(f"  Enviando {n_fotos} foto(s) para o WordPress...")
                for i, img_path in enumerate(fotos, 1):
                    try:
                        alt = f"{titulo} — foto {i}"
                        mid, murl = pub.upload_media(img_path, alt_text=alt)
                        if mid and murl:
                            media_list.append({"id": mid, "url": murl, "alt": alt})
                            self._web_log_append(
                                f"    ✅ [{i}/{n_fotos}] {Path(img_path).name} → ID {mid}")
                        else:
                            self._web_log_append(
                                f"    ⚠️ [{i}/{n_fotos}] {Path(img_path).name}: upload sem retorno")
                    except Exception as ei:
                        self._web_log_append(
                            f"    ❌ [{i}/{n_fotos}] {Path(img_path).name}: {ei}")

            # ── 2. Featured image: usa o ID já obtido (evita segundo upload) ──
            if media_list:
                p["_featured_media_id"] = media_list[0]["id"]
                p["featured_image_path"] = ""   # publisher verá o ID acima

            # ── 3. Embed das fotos no corpo do post ───────────────────────────
            # 1 foto  → 1 embed estratégico (depois do 1º H2)
            # 3+ fotos → 3 posições estratégicas distribuídas
            # (se 2 fotos, a 1ª é destaque e a 2ª vai para o meio)
            imagens_para_embed = media_list  # inclui a 1ª foto também no corpo
            if imagens_para_embed:
                p["content"] = seo_writer.inserir_imagens_no_content(
                    p.get("content", ""), imagens_para_embed
                )
                self._web_log_append(
                    f"  {len(imagens_para_embed)} foto(s) inserida(s) no corpo do post.")

            # ── 4. Publicar ───────────────────────────────────────────────────
            self._web_log_append(f"  Publicando: {titulo[:55]}...")
            resultado = pub.publicar_post(p)

            if resultado:
                wp_id    = resultado.get("wp_id", "")
                post_url = resultado.get("url", "")
                self._web_log_append(f"  ✅ Post criado! ID: {wp_id} — {post_url}")
                resultado["gerado_em"] = datetime.now().isoformat()
                resultado["titulo"]    = titulo
                historico.append(resultado)

            hist_path.write_text(
                json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            self.after(0, self._load_posts_tab)
        except Exception as e:
            self._web_log_append(f"  ❌ Erro ao publicar: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.web_running = False
            self.after(0, self._web_on_done)

    # ── Limpar ─────────────────────────────────────────────────────────────────

    def _web_limpar(self):
        self.var_web_url.set("")
        self.var_web_keyword.set("")
        self.var_web_secondary.set("")
        self.web_content_text.delete("1.0", tk.END)
        self.web_post_gerado = None
        self.web_imagens_selecionadas = []
        self.web_fotos_lb.delete(0, tk.END)
        self.lbl_web_titulo.config(text="—")
        self.lbl_web_meta.config(text="")
        self.lbl_web_fotos.config(text="Nenhuma foto selecionada", fg=TEXT_DIM)
        self.web_log_text.config(state=tk.NORMAL)
        self.web_log_text.delete("1.0", tk.END)
        self.web_log_text.config(state=tk.DISABLED)


    # ── Aba YouTube SEO ────────────────────────────────────────────────────────

    def _build_yt_tab(self):
        outer = tk.Frame(self.tab_yt, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._tab_info_banner(
            outer,
            "🎬  YouTube → Post Automático (1 clique)",
            "Pipeline simplificado: cole a URL do vídeo e clique em Gerar e Publicar. "
            "O sistema extrai título e transcrição automaticamente, detecta keywords, "
            "escreve o artigo em PT-BR com interlinks do cluster SEO e publica como rascunho no WordPress.",
            ["Colar URL do YouTube", "Selecionar categoria", "Gerar e Publicar (automático)"],
        )

        # Inputs
        inputs = tk.Frame(outer, bg=BG2, padx=14, pady=12)
        inputs.pack(fill=tk.X, pady=(0, 10))

        row_url = tk.Frame(inputs, bg=BG2)
        row_url.pack(fill=tk.X, pady=(0, 8))
        tk.Label(row_url, text="URL YouTube:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=16, anchor=tk.W).pack(side=tk.LEFT)
        self.var_yt_url = tk.StringVar()
        ttk.Entry(row_url, textvariable=self.var_yt_url, width=56).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row_url, text="✕", command=lambda: self.var_yt_url.set(""),
                   width=3).pack(side=tk.LEFT)

        row_cat = tk.Frame(inputs, bg=BG2)
        row_cat.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row_cat, text="Categoria WP:", bg=BG2, fg=TEXT_DIM, font=FONT,
                 width=16, anchor=tk.W).pack(side=tk.LEFT)
        self.var_yt_categoria = tk.StringVar(value="STL Geek")
        ttk.Combobox(
            row_cat, textvariable=self.var_yt_categoria, width=28,
            values=["STL Geek", "Impressao 3D", "Renda Extra", "Filamentos",
                    "Para Iniciantes", "Impressoras 3D", "Modelagem 3D",
                    "Tecnicas", "Reviews"],
            state="readonly",
        ).pack(side=tk.LEFT, padx=(0, 16))
        self.var_yt_renda_extra = tk.BooleanVar()
        ttk.Checkbutton(row_cat, text="Renda Extra (post de monetização)",
                        variable=self.var_yt_renda_extra).pack(side=tk.LEFT)

        # Botões
        btns = tk.Frame(outer, bg=BG)
        btns.pack(fill=tk.X, pady=(0, 8))
        self.btn_yt_gerar = ttk.Button(btns, text="🎬  Gerar e Publicar",
                                        command=self._yt_gerar,
                                        style="Run.TButton")
        self.btn_yt_gerar.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="🧹  Limpar", command=self._yt_limpar).pack(side=tk.LEFT)

        # Resultado
        res = tk.Frame(outer, bg=BG2, padx=10, pady=8)
        res.pack(fill=tk.X, pady=(0, 8))
        tk.Label(res, text="Resultado:", bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W)
        self.lbl_yt_titulo = tk.Label(res, text="—", bg=BG2, fg=WHITE,
                                       font=FONT_BOLD, wraplength=750, justify=tk.LEFT)
        self.lbl_yt_titulo.pack(anchor=tk.W)
        self.lbl_yt_link = tk.Label(res, text="", bg=BG2, fg=ACCENT2,
                                     font=FONT, cursor="hand2")
        self.lbl_yt_link.pack(anchor=tk.W)
        self.lbl_yt_link.bind("<Button-1>", lambda e: webbrowser.open(self.yt_result_url) if self.yt_result_url else None)

        # Log
        lf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        lf.pack(fill=tk.BOTH, expand=True)
        self.yt_log_text = tk.Text(lf, bg="#0d0d1a", fg="#c8ffc8",
                                    font=FONT_MONO, wrap=tk.WORD,
                                    state=tk.DISABLED, relief=tk.FLAT)
        yt_vsb = ttk.Scrollbar(lf, command=self.yt_log_text.yview)
        self.yt_log_text.configure(yscrollcommand=yt_vsb.set)
        self.yt_log_text.tag_config("ok",      foreground="#69ff69")
        self.yt_log_text.tag_config("err",     foreground="#ff6969")
        self.yt_log_text.tag_config("warn",    foreground="#ffcc00")
        self.yt_log_text.tag_config("info",    foreground="#69c8ff")
        self.yt_log_text.tag_config("heading", foreground=WHITE, font=("Consolas", 9, "bold"))
        yt_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.yt_log_text.pack(fill=tk.BOTH, expand=True)

        bot = tk.Frame(outer, bg=BG)
        bot.pack(fill=tk.X, pady=(8, 0))
        self.yt_progress = ttk.Progressbar(bot, mode="indeterminate", length=200)
        self.yt_progress.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_yt_status = tk.Label(bot, text="Pronto.", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_yt_status.pack(side=tk.LEFT)

    def _yt_log_append(self, msg: str):
        self.yt_log_queue.put(msg)

    def _poll_yt_log(self):
        try:
            while True:
                item = self.yt_log_queue.get_nowait()
                self.yt_log_text.config(state=tk.NORMAL)
                tag = "err" if any(w in item.lower() for w in ("erro", "error", "❌")) else \
                      "warn" if any(w in item.lower() for w in ("aviso", "warn", "⚠")) else \
                      "info" if item.startswith("  [") else "ok"
                self.yt_log_text.insert(tk.END, item + "\n", tag)
                self.yt_log_text.see(tk.END)
                self.yt_log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(80, self._poll_yt_log)

    def _yt_set_buttons(self, enabled: bool):
        st = tk.NORMAL if enabled else tk.DISABLED
        self.btn_yt_gerar.config(state=st)

    def _yt_on_done(self):
        self.yt_progress.stop()
        self._yt_set_buttons(True)
        self.lbl_yt_status.config(text="Concluído." if self.yt_result_url else "Pronto.")

    def _yt_gerar(self):
        url = self.var_yt_url.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole a URL do YouTube.")
            return
        if self.yt_running:
            return
        self._carregar_env()
        self.yt_running = True
        self.yt_result_url = ""
        self._yt_set_buttons(False)
        self.yt_progress.start(12)
        self.lbl_yt_status.config(text="Processando...")
        self.lbl_yt_titulo.config(text="—")
        self.lbl_yt_link.config(text="")
        threading.Thread(target=self._yt_worker, args=(url,), daemon=True).start()

    def _yt_worker(self, url: str):
        try:
            from gerar_post_youtube import extrair_metadados_yt, titulo_para_keyword, gerar_secondary_kws
            import seo_writer, publisher, importlib
            importlib.reload(seo_writer)

            sep = "=" * 52
            self._yt_log_append(sep)
            self._yt_log_append(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')} — YouTube SEO Pipeline")
            self._yt_log_append(sep)

            # 1. Metadados
            self._yt_log_append("\n  [1/4] Metadados do vídeo...")
            meta = extrair_metadados_yt(url)
            titulo_yt      = meta.get("title", "")
            yt_description = meta.get("description", "")
            if titulo_yt:
                self._yt_log_append(f"  Título original: {titulo_yt}")
                titulo_yt = seo_writer.traduzir_titulo_para_pt(titulo_yt, log_fn=self._yt_log_append)
            else:
                titulo_yt = "impressao 3d"
                self._yt_log_append("  Título não obtido — usando keyword genérica.")

            keyword   = titulo_para_keyword(titulo_yt)
            secondary = gerar_secondary_kws(keyword, titulo_yt)
            self._yt_log_append(f"  Keyword: {keyword}")
            self._yt_log_append(f"  Secundárias: {', '.join(secondary)}")

            # 2. Transcrição
            self._yt_log_append("\n  [2/4] Extraindo transcrição...")
            transcript = seo_writer.extrair_transcricao_yt(url, log_fn=self._yt_log_append)
            if not transcript:
                self._yt_log_append("  Sem transcrição — usando descrição como contexto.")

            # 3. Gerar post
            categoria = self.var_yt_categoria.get()
            if self.var_yt_renda_extra.get():
                categoria = "Renda Extra"
            self._yt_log_append(f"\n  [3/4] Gerando post SEO [PT-BR] — categoria: {categoria}...")
            post = seo_writer.gerar_post_seo(
                keyword=keyword, secondary_kws=secondary,
                transcript=transcript, youtube_url=url,
                yt_description=yt_description,
                log_fn=self._yt_log_append,
                categoria=categoria,
            )

            # Cluster / interlinks
            if categoria.lower() not in ("financas", "finanças", "marketing digital", "ganhar dinheiro online"):
                try:
                    from cluster import ClusterManager
                    cluster = ClusterManager()
                    tema = cluster.detectar_tema(keyword, titulo_yt)
                    post["_cluster_tema"] = tema
                    interlinks = cluster.gerar_html_interlinks(tema, excluir_url="")
                    if interlinks:
                        script_pos = post.get("content", "").find('<script type="application/ld+json">')
                        if script_pos >= 0:
                            post["content"] = post["content"][:script_pos] + interlinks + "\n" + post["content"][script_pos:]
                        else:
                            post["content"] += interlinks
                        self._yt_log_append(f"  Interlinks injetados (tema: {tema})")
                except Exception:
                    pass

            # Thumbnail do YouTube como imagem destacada
            import re as _re, tempfile, requests as _req
            _vid = _re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
            if _vid and not post.get("featured_image_path"):
                vid = _vid.group(1)
                self._yt_log_append("  Baixando thumbnail do YouTube...")
                for quality in ("maxresdefault", "hqdefault"):
                    try:
                        resp = _req.get(
                            f"https://img.youtube.com/vi/{vid}/{quality}.jpg",
                            timeout=10,
                        )
                        if resp.status_code == 200 and len(resp.content) > 5000:
                            from pathlib import Path as _Path
                            tmp = _Path(tempfile.mkdtemp()) / f"yt_thumb_{vid}.jpg"
                            tmp.write_bytes(resp.content)
                            post["featured_image_path"] = str(tmp)
                            self._yt_log_append(f"  Thumbnail salvo ({quality})")
                            break
                    except Exception:
                        pass

            # Link de saída para o vídeo (resolve aviso Yoast)
            outbound = (
                f'\n<p>Baseado em vídeo original do YouTube: '
                f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                f'assista aqui</a>.</p>\n'
            )
            content = post.get("content", "")
            schema_pos = content.find('<script type="application/ld+json">')
            if schema_pos >= 0:
                post["content"] = content[:schema_pos] + outbound + content[schema_pos:]
            else:
                post["content"] = content + outbound
            self._yt_log_append("  Link de saída para YouTube injetado.")

            titulo_post = post.get("titulo", "")
            meta_desc   = post.get("yoast_meta", "")
            self._yt_log_append(f"\n  Título: {titulo_post}")
            self._yt_log_append(f"  Meta ({len(meta_desc)} chars): {meta_desc}")

            # 4. Publicar
            self._yt_log_append("\n  [4/4] Publicando como rascunho no WordPress...")
            cfg = self._ler_config_atual()
            pub = publisher.WordPressPublisher(cfg)
            result = pub.publicar_post(post)
            wp_id  = result.get("wp_id", "")
            wp_url = result.get("url", "")
            self.yt_result_url = wp_url

            self._yt_log_append(f"\n  ✅ Publicado! ID: {wp_id}")
            self._yt_log_append(f"  Link: {wp_url}")
            self._yt_log_append(sep)

            # Cluster: registra post
            try:
                cluster.adicionar_post(tema, {"titulo": titulo_post, "url": wp_url, "wp_id": wp_id})
            except Exception:
                pass

            def update_ui():
                self.lbl_yt_titulo.config(text=titulo_post)
                self.lbl_yt_link.config(text=wp_url or "")
            self.after(0, update_ui)

        except Exception as e:
            self._yt_log_append(f"\n  ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.yt_running = False
            self.after(0, self._yt_on_done)

    def _yt_limpar(self):
        self.var_yt_url.set("")
        self.yt_result_url = ""
        self.lbl_yt_titulo.config(text="—")
        self.lbl_yt_link.config(text="")
        self.lbl_yt_status.config(text="Pronto.")
        self.yt_log_text.config(state=tk.NORMAL)
        self.yt_log_text.delete("1.0", tk.END)
        self.yt_log_text.config(state=tk.DISABLED)




if __name__ == "__main__":
    App().mainloop()
