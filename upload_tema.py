"""
upload_tema.py — Faz upload do style.css harmonizado para o servidor WordPress via FTP.

Uso:
    python upload_tema.py

Preencha FTP_HOST, FTP_USER e FTP_PASS antes de rodar.
"""

import ftplib
import os

# ─── CONFIGURAR AQUI ────────────────────────────────────────────────────────
FTP_HOST = "clube3dbrasil.com"          # ou ftp.clube3dbrasil.com
FTP_USER = ""                            # usuario FTP do cPanel (ex: jose3562)
FTP_PASS = ""                            # senha FTP do cPanel
FTP_PATH = "/public_html/wp-content/themes/clube3dbrasil/style.css"
LOCAL_CSS = os.path.join(os.path.dirname(__file__), "style.css")
# ────────────────────────────────────────────────────────────────────────────

def upload():
    if not FTP_USER or not FTP_PASS:
        print("ERRO: Preencha FTP_USER e FTP_PASS no topo do script antes de rodar.")
        return

    if not os.path.exists(LOCAL_CSS):
        print(f"ERRO: Arquivo nao encontrado: {LOCAL_CSS}")
        return

    print(f"Conectando ao FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"Login OK. Enviando style.css...")

        with open(LOCAL_CSS, "rb") as f:
            ftp.storbinary(f"STOR {FTP_PATH}", f)

        ftp.quit()
        print("Upload concluido! Acesse clube3dbrasil.com para verificar.")
    except Exception as e:
        print(f"Erro FTP: {e}")
        print("\nAlternativas:")
        print("  1. Acesse cPanel > File Manager > public_html/wp-content/themes/clube3dbrasil/")
        print("  2. Ou va em wp-admin > Aparencia > Editor de Temas > style.css")

if __name__ == "__main__":
    upload()
