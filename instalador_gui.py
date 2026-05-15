"""
Instalador grafico do projeto Clube 3D Brasil.

Uso:
  python instalador_gui.py

A tela ajuda a preparar o computador para rodar o projeto:
- verifica Python/pip
- instala requirements.txt
- salva .env e config.json
- testa WordPress
- cria atalhos .bat locais
- abre app_gui.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import BooleanVar, StringVar, Tk, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
CONFIG_PATH = ROOT / "config.json"
REQUIREMENTS_PATH = ROOT / "requirements.txt"
GUIDE_PATH = ROOT / "GUIA_POSTAGEM.md"


DEFAULT_CONFIG = {
    "planilha_path": "",
    "wp_url": "https://clube3dbrasil.com",
    "posts_por_dia": 10,
    "wp_post_status": "draft",
    "downloads_dir": "./downloads",
    "horario_execucao": "09:00",
    "top10_habilitado": False,
    "ml_afiliado_url": "",
}


def read_env() -> dict[str, str]:
    data: dict[str, str] = {}
    if not ENV_PATH.exists():
        return data
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def write_env(updates: dict[str, str]) -> None:
    existing = read_env()
    existing.update({k: v for k, v in updates.items() if v is not None})
    lines = [f"{key}={value}" for key, value in existing.items() if value != ""]
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except Exception:
            pass
    return config


def write_config(config: dict) -> None:
    merged = read_config()
    merged.update(config)
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")


class InstallerApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Clube 3D Brasil - Instalador")
        self.root.geometry("980x720")
        self.root.minsize(840, 640)

        self.env = read_env()
        self.config = read_config()
        self.running = False

        self.wp_url = StringVar(value=self.config.get("wp_url", DEFAULT_CONFIG["wp_url"]))
        self.wp_user = StringVar(value=self.env.get("WP_USER", ""))
        self.wp_pass = StringVar(value=self.env.get("WP_PASS", ""))
        self.anthropic_key = StringVar(value=self.env.get("ANTHROPIC_API_KEY", ""))
        self.telegram_invite_url = StringVar(value=self.env.get("TELEGRAM_INVITE_URL", ""))
        self.planilha_path = StringVar(value=self.config.get("planilha_path", ""))
        self.downloads_dir = StringVar(value=self.config.get("downloads_dir", "./downloads"))
        self.posts_por_dia = StringVar(value=str(self.config.get("posts_por_dia", 10)))
        self.horario_execucao = StringVar(value=self.config.get("horario_execucao", "09:00"))
        self.status_wp = StringVar(value=self.config.get("wp_post_status", "draft"))
        self.top10_habilitado = BooleanVar(value=bool(self.config.get("top10_habilitado", False)))

        self._build()
        self.log("Instalador aberto em: " + str(ROOT))
        self.log("Dica: preencha os campos e use 'Salvar configuracao' antes de testar o WordPress.")

    def _build(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

        frame = ttk.Frame(self.root, padding=14)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Instalador Clube 3D Brasil", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            top,
            text="Prepare este computador para gerar posts, publicar no WordPress e rodar a automacao.",
        ).pack(anchor="w", pady=(4, 0))

        body = ttk.PanedWindow(frame, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        self._build_config(left)
        self._build_actions(right)
        self._build_log(frame)

    def _build_config(self, parent: ttk.Frame) -> None:
        wp_box = ttk.LabelFrame(parent, text="WordPress", padding=10, style="Section.TLabelframe")
        wp_box.pack(fill="x", pady=(0, 10))
        self._entry(wp_box, "URL do site", self.wp_url)
        self._entry(wp_box, "Usuario", self.wp_user)
        self._entry(wp_box, "Application Password", self.wp_pass, show="*")

        api_box = ttk.LabelFrame(parent, text="APIs opcionais", padding=10, style="Section.TLabelframe")
        api_box.pack(fill="x", pady=(0, 10))
        self._entry(api_box, "ANTHROPIC_API_KEY", self.anthropic_key, show="*")
        self._entry(api_box, "TELEGRAM_INVITE_URL", self.telegram_invite_url)

        general_box = ttk.LabelFrame(parent, text="Projeto", padding=10, style="Section.TLabelframe")
        general_box.pack(fill="x")
        self._path_entry(general_box, "Planilha .xlsx", self.planilha_path, [("Excel", "*.xlsx"), ("Todos", "*.*")])
        self._path_entry(general_box, "Pasta downloads", self.downloads_dir, directory=True)
        self._entry(general_box, "Posts por dia", self.posts_por_dia)
        self._entry(general_box, "Horario diario", self.horario_execucao)

        row = ttk.Frame(general_box)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Status WordPress", width=20).pack(side="left")
        ttk.Combobox(row, textvariable=self.status_wp, values=("draft", "publish"), state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Checkbutton(general_box, text="Habilitar Top 10", variable=self.top10_habilitado).pack(anchor="w", pady=4)

    def _build_actions(self, parent: ttk.Frame) -> None:
        box = ttk.LabelFrame(parent, text="Acoes", padding=10, style="Section.TLabelframe")
        box.pack(fill="x")

        actions = [
            ("1. Verificar ambiente", self.check_environment),
            ("2. Instalar dependencias", self.install_requirements),
            ("3. Salvar configuracao", self.save_configuration),
            ("4. Testar WordPress", self.test_wordpress),
            ("5. Criar atalhos .bat", self.create_shortcuts),
            ("6. Abrir app principal", self.open_main_app),
        ]
        for text, command in actions:
            ttk.Button(box, text=text, command=command).pack(fill="x", pady=5)

        ttk.Separator(box).pack(fill="x", pady=12)
        ttk.Button(box, text="Instalacao rapida (1 a 5)", command=self.quick_install).pack(fill="x", pady=5)
        ttk.Button(box, text="Abrir pasta do projeto", command=self.open_project_folder).pack(fill="x", pady=5)

        guide = ttk.LabelFrame(parent, text="Sequencia para criar um post", padding=10, style="Section.TLabelframe")
        guide.pack(fill="both", expand=True, pady=(10, 0))

        ttk.Label(
            guide,
            text=(
                "Depois que o ambiente estiver pronto, siga este fluxo:\n\n"
                "1. Escolha o tema prioritario do dia.\n"
                "2. Abra o app principal.\n"
                "3. Use Post Web para pesquisar paginas BR/US ou YouTube para partir de video.\n"
                "4. Carregue afiliados e selecione fotos quando o post tiver produto.\n"
                "5. Gere o post SEO como rascunho.\n"
                "6. Revise titulo, Yoast, imagens e links no WordPress.\n"
                "7. Publique e divulgue em Pinterest, WhatsApp e Telegram."
            ),
            justify="left",
            wraplength=330,
        ).pack(fill="both", expand=True, anchor="n")

        ttk.Button(guide, text="Abrir guia completo de postagem", command=self.open_posting_guide).pack(
            fill="x", pady=(10, 0)
        )

    def _build_log(self, parent: ttk.Frame) -> None:
        log_box = ttk.LabelFrame(parent, text="Log", padding=8, style="Section.TLabelframe")
        log_box.pack(fill="both", expand=False, pady=(12, 0))
        self.output = ScrolledText(log_box, height=11, wrap="word")
        self.output.pack(fill="both", expand=True)

    def _entry(self, parent: ttk.Frame, label: str, var: StringVar, show: str | None = None) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=20).pack(side="left")
        ttk.Entry(row, textvariable=var, show=show).pack(side="left", fill="x", expand=True)

    def _path_entry(
        self,
        parent: ttk.Frame,
        label: str,
        var: StringVar,
        filetypes: list[tuple[str, str]] | None = None,
        directory: bool = False,
    ) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=20).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="...", width=4, command=lambda: self._browse(var, filetypes, directory)).pack(
            side="left", padx=(6, 0)
        )

    def _browse(self, var: StringVar, filetypes: list[tuple[str, str]] | None, directory: bool) -> None:
        if directory:
            selected = filedialog.askdirectory(initialdir=str(ROOT))
        else:
            selected = filedialog.askopenfilename(initialdir=str(ROOT), filetypes=filetypes or [("Todos", "*.*")])
        if selected:
            var.set(selected)

    def log(self, message: str) -> None:
        self.output.insert("end", message + "\n")
        self.output.see("end")
        self.root.update_idletasks()

    def run_threaded(self, title: str, target) -> None:
        if self.running:
            messagebox.showinfo("Aguarde", "Ja existe uma acao em execucao.")
            return

        def runner():
            self.running = True
            self.log("")
            self.log("== " + title + " ==")
            try:
                target()
            except Exception as exc:
                self.log("ERRO: " + str(exc))
                messagebox.showerror("Erro", str(exc))
            finally:
                self.running = False

        threading.Thread(target=runner, daemon=True).start()

    def run_command(self, args: list[str]) -> int:
        self.log("$ " + " ".join(args))
        proc = subprocess.Popen(
            args,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            self.log(line.rstrip())
        proc.wait()
        self.log(f"Codigo de saida: {proc.returncode}")
        return int(proc.returncode)

    def check_environment(self) -> None:
        self.run_threaded("Verificar ambiente", self._check_environment)

    def _check_environment(self) -> None:
        self.log("Python: " + sys.version.replace("\n", " "))
        self.run_command([sys.executable, "--version"])
        self.run_command([sys.executable, "-m", "pip", "--version"])
        self.log("requirements.txt: " + ("OK" if REQUIREMENTS_PATH.exists() else "NAO ENCONTRADO"))
        self.log(".env: " + ("existe" if ENV_PATH.exists() else "nao existe ainda"))
        self.log("config.json: " + ("existe" if CONFIG_PATH.exists() else "nao existe ainda"))

    def install_requirements(self) -> None:
        self.run_threaded("Instalar dependencias", self._install_requirements)

    def _install_requirements(self) -> None:
        if not REQUIREMENTS_PATH.exists():
            raise RuntimeError("requirements.txt nao encontrado.")
        code = self.run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)])
        if code != 0:
            raise RuntimeError("Instalacao de dependencias falhou.")

    def save_configuration(self) -> None:
        self.run_threaded("Salvar configuracao", self._save_configuration)

    def _save_configuration(self) -> None:
        try:
            posts_por_dia = int(self.posts_por_dia.get().strip() or "10")
        except ValueError as exc:
            raise RuntimeError("Posts por dia precisa ser numero inteiro.") from exc

        config = {
            "planilha_path": self.planilha_path.get().strip(),
            "wp_url": self.wp_url.get().strip().rstrip("/") or DEFAULT_CONFIG["wp_url"],
            "posts_por_dia": posts_por_dia,
            "wp_post_status": self.status_wp.get().strip() or "draft",
            "downloads_dir": self.downloads_dir.get().strip() or "./downloads",
            "horario_execucao": self.horario_execucao.get().strip() or "09:00",
            "top10_habilitado": bool(self.top10_habilitado.get()),
        }
        write_config(config)

        env_updates = {
            "WP_USER": self.wp_user.get().strip(),
            "WP_PASS": self.wp_pass.get().strip(),
            "ANTHROPIC_API_KEY": self.anthropic_key.get().strip(),
            "TELEGRAM_INVITE_URL": self.telegram_invite_url.get().strip(),
        }
        write_env(env_updates)

        Path(config["downloads_dir"]).mkdir(parents=True, exist_ok=True)
        self.log("Configuracao salva em config.json e .env.")
        self.log("Credenciais ficam locais e nao entram no Git.")

    def test_wordpress(self) -> None:
        self.run_threaded("Testar WordPress", self._test_wordpress)

    def _test_wordpress(self) -> None:
        self._save_configuration()
        import publisher

        cfg = read_config()
        cfg["wp_user"] = self.wp_user.get().strip()
        cfg["wp_app_password"] = self.wp_pass.get().strip()
        pub = publisher.WordPressPublisher(cfg)
        ok = pub.testar_conexao()
        if not ok:
            raise RuntimeError("Falha no teste WordPress. Verifique usuario e Application Password.")
        self.log("WordPress conectado com sucesso.")

    def create_shortcuts(self) -> None:
        self.run_threaded("Criar atalhos .bat", self._create_shortcuts)

    def _create_shortcuts(self) -> None:
        shortcuts = {
            "abrir_instalador_gui.bat": "@echo off\ncd /d \"%~dp0\"\npython instalador_gui.py\npause\n",
            "abrir_app_principal.bat": "@echo off\ncd /d \"%~dp0\"\npython app_gui.py\npause\n",
            "instalar_dependencias.bat": (
                "@echo off\ncd /d \"%~dp0\"\npython -m pip install -r requirements.txt\npause\n"
            ),
        }
        for name, content in shortcuts.items():
            (ROOT / name).write_text(content, encoding="utf-8")
            self.log("Criado: " + name)

    def open_main_app(self) -> None:
        self.run_threaded("Abrir app principal", self._open_main_app)

    def _open_main_app(self) -> None:
        self._save_configuration()
        subprocess.Popen([sys.executable, "app_gui.py"], cwd=ROOT)
        self.log("app_gui.py iniciado em uma nova janela/processo.")

    def open_project_folder(self) -> None:
        os.startfile(str(ROOT))

    def open_posting_guide(self) -> None:
        if not GUIDE_PATH.exists():
            messagebox.showwarning("Guia nao encontrado", "O arquivo GUIA_POSTAGEM.md nao foi encontrado.")
            return
        os.startfile(str(GUIDE_PATH))

    def quick_install(self) -> None:
        def run_all():
            self._check_environment()
            self._install_requirements()
            self._save_configuration()
            self._test_wordpress()
            self._create_shortcuts()
            self.log("Instalacao rapida concluida.")

        self.run_threaded("Instalacao rapida", run_all)


def main() -> None:
    os.chdir(ROOT)
    root = Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
