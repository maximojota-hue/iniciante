"""
painel.py — Painel de Automação Clube 3D Brasil
Fluxo: configurar → fonte de dados → executar post a post com imagem manual obrigatória
"""

import json
import queue
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import random

# ── Paleta ────────────────────────────────────────────────────────────────────

BG       = "#12121f"
BG2      = "#1a1a2e"
BG3      = "#252540"
ACCENT   = "#7c6af7"
ACCENT2  = "#5b4fe8"
GREEN    = "#4ade80"
YELLOW   = "#fbbf24"
RED      = "#f87171"
TEXT     = "#e2e8f0"
TEXT_DIM = "#64748b"
WHITE    = "#ffffff"

FONT    = ("Segoe UI", 10)
FONT_B  = ("Segoe UI", 10, "bold")
FONT_XS = ("Segoe UI", 9)
FONT_LG = ("Segoe UI", 14, "bold")

# ── Dados para modo automático ────────────────────────────────────────────────

MODELOS_AUTO = [
    {"nome": "Pikachu Articulado",          "tema": "Games e Anime",  "descricao": "Pikachu articulado print-in-place sem suporte para impressão FDM.",              "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Vaso Geométrico Moderno",     "tema": "Decoração",      "descricao": "Vaso decorativo geométrico ideal para impressão em vase mode.",                  "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Suporte para Celular",        "tema": "Utilidades",     "descricao": "Suporte ajustável para smartphone com múltiplos ângulos.",                      "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Mandalorian Helmet",          "tema": "Games e Anime",  "descricao": "Capacete do Mandalorian para cosplay em escala real.",                         "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Organizador de Gaveta",       "tema": "Utilidades",     "descricao": "Divisórias modulares encaixáveis para organização de gavetas.",                "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Dragon Flexi Articulado",     "tema": "Games e Anime",  "descricao": "Dragão articulado sem suporte — imprime pronto para uso.",                    "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Placa de Endereço",           "tema": "Decoração",      "descricao": "Placa numerada personalizável para fachada residencial.",                     "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Suporte Headset Gamer",       "tema": "Utilidades",     "descricao": "Suporte de mesa elegante para fone de ouvido gamer.",                        "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Baby Yoda Grogu",             "tema": "Games e Anime",  "descricao": "Grogu de Star Wars em alta fidelidade para impressão FDM.",                  "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Engrenagem Steampunk",        "tema": "Decoração",      "descricao": "Engrenagens decorativas estilo steampunk para parede ou mesa.",               "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Cachepô para Suculentas",     "tema": "Decoração",      "descricao": "Vaso moderno e leve para suculentas e cactos.",                              "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Terreno Modular RPG",         "tema": "Miniaturas",     "descricao": "Set de terrenos modulares compatíveis para RPG de mesa.",                    "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Stormtrooper Helmet",         "tema": "Games e Anime",  "descricao": "Capacete Stormtrooper Star Wars em escala real para cosplay.",               "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Porta Temperos Giratório",    "tema": "Cozinha",        "descricao": "Porta-temperos giratório para potes de até 50 ml.",                         "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
    {"nome": "Cubo Fidget Anti-estresse",   "tema": "Utilidades",     "descricao": "Cubo anti-estresse print-in-place com botões e switches clicáveis.",        "url_fonte": "https://makerworld.com", "url_makerworld": "https://makerworld.com", "criador": "Comunidade MakerWorld"},
]

AFILIADOS_PADRAO = [
    {"keyword": "impressora 3d", "nome": "Impressora 3D Bambu Lab A1 Mini",      "link": "https://amzn.to/bambulab-a1-mini"},
    {"keyword": "filamento pla", "nome": "Filamento PLA 1kg Polymaker PolyLite", "link": "https://amzn.to/filamento-pla-polymaker"},
    {"keyword": "impressão 3d",  "nome": "Kit Iniciante Impressão 3D",           "link": "https://meli.la/1Zz31yZ"},
]


# ── App principal ─────────────────────────────────────────────────────────────

class PainelApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Clube 3D Brasil — Painel de Automação")
        self.root.geometry("1000x660")
        self.root.minsize(860, 580)
        self.root.configure(bg=BG)

        self.ui_queue  = queue.Queue()   # worker → main: logs, controle
        self.img_queue = queue.Queue()   # main → worker: path da imagem ou ""
        self.rodando   = False

        self.var_wp_url  = tk.StringVar(value="https://clube3dbrasil.com")
        self.var_wp_user = tk.StringVar()
        self.var_wp_pass = tk.StringVar()
        self.var_fonte   = tk.StringVar(value="manual")
        self.var_xlsx    = tk.StringVar()
        self.var_qtd     = tk.IntVar(value=5)
        self.var_monet   = tk.StringVar(value="padrao")
        self.var_af_xlsx = tk.StringVar()
        self.var_img_dir = tk.StringVar()

        self._load_env()
        self._setup_styles()
        self._build_ui()
        self.root.after(100, self._poll_queue)
        self.root.mainloop()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _load_env(self):
        for env_path in [Path(".env"), Path(__file__).parent / ".env"]:
            if env_path.exists():
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        if k.strip() == "WP_USER":
                            self.var_wp_user.set(v.strip())
                        elif k.strip() == "WP_PASS":
                            self.var_wp_pass.set(v.strip())
                break

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=TEXT, font=FONT, borderwidth=0, relief="flat")
        s.configure("TFrame",      background=BG)
        s.configure("TLabel",      background=BG,  foreground=TEXT,     font=FONT)
        s.configure("TEntry",      fieldbackground=BG3, foreground=TEXT, insertcolor=TEXT, borderwidth=1)
        s.configure("TButton",     background=BG3, foreground=TEXT, padding=(8, 5))
        s.map("TButton",           background=[("active", ACCENT2), ("disabled", BG2)],
                                   foreground=[("disabled", TEXT_DIM)])
        s.configure("Accent.TButton", background=ACCENT, foreground=WHITE, font=FONT_B, padding=(14, 9))
        s.map("Accent.TButton",    background=[("active", ACCENT2), ("disabled", BG3)],
                                   foreground=[("disabled", TEXT_DIM)])
        s.configure("TRadiobutton", background=BG2, foreground=TEXT,  font=FONT)
        s.map("TRadiobutton",       background=[("active", BG2)])
        s.configure("TSpinbox",    fieldbackground=BG3, foreground=TEXT, arrowcolor=TEXT)
        s.configure("TProgressbar", background=ACCENT, troughcolor=BG3, thickness=12)
        s.configure("TScrollbar",  background=BG3, troughcolor=BG2, arrowcolor=TEXT_DIM)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=BG2, height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🖨️  Clube 3D Brasil — Painel de Automação",
                 bg=BG2, fg=WHITE, font=FONT_LG).pack(side=tk.LEFT, padx=20, pady=14)
        tk.Label(hdr, text="v1.0", bg=BG2, fg=TEXT_DIM, font=FONT_XS).pack(side=tk.RIGHT, padx=20)
        ttk.Button(hdr, text="🖥️  Abrir App GUI",
                   command=self._abrir_app_gui).pack(side=tk.RIGHT, padx=(0, 12), pady=10)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main, bg=BG, width=400)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(14, 6), pady=14)
        left.pack_propagate(False)

        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 14), pady=14)

        self._build_left(left)
        self._build_right(right)

    def _section(self, parent, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=BG2)
        outer.pack(fill=tk.X, pady=(0, 10))
        tk.Label(outer, text=title, bg=BG2, fg=ACCENT, font=FONT_B).pack(
            anchor=tk.W, padx=12, pady=(10, 4))
        inner = tk.Frame(outer, bg=BG2)
        inner.pack(fill=tk.X, padx=12, pady=(0, 12))
        return inner

    def _field(self, parent, label: str, var, show=""):
        row = tk.Frame(parent, bg=BG2)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text=label, bg=BG2, fg=TEXT_DIM, font=FONT, width=9, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var, show=show).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_left(self, parent):

        # ── WordPress ─────────────────────────────────────────────────────
        sec = self._section(parent, "🌐  Configuração WordPress")
        self._field(sec, "URL",     self.var_wp_url)
        self._field(sec, "Usuário", self.var_wp_user)
        self._field(sec, "Senha",   self.var_wp_pass, show="•")

        row_test = tk.Frame(sec, bg=BG2)
        row_test.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(row_test, text="🔗 Testar Conexão",
                   command=self._testar_conexao).pack(side=tk.LEFT)
        self.lbl_conn = tk.Label(row_test, text="", bg=BG2, fg=TEXT_DIM, font=FONT_XS)
        self.lbl_conn.pack(side=tk.LEFT, padx=10)

        # ── Fonte de dados ─────────────────────────────────────────────────
        sec2 = self._section(parent, "📊  Fonte de Dados")
        ttk.Radiobutton(sec2, text="Automático — usa lista de tendências interna",
                        variable=self.var_fonte, value="auto",
                        command=self._on_fonte).pack(anchor=tk.W)
        ttk.Radiobutton(sec2, text="Manual — planilha .xlsx  (colunas: nome, link)",
                        variable=self.var_fonte, value="manual",
                        command=self._on_fonte).pack(anchor=tk.W, pady=(3, 6))

        self.frame_xlsx = tk.Frame(sec2, bg=BG2)
        self.frame_xlsx.pack(fill=tk.X)
        ttk.Entry(self.frame_xlsx, textvariable=self.var_xlsx).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.frame_xlsx, text="📂", width=3,
                   command=lambda: self._browse_file(self.var_xlsx)).pack(side=tk.LEFT, padx=(4, 0))

        row_qtd = tk.Frame(sec2, bg=BG2)
        row_qtd.pack(fill=tk.X, pady=(10, 0))
        tk.Label(row_qtd, text="Quantidade de posts:", bg=BG2, fg=TEXT, font=FONT).pack(side=tk.LEFT)
        ttk.Spinbox(row_qtd, from_=1, to=200, textvariable=self.var_qtd,
                    width=6, font=FONT).pack(side=tk.LEFT, padx=(10, 0))

        # ── Monetização ────────────────────────────────────────────────────
        sec3 = self._section(parent, "💰  Monetização")
        ttk.Radiobutton(sec3, text="Lista padrão do sistema",
                        variable=self.var_monet, value="padrao",
                        command=self._on_monet).pack(anchor=tk.W)
        ttk.Radiobutton(sec3, text="Planilha de afiliados  (colunas: nome, link, tipo)",
                        variable=self.var_monet, value="planilha",
                        command=self._on_monet).pack(anchor=tk.W, pady=(3, 6))

        self.frame_af = tk.Frame(sec3, bg=BG2)
        self.frame_af.pack(fill=tk.X)
        ttk.Entry(self.frame_af, textvariable=self.var_af_xlsx).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.frame_af, text="📂", width=3,
                   command=lambda: self._browse_file(self.var_af_xlsx)).pack(side=tk.LEFT, padx=(4, 0))

        # ── Pasta de imagens ───────────────────────────────────────────────
        sec4 = self._section(parent, "🖼️  Pasta de Imagens (opcional)")
        row_img = tk.Frame(sec4, bg=BG2)
        row_img.pack(fill=tk.X)
        ttk.Entry(row_img, textvariable=self.var_img_dir).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row_img, text="📂", width=3,
                   command=self._browse_dir).pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(sec4, text="O diálogo de imagem abre direto nesta pasta",
                 bg=BG2, fg=TEXT_DIM, font=FONT_XS).pack(anchor=tk.W, pady=(5, 0))

        self._on_fonte()
        self._on_monet()

    def _build_right(self, parent):
        tk.Label(parent, text="📋  Log em tempo real",
                 bg=BG, fg=ACCENT, font=FONT_B).pack(anchor=tk.W)

        log_frame = tk.Frame(parent, bg=BG3)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 10))

        self.log = tk.Text(
            log_frame, bg=BG2, fg=TEXT, font=("Consolas", 9),
            wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT,
            insertbackground=TEXT, selectbackground=ACCENT,
        )
        vsb = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log.yview)
        self.log.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.log.tag_configure("ok",   foreground=GREEN)
        self.log.tag_configure("warn", foreground=YELLOW)
        self.log.tag_configure("err",  foreground=RED)
        self.log.tag_configure("dim",  foreground=TEXT_DIM)
        self.log.tag_configure("head", foreground=ACCENT, font=FONT_B)

        # Progresso
        prog = tk.Frame(parent, bg=BG)
        prog.pack(fill=tk.X, pady=(0, 10))

        self.lbl_prog = tk.Label(prog, text="Aguardando...", bg=BG, fg=TEXT_DIM, font=FONT_XS)
        self.lbl_prog.pack(anchor=tk.W)

        self.pvar = tk.DoubleVar(value=0)
        ttk.Progressbar(prog, variable=self.pvar, maximum=100).pack(fill=tk.X, pady=(4, 0))

        # Botão executar
        self.btn_exec = ttk.Button(parent, text="🚀  Executar",
                                   style="Accent.TButton", command=self._executar)
        self.btn_exec.pack(fill=tk.X, ipady=4)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _on_fonte(self):
        st = "normal" if self.var_fonte.get() == "manual" else "disabled"
        for w in self.frame_xlsx.winfo_children():
            try: w.configure(state=st)
            except tk.TclError: pass

    def _on_monet(self):
        st = "normal" if self.var_monet.get() == "planilha" else "disabled"
        for w in self.frame_af.winfo_children():
            try: w.configure(state=st)
            except tk.TclError: pass

    def _browse_file(self, var):
        path = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")])
        if path:
            var.set(path)

    def _browse_dir(self):
        path = filedialog.askdirectory(title="Pasta de imagens")
        if path:
            self.var_img_dir.set(path)

    def _append_log(self, msg: str, tag: str = ""):
        self.log.configure(state=tk.NORMAL)
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {msg}\n", tag)
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _clear_log(self):
        self.log.configure(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.configure(state=tk.DISABLED)

    def _set_running(self, on: bool):
        self.rodando = on
        self.btn_exec.configure(state=tk.DISABLED if on else tk.NORMAL)

    # ── Teste de conexão ──────────────────────────────────────────────────────

    def _testar_conexao(self):
        self.lbl_conn.config(text="Testando...", fg=YELLOW)
        threading.Thread(target=self._testar_conexao_th, daemon=True).start()

    def _testar_conexao_th(self):
        try:
            from publisher import WordPressPublisher
            pub = WordPressPublisher({
                "wp_url":          self.var_wp_url.get(),
                "wp_user":         self.var_wp_user.get(),
                "wp_app_password": self.var_wp_pass.get(),
            })
            ok = pub.testar_conexao()
            msg, cor = ("✅ Conectado!", GREEN) if ok else ("❌ Falha", RED)
        except Exception as e:
            msg, cor = f"❌ {e}", RED
        self.root.after(0, lambda: self.lbl_conn.config(text=msg, fg=cor))

    def _abrir_app_gui(self):
        import subprocess, sys
        app = Path(__file__).parent / "app_gui.py"
        subprocess.Popen([sys.executable, str(app)], cwd=str(Path(__file__).parent))

    # ── Execução ──────────────────────────────────────────────────────────────

    def _executar(self):
        if not self.var_wp_url.get().startswith("http"):
            messagebox.showwarning("Atenção", "Informe a URL do WordPress.")
            return
        if not self.var_wp_user.get() or not self.var_wp_pass.get():
            messagebox.showwarning("Atenção", "Preencha usuário e senha.")
            return
        if self.var_fonte.get() == "manual" and not self.var_xlsx.get():
            messagebox.showwarning("Atenção", "Selecione a planilha de modelos.")
            return

        self._clear_log()
        self.pvar.set(0)
        self.lbl_prog.config(text="Iniciando...", fg=TEXT_DIM)
        self._set_running(True)
        threading.Thread(target=self._worker, daemon=True).start()

    # ── Worker (thread) ───────────────────────────────────────────────────────

    def _worker(self):
        try:
            from publisher import WordPressPublisher, WordPressApiError
            from gerador import gerar_post_v3, gerar_post_v5

            config = {
                "wp_url":          self.var_wp_url.get().rstrip("/"),
                "wp_user":         self.var_wp_user.get(),
                "wp_app_password": self.var_wp_pass.get(),
                "wp_post_status":  "draft",
            }

            # 1. Conexão
            self._qlog("🔗 Verificando conexão com WordPress...", "dim")
            pub = WordPressPublisher(config)
            if not pub.testar_conexao():
                self._qlog("❌ Falha na autenticação. Verifique as credenciais.", "err")
                self.ui_queue.put({"t": "done"})
                return
            self._qlog("✅ Conectado!\n", "ok")

            # 2. Modelos
            qtd = self.var_qtd.get()
            if self.var_fonte.get() == "auto":
                modelos = MODELOS_AUTO[:qtd]
                self._qlog(f"📋 Modo automático — {len(modelos)} modelo(s) selecionado(s)\n", "dim")
            else:
                modelos = self._ler_xlsx_modelos(self.var_xlsx.get(), qtd)
                if not modelos:
                    self._qlog("❌ Planilha vazia ou sem dados válidos.", "err")
                    self.ui_queue.put({"t": "done"})
                    return
                self._qlog(f"📋 Planilha carregada — {len(modelos)} modelo(s)\n", "dim")

            # 3. Afiliados
            if self.var_monet.get() == "planilha" and self.var_af_xlsx.get():
                afiliados = self._ler_xlsx_afiliados(self.var_af_xlsx.get())
                self._qlog(f"💰 {len(afiliados)} afiliado(s) da planilha\n", "dim")
            else:
                afiliados = AFILIADOS_PADRAO
                self._qlog("💰 Usando lista padrão de afiliados\n", "dim")

            # 4. Loop post a post
            total      = len(modelos)
            publicados = []

            for i, modelo in enumerate(modelos, 1):
                nome = modelo["nome"]
                self._qlog("─" * 44, "dim")
                self._qlog(f"📝 Post {i}/{total}: {nome}", "head")

                # Gerar conteúdo SEO + monetização
                try:
                    post = gerar_post_v5(modelo, publicados, afiliados) if afiliados else gerar_post_v3(modelo, publicados)
                except Exception:
                    post = gerar_post_v3(modelo, publicados)
                post["status"] = "draft"
                self._qlog("   ✏️  Conteúdo gerado (SEO + monetização)", "ok")

                # ── PAUSA: solicitar imagem ────────────────────────────────
                self.ui_queue.put({"t": "img", "nome": nome, "i": i, "total": total})
                img_path = self.img_queue.get()          # bloqueia aqui

                if img_path:
                    post["featured_image_path"] = img_path
                    self._qlog(f"   🖼️  Imagem: {Path(img_path).name}", "ok")
                else:
                    self._qlog("   ⏭️  Imagem pulada", "dim")

                # Publicar
                self._qlog("   📤 Publicando...", "dim")
                try:
                    res = pub.publicar_post(post, skip_if_exists=True)
                    if res:
                        self._qlog(f"   ✅ {res.get('url', '')}", "ok")
                        publicados.append({"titulo": res["titulo"], "url": res.get("url", ""), "tema": modelo.get("tema", "3D")})
                    else:
                        self._qlog("   ❌ Sem retorno do WordPress", "err")
                except WordPressApiError as exc:
                    self._qlog(f"   ❌ Erro WP: {exc}", "err")
                except Exception as exc:
                    self._qlog(f"   ❌ {exc}", "err")

                self.ui_queue.put({"t": "prog", "i": i, "total": total})

            self._qlog("═" * 44, "dim")
            self._qlog(f"✅ Concluído! {len(publicados)}/{total} post(s) publicado(s).", "ok")

        except Exception as exc:
            import traceback
            self._qlog(f"❌ Erro inesperado: {exc}", "err")
            self._qlog(traceback.format_exc(), "err")
        finally:
            self.ui_queue.put({"t": "done"})

    def _qlog(self, msg: str, tag: str = ""):
        self.ui_queue.put({"t": "log", "msg": msg, "tag": tag})

    # ── Poll fila (main thread) ───────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                tp = item["t"]

                if tp == "log":
                    self._append_log(item["msg"], item.get("tag", ""))

                elif tp == "img":
                    self._dialog_imagem(item["nome"], item["i"], item["total"])

                elif tp == "prog":
                    at, tot = item["i"], item["total"]
                    self.pvar.set(at / tot * 100)
                    bar_len  = min(tot, 20)
                    filled   = round(at / tot * bar_len)
                    bar      = "█" * filled + "░" * (bar_len - filled)
                    pct      = at * 100 // tot
                    self.lbl_prog.config(text=f"Post {at} de {tot}   [{bar}]  {pct}%", fg=TEXT)

                elif tp == "done":
                    self._set_running(False)
                    self.lbl_prog.config(text="Concluído ✅", fg=GREEN)

        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    # ── Diálogo de imagem (main thread) ──────────────────────────────────────

    def _dialog_imagem(self, nome: str, index: int, total: int):
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Selecionar imagem — Post {index} de {total}")
        dlg.geometry("560x270")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.focus_set()
        dlg.protocol("WM_DELETE_WINDOW", lambda: _pular())

        pad = 22

        tk.Label(dlg, text=f"Post {index} de {total}",
                 bg=BG, fg=TEXT_DIM, font=FONT_XS).pack(pady=(pad, 2))
        tk.Label(dlg, text="Selecione a imagem para:",
                 bg=BG, fg=TEXT, font=FONT).pack()
        tk.Label(dlg, text=f'"{nome}"',
                 bg=BG, fg=ACCENT, font=FONT_B, wraplength=500).pack(pady=(4, pad // 2))

        # Exibe o caminho selecionado
        var_path = tk.StringVar(value="Nenhuma imagem selecionada")
        frame_path = tk.Frame(dlg, bg=BG3, padx=10, pady=6)
        frame_path.pack(fill=tk.X, padx=pad)
        tk.Label(frame_path, textvariable=var_path, bg=BG3, fg=TEXT_DIM,
                 font=FONT_XS, anchor=tk.W, wraplength=500).pack(fill=tk.X)

        def _selecionar():
            init = self.var_img_dir.get() or str(Path.home())
            path = filedialog.askopenfilename(
                parent=dlg,
                title="Selecionar imagem",
                initialdir=init,
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp *.gif"), ("Todos", "*.*")],
            )
            if path:
                var_path.set(Path(path).name)
                var_path._full = path   # guarda o caminho completo

        def _confirmar():
            full = getattr(var_path, "_full", "")
            if not full or not Path(full).exists():
                messagebox.showwarning("Aviso", "Selecione uma imagem válida ou clique em Pular.", parent=dlg)
                return
            dlg.destroy()
            self.img_queue.put(full)

        def _pular():
            dlg.destroy()
            self.img_queue.put("")

        btn_row = tk.Frame(dlg, bg=BG)
        btn_row.pack(pady=pad)
        ttk.Button(btn_row, text="📂  Selecionar Imagem", command=_selecionar).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="✅  Confirmar", style="Accent.TButton", command=_confirmar).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="⏭️  Pular", command=_pular).pack(side=tk.LEFT)

    # ── Leitores de planilha ──────────────────────────────────────────────────

    def _ler_xlsx_modelos(self, path: str, limite: int) -> list[dict]:
        try:
            import pandas as pd
            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]
            result = []
            for _, row in df.iterrows():
                nome = str(row.get("nome", "")).strip()
                if not nome or nome == "nan":
                    continue
                link  = str(row.get("link", "")).strip()
                tema  = str(row.get("tema", "Geral")).strip()
                if tema  == "nan": tema  = "Geral"
                if link  == "nan": link  = "https://makerworld.com"
                descricao = str(row.get("descricao", "")).strip()
                if not descricao or descricao == "nan":
                    descricao = f"Modelo 3D {nome} disponível para impressão FDM."
                result.append({
                    "nome":           nome,
                    "tema":           tema,
                    "descricao":      descricao,
                    "url_fonte":      link,
                    "url_makerworld": link,
                    "criador":        str(row.get("criador", "")).strip() or "",
                })
                if len(result) >= limite:
                    break
            return result
        except Exception as e:
            self._qlog(f"Erro ao ler planilha de modelos: {e}", "err")
            return []

    def _ler_xlsx_afiliados(self, path: str) -> list[dict]:
        try:
            import pandas as pd
            df = pd.read_excel(path)
            df.columns = [c.strip().lower() for c in df.columns]
            _map = {
                "impressora": "impressora 3d", "filamento": "filamento pla",
                "acessorio":  "impressora 3d", "acessório": "impressora 3d",
                "outro":      "impressão 3d",
            }
            result = []
            for _, row in df.iterrows():
                nome = str(row.get("nome") or row.get("nome_produto", "")).strip()
                link = str(row.get("link", "")).strip()
                tipo = str(row.get("tipo", "outro")).strip().lower()
                if nome and link and link != "nan":
                    result.append({"keyword": _map.get(tipo, "impressão 3d"), "nome": nome, "link": link})
            return result or AFILIADOS_PADRAO
        except Exception:
            return AFILIADOS_PADRAO


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent)
    PainelApp()
