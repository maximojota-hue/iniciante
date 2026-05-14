"""
app_helio.py — Gerador de Posts para HelioBrinquedos
Execute: python app_helio.py

Credenciais Helio carregadas do .env.
Sem conflito com clube3dbrasil.com.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import io
import sys
import importlib
import webbrowser
from pathlib import Path
from datetime import datetime

os.chdir(Path(__file__).parent)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Tema ──────────────────────────────────────────────────────────────────────
BG        = "#1a1a2e"
BG2       = "#16213e"
BG3       = "#0f3460"
ACCENT    = "#8B4513"     # marrom vintage — diferencia do Clube 3D
ACCENT2   = "#CD853F"
TEXT      = "#e0e0e0"
TEXT_DIM  = "#888888"
WHITE     = "#ffffff"
FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)

def _load_env_file(path: str, override: bool = False):
    env_path = Path(path)
    if not env_path.exists():
        return
    for _linha in env_path.read_text(encoding="utf-8").splitlines():
        _linha = _linha.strip()
        if _linha and not _linha.startswith("#") and "=" in _linha:
            _k, _, _v = _linha.partition("=")
            key = _k.strip().lstrip("\ufeff")
            if override:
                os.environ[key] = _v.strip()
            else:
                os.environ.setdefault(key, _v.strip())


# ── Credenciais Helio Brinquedos ─────────────────────────────────────────────
_load_env_file(".env")
_load_env_file(".env.helio", override=True)

WP_URL      = os.environ.get("HELIO_WP_URL") or os.environ.get("WP_URL", "https://heliobrinquedos.clube3dbrasil.com")
WP_USER     = os.environ.get("HELIO_WP_USER") or os.environ.get("WP_USER", "")
WP_APP_PASS = os.environ.get("HELIO_WP_PASS") or os.environ.get("WP_PASS", "")
WA_NUMBER   = os.environ.get("HELIO_WA_NUMBER") or os.environ.get("WA", "5521981536073")

CFG = {
    "wp_url":             WP_URL,
    "wp_user":            WP_USER,
    "wp_app_password":    WP_APP_PASS,
    "wp_use_rest_route":  True,
}


def _carregar_env():
    _load_env_file(".env")
    _load_env_file(".env.helio", override=True)


# ── Estilos ttk ───────────────────────────────────────────────────────────────
def _aplicar_estilos(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=FONT,
                 fieldbackground=BG2, troughcolor=BG3, borderwidth=0)
    s.configure("TFrame",        background=BG)
    s.configure("TLabel",        background=BG, foreground=TEXT)
    s.configure("TEntry",        fieldbackground=BG2, foreground=TEXT,
                insertcolor=WHITE, borderwidth=1)
    s.configure("TButton",       background=BG3, foreground=TEXT, padding=(8, 4))
    s.map("TButton", background=[("active", ACCENT)])
    s.configure("Run.TButton",   background=ACCENT, foreground=WHITE,
                font=FONT_BOLD, padding=(12, 6))
    s.map("Run.TButton",         background=[("active", ACCENT2)])
    s.configure("TCombobox",     fieldbackground=BG2, foreground=TEXT, arrowcolor=TEXT)
    s.configure("TScrollbar",    background=BG3, troughcolor=BG)
    s.configure("TProgressbar",  troughcolor=BG3, background=ACCENT2)


# ── App Principal ─────────────────────────────────────────────────────────────
class HelioApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("🧸 HelioBrinquedos — Publicador de Posts")
        self.geometry("1100x820")
        self.minsize(900, 650)
        self.configure(bg=BG)
        _aplicar_estilos(self)

        # State
        self.log_queue:           queue.Queue = queue.Queue()
        self.running:             bool        = False
        self.pub_running:         bool        = False
        self.post_gerado:         dict | None = None
        self.fotos_selecionadas:  list        = []
        self._pub_url:            str         = ""

        self._build_header()
        self._build_main()
        self.after(80, self._poll_log)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(
            hdr,
            text="🧸  HelioBrinquedos — Gerar Post por Foto",
            bg=ACCENT, fg=WHITE, font=("Segoe UI", 13, "bold"),
        ).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(
            hdr,
            text=f"🌐 {WP_URL}  |  👤 {WP_USER}",
            bg=ACCENT, fg="#ffddaa", font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT, padx=20)

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build_main(self):
        outer = tk.Frame(self, bg=BG, padx=16, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        # Banner informativo
        self._banner(
            outer,
            "Envie 1 ou mais fotos do produto. Claude Vision analisa, gera post completo "
            "com história, SEO Yoast e botão WhatsApp. Edite e publique direto no WordPress.",
            ["① Selecionar fotos", "② Analisar com IA", "③ Revisar / editar", "④ Publicar no WP"],
        )

        # Painel duplo: fotos (esq) | SEO (dir)
        top = tk.Frame(outer, bg=BG)
        top.pack(fill=tk.X, pady=(0, 8))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=2)

        self._build_foto_panel(top)
        self._build_seo_panel(top)

        # Conteúdo HTML
        tk.Label(outer, text="✏️  Conteúdo HTML (editável):",
                 bg=BG, fg=TEXT_DIM, font=FONT).pack(anchor=tk.W, pady=(4, 2))
        cf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        cf.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self.content_text = tk.Text(
            cf, bg=BG2, fg=TEXT, font=("Segoe UI", 9),
            wrap=tk.WORD, height=11, relief=tk.FLAT,
            insertbackground=WHITE,
        )
        vsb_c = ttk.Scrollbar(cf, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=vsb_c.set)
        vsb_c.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Botões
        btns = tk.Frame(outer, bg=BG)
        btns.pack(fill=tk.X, pady=(0, 6))
        self.btn_gerar = ttk.Button(
            btns, text="🤖  Analisar Fotos + Gerar Post",
            command=self._gerar, style="Run.TButton")
        self.btn_gerar.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_publicar = ttk.Button(
            btns, text="🚀  Publicar no WordPress",
            command=self._publicar, style="Run.TButton")
        self.btn_publicar.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="🧹  Limpar", command=self._limpar).pack(side=tk.RIGHT)

        # Preview publicação
        pf = tk.Frame(outer, bg=BG2, padx=10, pady=6)
        pf.pack(fill=tk.X, pady=(0, 6))
        self.lbl_titulo_pub = tk.Label(pf, text="—", bg=BG2, fg=WHITE,
                                        font=FONT_BOLD, wraplength=700, justify=tk.LEFT)
        self.lbl_titulo_pub.pack(anchor=tk.W)
        self.lbl_link = tk.Label(pf, text="", bg=BG2, fg=ACCENT2,
                                  font=("Segoe UI", 9), cursor="hand2")
        self.lbl_link.pack(anchor=tk.W)
        self.lbl_link.bind(
            "<Button-1>",
            lambda _e: webbrowser.open(self._pub_url) if self._pub_url else None)

        # Log
        lf = tk.Frame(outer, bg=BG3, padx=2, pady=2)
        lf.pack(fill=tk.X)
        self.log_text = tk.Text(
            lf, bg="#0d0d1a", fg="#c8ffc8", font=FONT_MONO,
            wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT, height=7)
        vsb_l = ttk.Scrollbar(lf, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb_l.set)
        self.log_text.tag_config("ok",   foreground="#69ff69")
        self.log_text.tag_config("err",  foreground="#ff6969")
        self.log_text.tag_config("warn", foreground="#ffcc00")
        self.log_text.tag_config("info", foreground="#69c8ff")
        vsb_l.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Barra inferior
        bot = tk.Frame(outer, bg=BG)
        bot.pack(fill=tk.X, pady=(6, 0))
        self.progress = ttk.Progressbar(bot, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_status = tk.Label(bot, text="Pronto.", bg=BG, fg=TEXT_DIM, font=FONT)
        self.lbl_status.pack(side=tk.LEFT)

    def _build_foto_panel(self, parent):
        fp = tk.Frame(parent, bg=BG2, padx=10, pady=8)
        fp.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        tk.Label(fp, text="📸  Fotos do Produto", bg=BG2, fg=TEXT,
                 font=FONT_BOLD).pack(anchor=tk.W, pady=(0, 6))
        fb = tk.Frame(fp, bg=BG2)
        fb.pack(fill=tk.X, pady=(0, 4))
        self.btn_fotos = ttk.Button(fb, text="📂  Selecionar Fotos",
                                     command=self._selecionar_fotos)
        self.btn_fotos.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(fb, text="🗑️  Remover", width=10,
                   command=self._remover_foto).pack(side=tk.LEFT)
        lbf = tk.Frame(fp, bg=BG3, padx=2, pady=2)
        lbf.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.fotos_lb = tk.Listbox(
            lbf, bg=BG2, fg=TEXT, font=("Segoe UI", 9),
            height=6, selectmode=tk.EXTENDED, borderwidth=0,
            highlightthickness=0, activestyle="none")
        self.fotos_lb.pack(fill=tk.BOTH, expand=True)
        self.lbl_fotos = tk.Label(fp, text="Nenhuma foto selecionada",
                                   bg=BG2, fg=TEXT_DIM, font=("Segoe UI", 9))
        self.lbl_fotos.pack(anchor=tk.W)

    def _build_seo_panel(self, parent):
        sp = tk.Frame(parent, bg=BG2, padx=10, pady=8)
        sp.grid(row=0, column=1, sticky=tk.NSEW)
        tk.Label(sp, text="🔍  Campos SEO / Yoast (editáveis após gerar)",
                 bg=BG2, fg=TEXT, font=FONT_BOLD).pack(anchor=tk.W, pady=(0, 6))
        sf = tk.Frame(sp, bg=BG2)
        sf.pack(fill=tk.X)
        sf.columnconfigure(1, weight=1)
        self.vars: dict[str, tk.StringVar] = {}
        fields = [
            ("titulo",          "Título do Post"),
            ("yoast_keyphrase", "Focus Keyword"),
            ("yoast_title",     "SEO Title (≤60ch)"),
            ("yoast_meta",      "Meta Description (≤155ch)"),
            ("tags",            "Tags (separadas por vírgula)"),
        ]
        for i, (key, label) in enumerate(fields):
            tk.Label(sf, text=label, bg=BG2, fg=TEXT_DIM,
                     font=("Segoe UI", 9), width=24, anchor=tk.W).grid(
                row=i, column=0, sticky=tk.W, pady=3)
            v = tk.StringVar()
            ttk.Entry(sf, textvariable=v).grid(
                row=i, column=1, sticky=tk.EW, padx=(6, 0), pady=3)
            self.vars[key] = v
        status_row = len(fields)
        tk.Label(sf, text="Status WP", bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9), width=24, anchor=tk.W).grid(
            row=status_row, column=0, sticky=tk.W, pady=3)
        self.var_status = tk.StringVar(value="draft")
        ttk.Combobox(sf, textvariable=self.var_status,
                     values=["draft", "publish"], state="readonly", width=12).grid(
            row=status_row, column=1, sticky=tk.W, padx=(6, 0), pady=3)

    def _banner(self, parent, descricao: str, passos: list):
        w = tk.Frame(parent, bg=ACCENT2, padx=3, pady=0)
        w.pack(fill=tk.X, pady=(0, 12))
        inner = tk.Frame(w, bg=BG2, padx=14, pady=10)
        inner.pack(fill=tk.X)
        tk.Label(inner, text=descricao, bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9), wraplength=960, justify=tk.LEFT).pack(anchor=tk.W)
        txt = "   →   ".join(passos)
        tk.Label(inner, text=txt, bg=BG2, fg=ACCENT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(6, 0))

    # ── Log ───────────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        self.log_queue.put(msg)

    def _poll_log(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                lo = item.lower()
                if "❌" in item or "erro" in lo or "error" in lo or "falha" in lo:
                    tag = "err"
                elif "⚠️" in item or "warn" in lo or "aviso" in lo:
                    tag = "warn"
                elif "==" in item or "etapa" in lo or "ℹ️" in item:
                    tag = "info"
                else:
                    tag = "ok"
                self.log_text.insert(tk.END, item + "\n", tag)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(80, self._poll_log)

    def _set_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self.btn_fotos, self.btn_gerar, self.btn_publicar):
            btn.config(state=state)

    # ── Fotos ─────────────────────────────────────────────────────────────────

    def _selecionar_fotos(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar fotos do produto",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp *.bmp *.gif"), ("Todos", "*.*")],
        )
        for p in paths:
            if p not in self.fotos_selecionadas:
                self.fotos_selecionadas.append(p)
                self.fotos_lb.insert(tk.END, Path(p).name)
        n = len(self.fotos_selecionadas)
        self.lbl_fotos.config(text=f"{n} foto(s) selecionada(s)" if n else "Nenhuma foto selecionada")

    def _remover_foto(self):
        for idx in reversed(list(self.fotos_lb.curselection())):
            self.fotos_lb.delete(idx)
            self.fotos_selecionadas.pop(idx)
        n = len(self.fotos_selecionadas)
        self.lbl_fotos.config(text=f"{n} foto(s) selecionada(s)" if n else "Nenhuma foto selecionada")

    # ── Gerar Post ────────────────────────────────────────────────────────────

    def _gerar(self):
        if not self.fotos_selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos 1 foto do produto.")
            return
        if self.running:
            return
        _carregar_env()
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            messagebox.showerror("API Key", "ANTHROPIC_API_KEY não encontrada no .env")
            return
        self.running = True
        self.post_gerado = None
        self._set_buttons(False)
        self.progress.start(12)
        self.lbl_status.config(text="Analisando fotos com Claude Vision...")
        threading.Thread(
            target=self._gerar_worker,
            args=(list(self.fotos_selecionadas), api_key),
            daemon=True,
        ).start()

    def _gerar_worker(self, fotos: list, api_key: str):
        try:
            import anthropic, base64 as _b64, json as _json, re as _re

            sep = "=" * 54
            self._log(sep)
            self._log(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')} — Análise por Foto")
            self._log(sep)
            self._log(f"  {len(fotos)} foto(s) carregada(s)")

            client = anthropic.Anthropic(api_key=api_key)
            ext_map = {".jpg":"image/jpeg",".jpeg":"image/jpeg",
                       ".png":"image/png",".webp":"image/webp",
                       ".gif":"image/gif",".bmp":"image/jpeg"}

            content = []
            for path in fotos[:5]:
                mt = ext_map.get(Path(path).suffix.lower(), "image/jpeg")
                with open(path, "rb") as f:
                    data = _b64.standard_b64encode(f.read()).decode("utf-8")
                content.append({"type":"image","source":{"type":"base64","media_type":mt,"data":data}})
                self._log(f"  Foto: {Path(path).name}")

            prompt = (
                "Analise as imagens do produto e gere um post completo para o blog HelioBrinquedos "
                "— especializado em brinquedos raros, games clássicos e colecionáveis brasileiros.\n\n"
                "Retorne SOMENTE um JSON válido (sem markdown, sem blocos de código, só o JSON bruto) "
                "com esta estrutura exata:\n"
                '{\n'
                '  "titulo": "Título completo SEO (marca + modelo + características + Vintage/Raro/Colecionável) — máximo 70 chars",\n'
                '  "subtitulo": "Subtítulo H2 atraente que CONTÉM a yoast_keyphrase — máximo 80 chars",\n'
                '  "intro": "2-3 frases de introdução que OBRIGATORIAMENTE contêm a yoast_keyphrase logo na 1ª ou 2ª frase.",\n'
                '  "marca": "Marca do produto",\n'
                '  "modelo": "Modelo ou referência",\n'
                '  "tipo": "Tipo de produto (ex: Relógio digital, Videogame portátil, Boneco articulado)",\n'
                '  "funcoes": "Funções e características principais",\n'
                '  "tecnologia": "Tecnologia ou material (ex: LCD, plástico ABS, metal)",\n'
                '  "decada": "Década de lançamento (ex: anos 80, anos 90)",\n'
                '  "acompanha": "O que acompanha — se não visível escreva: (preencher conforme o item real)",\n'
                '  "historia": "3-4 frases sobre história, contexto de mercado e importância cultural.",\n'
                '  "por_que_raro": ["Motivo 1", "Motivo 2", "Motivo 3", "Motivo 4", "Motivo 5"],\n'
                '  "raridade": 8,\n'
                '  "tendencia": "Alta valorização",\n'
                '  "valor_mercado": "Texto sobre valor de mercado para colecionadores.",\n'
                '  "estado_produto": ["Estado visível nas fotos", "Funcionamento estimado", "(preencher conforme o item real)"],\n'
                '  "veja_tambem": ["Categoria relacionada 1", "Categoria relacionada 2", "Categoria relacionada 3", "Categoria relacionada 4"],\n'
                '  "links_externos": [{"titulo": "Texto do link", "url": "https://pt.wikipedia.org/wiki/..."}, {"titulo": "Texto 2", "url": "https://..."}],\n'
                '  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],\n'
                '  "yoast_keyphrase": "keyword foco principal SEO em português (2-4 palavras)",\n'
                '  "yoast_title": "DEVE começar com a yoast_keyphrase. Máximo ESTRITO 55 caracteres.",\n'
                '  "yoast_meta": "DEVE conter a yoast_keyphrase. Máximo ESTRITO 155 caracteres. CTA para colecionadores."\n'
                "}\n\n"
                "REGRAS OBRIGATÓRIAS:\n"
                "1. yoast_title DEVE começar pela yoast_keyphrase e ter no máximo 55 chars\n"
                "2. yoast_meta DEVE conter a yoast_keyphrase e ter no máximo 155 chars\n"
                "3. intro DEVE conter a yoast_keyphrase na 1ª ou 2ª frase\n"
                "4. subtitulo DEVE conter a yoast_keyphrase\n"
                "5. links_externos: 2-3 links reais do Wikipedia em português\n"
                "Escreva em português brasileiro."
            )
            content.append({"type":"text","text":prompt})

            self._log("\n  Enviando para Claude Vision (Haiku)...")
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                messages=[{"role":"user","content":content}],
            )
            raw = msg.content[0].text.strip()
            self._log("  Resposta recebida. Parseando JSON...")

            m = _re.search(r'\{[\s\S]*\}', raw)
            if not m:
                raise ValueError(f"JSON não encontrado: {raw[:200]}")
            dados = _json.loads(m.group())

            self._log(f"  Produto: {dados.get('titulo','?')}")
            self._log(f"  Raridade: {dados.get('raridade','?')}/10")

            html            = _gerar_html(dados, WP_URL, WA_NUMBER)
            titulo          = dados.get("titulo", "Produto Colecionável HelioBrinquedos")
            yoast_keyphrase = dados.get("yoast_keyphrase", "")
            yoast_title     = dados.get("yoast_title", titulo[:55])
            yoast_meta      = dados.get("yoast_meta", "")[:155]
            tags_list       = dados.get("tags", [])

            self.post_gerado = {
                "titulo":          titulo,
                "content":         html,
                "yoast_keyphrase": yoast_keyphrase,
                "yoast_title":     yoast_title,
                "yoast_meta":      yoast_meta,
                "hb_seo_desc":     yoast_meta,
                "tags":            tags_list,
                "dados":           dados,
            }

            def _upd():
                self.vars["titulo"].set(titulo)
                self.vars["yoast_keyphrase"].set(yoast_keyphrase)
                self.vars["yoast_title"].set(yoast_title)
                self.vars["yoast_meta"].set(yoast_meta)
                self.vars["tags"].set(", ".join(tags_list))
                self.content_text.config(state=tk.NORMAL)
                self.content_text.delete("1.0", tk.END)
                self.content_text.insert("1.0", html)
                self.lbl_titulo_pub.config(text=titulo)
            self.after(0, _upd)

            self._log(f"\n  Keyword: {yoast_keyphrase}")
            self._log(f"  SEO Title ({len(yoast_title)}ch): {yoast_title}")
            self._log(f"  Meta ({len(yoast_meta)}ch): {yoast_meta}")
            self._log("\n  Post gerado! Revise o conteúdo e clique em Publicar.")

        except Exception as e:
            self._log(f"\n  ❌ Erro: {e}")
            import traceback; traceback.print_exc()
        finally:
            self.running = False
            self.after(0, lambda: (
                self.progress.stop(),
                self.lbl_status.config(text="Post gerado. Revise e publique."),
                self._set_buttons(True),
            ))

    # ── Publicar ──────────────────────────────────────────────────────────────

    def _publicar(self):
        if not self.post_gerado:
            messagebox.showwarning("Aviso", "Gere o post primeiro.")
            return
        if self.running or self.pub_running:
            return
        if not CFG.get("wp_user") or not CFG.get("wp_app_password"):
            messagebox.showerror(
                "Config",
                "HELIO_WP_USER e HELIO_WP_PASS não encontrados no .env."
            )
            return

        self.post_gerado["titulo"]          = self.vars["titulo"].get().strip()
        self.post_gerado["yoast_keyphrase"] = self.vars["yoast_keyphrase"].get().strip()
        self.post_gerado["yoast_title"]     = self.vars["yoast_title"].get().strip()
        self.post_gerado["yoast_meta"]      = self.vars["yoast_meta"].get().strip()
        self.post_gerado["hb_seo_desc"]     = self.vars["yoast_meta"].get().strip()
        self.post_gerado["content"]         = self.content_text.get("1.0", tk.END).strip()
        tags_raw = self.vars["tags"].get()
        self.post_gerado["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]

        self.pub_running = True
        self._set_buttons(False)
        self.progress.start(12)
        self.lbl_status.config(text="Publicando no WordPress...")
        threading.Thread(
            target=self._publicar_worker,
            args=(dict(self.post_gerado), self.var_status.get(),
                  list(self.fotos_selecionadas)),
            daemon=True,
        ).start()

    def _publicar_worker(self, post: dict, status: str, fotos: list):
        try:
            import publisher as pub_mod, re as _re
            importlib.reload(pub_mod)

            self._log("\n  [1/4] Conectando ao WordPress...")
            self._log(f"  URL: {CFG['wp_url']} | user: {CFG['wp_user']}")
            pub = pub_mod.WordPressPublisher(CFG)
            ok = pub.testar_conexao()
            if not ok:
                raise RuntimeError("Falha na autenticação — verifique URL e credenciais.")

            titulo          = post["titulo"]
            content         = post["content"]
            yoast_keyphrase = post.get("yoast_keyphrase", "")
            yoast_title     = post.get("yoast_title", "")
            yoast_meta      = post.get("yoast_meta", "")
            hb_seo_desc     = post.get("hb_seo_desc", yoast_meta)
            tags            = post.get("tags", [])
            dados           = post.get("dados") or {}

            raridade_raw = dados.get("raridade", "")
            try:
                raridade_num = int(raridade_raw)
            except (TypeError, ValueError):
                raridade_num = 0
            if raridade_num >= 9:
                hb_raridade = "Peça Única"
            elif raridade_num >= 7:
                hb_raridade = "Muito Raro"
            elif raridade_num >= 4:
                hb_raridade = "Raro"
            else:
                hb_raridade = str(raridade_raw or "Raro")

            self._log(f"  Título: {titulo}")
            self._log(f"  Keyword: {yoast_keyphrase}")

            # [2/4] Upload fotos
            self._log(f"\n  [2/4] Upload de {len(fotos)} foto(s)...")
            media_ids, media_urls = [], []
            for i, path in enumerate(fotos):
                try:
                    mid, murl = pub.upload_media(path, alt_text=titulo)
                    if mid and murl:
                        media_ids.append(mid)
                        size = "large" if not media_urls else "medium"
                        try:
                            media_info = pub._request(
                                "GET",
                                f"media/{mid}?_fields=source_url,media_details"
                            )
                            sizes = ((media_info.get("media_details") or {}).get("sizes") or {})
                            murl = (sizes.get(size) or {}).get("source_url") or media_info.get("source_url") or murl
                        except Exception:
                            pass
                        media_urls.append(murl)
                        self._log(f"  Foto {i+1}: {Path(path).name} → ID {mid}")
                    else:
                        self._log(f"  ⚠️ Falha upload foto {i+1}: WordPress não retornou mídia válida")
                except Exception as eu:
                    self._log(f"  ⚠️ Falha upload foto {i+1}: {eu}")

            # Injeta fotos nos placeholders
            final_content = content
            if media_ids:
                foto1 = (
                    f'<!-- wp:image {{"id":{media_ids[0]},"sizeSlug":"large","linkDestination":"none"}} -->\n'
                    f'<figure class="wp-block-image size-large">'
                    f'<img src="{media_urls[0]}" alt="{titulo}" class="wp-image-{media_ids[0]}"/>'
                    f'</figure>\n<!-- /wp:image -->'
                )
                final_content = final_content.replace("<!-- HELIO_FOTO_PRINCIPAL -->", foto1)
                galeria = ""
                for mid, murl in zip(media_ids[1:], media_urls[1:]):
                    galeria += (
                        f'<!-- wp:image {{"id":{mid},"sizeSlug":"medium","linkDestination":"none"}} -->\n'
                        f'<figure class="wp-block-image size-medium">'
                        f'<img src="{murl}" alt="{titulo}" class="wp-image-{mid}"/>'
                        f'</figure>\n<!-- /wp:image -->\n'
                    )
                final_content = final_content.replace("<!-- HELIO_FOTOS_GALERIA -->", galeria)
            else:
                final_content = final_content.replace("<!-- HELIO_FOTO_PRINCIPAL -->", "")
                final_content = final_content.replace("<!-- HELIO_FOTOS_GALERIA -->", "")

            # [3/4] Criar post
            self._log("\n  [3/4] Criando post com meta SEO...")
            _t = titulo.lower()
            for _src, _dst in [("áàãâä","a"),("éêë","e"),("íî","i"),("óõôö","o"),("úûü","u"),("ç","c")]:
                _t = _re.sub(f"[{_src}]", _dst, _t)
            slug = _re.sub(r"[^a-z0-9]+", "-", _t).strip("-")[:60]

            payload = {
                "title":   titulo,
                "content": final_content,
                "excerpt": yoast_meta,
                "status":  status,
                "slug":    slug,
                "meta": {
                    "_yoast_wpseo_focuskw":  yoast_keyphrase,
                    "_yoast_wpseo_title":    yoast_title,
                    "_yoast_wpseo_metadesc": yoast_meta,
                    "hb_seo_desc":           hb_seo_desc,
                    "hb_marca":              str(dados.get("marca", "")),
                    "hb_modelo":             str(dados.get("modelo", "")),
                    "hb_tipo":               str(dados.get("tipo", "")),
                    "hb_decada":             str(dados.get("decada", "")),
                    "hb_raridade":           hb_raridade,
                    "hb_conservacao":        ", ".join(dados.get("estado_produto", [])) if isinstance(dados.get("estado_produto"), list) else str(dados.get("estado_produto", "")),
                    "hb_acompanha":          str(dados.get("acompanha", "")),
                    "hb_historia":           str(dados.get("historia", "")),
                    "hb_preco":              str(dados.get("valor_mercado", "")),
                },
            }
            if tags:
                tag_ids = [pub._obter_ou_criar_tag(t) for t in tags]
                payload["tags"] = [tid for tid in tag_ids if tid]
                self._log(f"  Tags: {', '.join(tags[:6])}")
            cat_names = ["Acervo"]
            tipo_l = str(dados.get("tipo", "")).lower()
            if "rel" in tipo_l:
                cat_names.append("Relógios Vintage")
            elif "game" in tipo_l or "jogo" in tipo_l or "videogame" in tipo_l:
                cat_names.append("Games Clássicos")
            elif "action" in tipo_l or "boneco" in tipo_l or "figure" in tipo_l:
                cat_names.append("Action Figures")
            else:
                cat_names.append("Brinquedos Antigos")
            payload["categories"] = [cid for cid in [pub._obter_ou_criar_categoria(c) for c in cat_names] if cid]
            if media_ids:
                payload["featured_media"] = media_ids[0]

            try:
                r = pub._request("POST", "posts", json=payload)
            except Exception as exc:
                msg = str(exc)
                meta_error = any(s in msg for s in (
                    "rest_invalid_param",
                    "_yoast_wpseo",
                    "hb_seo_desc",
                    "meta",
                    "registered",
                ))
                if not meta_error:
                    raise

                self._log("  ⚠️ WordPress rejeitou meta SEO no payload inicial.")
                self._log("     Tentando publicar com meta reduzida...")
                payload_retry = dict(payload)
                if hb_seo_desc:
                    payload_retry["meta"] = {"hb_seo_desc": hb_seo_desc}
                else:
                    payload_retry.pop("meta", None)
                try:
                    r = pub._request("POST", "posts", json=payload_retry)
                except Exception:
                    self._log("     Meta reduzida também falhou. Tentando publicar sem meta SEO...")
                    payload_retry.pop("meta", None)
                    r = pub._request("POST", "posts", json=payload_retry)
            wp_id  = r.get("id")
            wp_url = r.get("link", "")
            self._log(f"  Post criado: ID={wp_id}")

            # Reforça campos que alguns temas/plugins só leem após o post existir.
            reinforce_payload = {
                "excerpt": yoast_meta,
                "meta": {
                    "_yoast_wpseo_focuskw":  yoast_keyphrase,
                    "_yoast_wpseo_title":    yoast_title,
                    "_yoast_wpseo_metadesc": yoast_meta,
                    "hb_seo_desc":           hb_seo_desc,
                    "hb_marca":              str(dados.get("marca", "")),
                    "hb_modelo":             str(dados.get("modelo", "")),
                    "hb_tipo":               str(dados.get("tipo", "")),
                    "hb_decada":             str(dados.get("decada", "")),
                    "hb_raridade":           hb_raridade,
                    "hb_conservacao":        ", ".join(dados.get("estado_produto", [])) if isinstance(dados.get("estado_produto"), list) else str(dados.get("estado_produto", "")),
                    "hb_acompanha":          str(dados.get("acompanha", "")),
                    "hb_historia":           str(dados.get("historia", "")),
                    "hb_preco":              str(dados.get("valor_mercado", "")),
                },
            }
            if media_ids:
                reinforce_payload["featured_media"] = media_ids[0]
            try:
                pub._request("POST", f"posts/{wp_id}", json=reinforce_payload)
            except Exception as exc:
                self._log(f"  ⚠️ Reforço de excerpt/meta não confirmado: {exc}")

            # Verifica Yoast
            verify   = pub._request("GET", f"posts/{wp_id}?context=edit&_fields=meta")
            saved_kw = (verify.get("meta") or {}).get("_yoast_wpseo_focuskw", "")
            saved_md = (verify.get("meta") or {}).get("_yoast_wpseo_metadesc", "")
            self._log(f"  {'✅ Yoast focuskw salvo: '+saved_kw if saved_kw else '⚠️ Yoast focuskw não confirmado — preencha manualmente'}")
            self._log(f"  {'✅ Yoast metadesc salvo ('+str(len(saved_md))+'ch)' if saved_md else '⚠️ Yoast metadesc não confirmado'}")

            # [4/4] Featured image
            self._log("\n  [4/4] Definindo imagem destacada...")
            if media_ids:
                pub._request("POST", f"posts/{wp_id}", json={"featured_media": media_ids[0]})
                self._log(f"  Imagem destacada: ID {media_ids[0]}")

            self._pub_url = wp_url
            self._log(f"\n  ✅ Publicado! URL: {wp_url}")

            def _upd():
                self.lbl_titulo_pub.config(text=titulo)
                self.lbl_link.config(text=wp_url)
            self.after(0, _upd)

            hist_path = Path("posts_helio.json")
            hist = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else []
            hist.append({
                "wp_id": wp_id, "titulo": titulo, "status": status,
                "url": wp_url, "gerado_em": datetime.now().isoformat(),
            })
            hist_path.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")

        except Exception as e:
            self._log(f"\n  ❌ Erro ao publicar: {e}")
            import traceback; traceback.print_exc()
        finally:
            self.pub_running = False
            self.after(0, lambda: (
                self.progress.stop(),
                self.lbl_status.config(text="Concluído."),
                self._set_buttons(True),
            ))

    # ── Limpar ────────────────────────────────────────────────────────────────

    def _limpar(self):
        self.fotos_selecionadas.clear()
        self.fotos_lb.delete(0, tk.END)
        self.lbl_fotos.config(text="Nenhuma foto selecionada")
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)
        for v in self.vars.values():
            v.set("")
        self.lbl_titulo_pub.config(text="—")
        self.lbl_link.config(text="")
        self.lbl_status.config(text="Pronto.")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.post_gerado = None
        self._pub_url = ""


# ── Gerador HTML (função standalone, sem depender do App) ─────────────────────

def _gerar_html(d: dict, wp_url: str, wa_number: str) -> str:
    import urllib.parse as _up

    titulo    = d.get("titulo", "")
    subtitulo = d.get("subtitulo", titulo)
    intro     = d.get("intro", "")
    marca     = d.get("marca", "")
    modelo    = d.get("modelo", "")
    tipo      = d.get("tipo", "")
    funcoes   = d.get("funcoes", "")
    tecno     = d.get("tecnologia", "")
    decada    = d.get("decada", "")
    acompanha = d.get("acompanha", "(preencher conforme o item real)")
    historia  = d.get("historia", "")
    por_que   = d.get("por_que_raro", [])
    raridade  = d.get("raridade", "?")
    tendencia = d.get("tendencia", "Alta valorização")
    valor     = d.get("valor_mercado", "")
    estado    = d.get("estado_produto", [])
    veja      = d.get("veja_tambem", [])
    links_ext = d.get("links_externos", [])

    base = wp_url.rstrip("/")
    wa_msg  = _up.quote(f"Olá! Tenho interesse no produto: {titulo} — da HelioBrinquedos")
    wa_href = f"https://wa.me/{wa_number}?text={wa_msg}"

    def _li(items):
        return "".join(f"<li>{i}</li>" for i in items)

    def _li_links(items):
        return "".join(
            f'<li><a href="{base}/?s={_up.quote(i)}" rel="noopener">{i}</a></li>'
            for i in items
        )

    ext_html = ""
    if links_ext:
        rows = "".join(
            f'<li><a href="{lk["url"]}" target="_blank" rel="noopener noreferrer">{lk.get("titulo","Saiba mais")}</a></li>'
            for lk in links_ext if isinstance(lk, dict) and lk.get("url")
        )
        if rows:
            ext_html = f"\n\n<h2>📚 Saiba Mais</h2>\n<ul>{rows}</ul>"

    wa_btn = (
        f'<p style="text-align:center">'
        f'<a href="{wa_href}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-block;background-color:#25D366;color:#ffffff;'
        f'padding:14px 28px;border-radius:8px;text-decoration:none;'
        f'font-weight:bold;font-size:16px;">📱 Consultar via WhatsApp</a></p>'
    )

    return (
        f"<h2>🧸 {subtitulo}</h2>\n\n"
        f"<p>{intro}</p>\n\n"
        f"<!-- HELIO_FOTO_PRINCIPAL -->\n\n"
        f"<h2>🔍 Detalhes do Produto</h2>\n"
        f"<ul>\n"
        f"<li><strong>Modelo:</strong> {modelo}</li>\n"
        f"<li><strong>Marca:</strong> {marca}</li>\n"
        f"<li><strong>Tipo:</strong> {tipo}</li>\n"
        f"<li><strong>Funções:</strong> {funcoes}</li>\n"
        f"<li><strong>Tecnologia:</strong> {tecno}</li>\n"
        f"<li><strong>Estilo:</strong> Vintage / retrô</li>\n"
        f"<li><strong>Década:</strong> {decada}</li>\n"
        f"<li><strong>Acompanha:</strong> {acompanha}</li>\n"
        f"</ul>\n\n"
        f"<h2>📜 História do Produto</h2>\n"
        f"<p>{historia}</p>\n\n"
        f"<h2>💎 Por que este item é raro?</h2>\n"
        f"<ul>{_li(por_que)}</ul>\n\n"
        f"<p><em>Itens completos (com embalagem) têm valor significativamente maior.</em></p>\n\n"
        f"<h2>💰 Valor de Mercado</h2>\n"
        f"<p>{valor}</p>\n\n"
        f"<h2>⭐ Classificação do Item</h2>\n"
        f"<ul>\n"
        f"<li>⭐ <strong>Raridade:</strong> {raridade}/10</li>\n"
        f"<li>💰 <strong>Valor estimado:</strong> (preencher)</li>\n"
        f"<li>📈 <strong>Tendência:</strong> {tendencia}</li>\n"
        f"</ul>\n\n"
        f"<h2>📦 Estado do Produto</h2>\n"
        f"<!-- HELIO_FOTOS_GALERIA -->\n"
        f"<ul>{_li(estado) if estado else '<li>(Preencher conforme o item real)</li>'}</ul>\n\n"
        f"<h2>🛒 Disponível para Compra</h2>\n"
        f"{wa_btn}\n\n"
        f"<h2>🔗 Veja também</h2>\n"
        f"<ul>{_li_links(veja)}</ul>"
        f"{ext_html}"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = HelioApp()
    app.mainloop()
