"""
Envio de avisos para grupo/canal do Telegram.

Configuracao esperada no .env:
  TELEGRAM_BOT_TOKEN=123456:ABC...
  TELEGRAM_CHAT_ID=-1001234567890
  TELEGRAM_ENABLED=true
  TELEGRAM_NOTIFY_STATUSES=publish
"""

from __future__ import annotations

import html
import logging
import os
import argparse
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


class TelegramConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class TelegramNotifier:
    bot_token: str
    chat_id: str
    timeout: int = 20

    @classmethod
    def from_config(cls, config: dict | None = None) -> "TelegramNotifier | None":
        config = config or {}
        enabled = str(config.get("telegram_enabled", os.getenv("TELEGRAM_ENABLED", "true"))).lower()
        if enabled in {"0", "false", "no", "nao", "não"}:
            return None

        bot_token = config.get("telegram_bot_token") or os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = config.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID", "")
        if not bot_token or not chat_id:
            return None

        timeout = int(config.get("telegram_timeout", os.getenv("TELEGRAM_TIMEOUT", "20")))
        return cls(bot_token=bot_token, chat_id=chat_id, timeout=timeout)

    def send_message(self, text: str, disable_preview: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": disable_preview,
        }
        response = requests.post(url, json=payload, timeout=self.timeout)
        if response.status_code >= 400:
            raise TelegramConfigError(f"Telegram erro {response.status_code}: {response.text[:300]}")
        data = response.json()
        if not data.get("ok"):
            raise TelegramConfigError(f"Telegram rejeitou a mensagem: {data}")
        return data

    def notify_post_published(self, title: str, url: str, excerpt: str = "") -> dict:
        safe_title = html.escape(title.strip() or "Novo post")
        safe_url = html.escape(url.strip())
        clean_excerpt = " ".join((excerpt or "").split())
        safe_excerpt = html.escape(clean_excerpt[:220])

        lines = [
            "<b>Novo post no Clube 3D Brasil</b>",
            "",
            f"<b>{safe_title}</b>",
        ]
        if safe_excerpt:
            lines.extend(["", safe_excerpt])
        if safe_url:
            lines.extend(["", f'<a href="{safe_url}">Abrir post</a>'])

        return self.send_message("\n".join(lines))

    def get_updates(self) -> list[dict]:
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code >= 400:
            raise TelegramConfigError(f"Telegram erro {response.status_code}: {response.text[:300]}")
        data = response.json()
        if not data.get("ok"):
            raise TelegramConfigError(f"Telegram rejeitou getUpdates: {data}")
        return data.get("result", [])


def notify_post_from_config(config: dict, post_result: dict, excerpt: str = "") -> bool:
    notifier = TelegramNotifier.from_config(config)
    if not notifier:
        return False

    notifier.notify_post_published(
        title=post_result.get("titulo", ""),
        url=post_result.get("url", ""),
        excerpt=excerpt,
    )
    return True


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    parser = argparse.ArgumentParser(description="Utilitario Telegram do Clube 3D Brasil.")
    parser.add_argument(
        "command",
        nargs="?",
        default="test",
        choices=("test", "updates"),
        help="test envia mensagem; updates lista chats recentes para descobrir o chat_id.",
    )
    args = parser.parse_args()

    notifier = TelegramNotifier.from_config({})
    if not notifier:
        if args.command == "updates" and os.getenv("TELEGRAM_BOT_TOKEN"):
            notifier = TelegramNotifier(
                bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
                chat_id="0",
                timeout=int(os.getenv("TELEGRAM_TIMEOUT", "20")),
            )
        else:
            raise SystemExit("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env.")

    if args.command == "updates":
        updates = notifier.get_updates()
        if not updates:
            print("Nenhum update encontrado. Adicione o bot no grupo e envie uma mensagem no grupo.")
            return
        for item in updates[-10:]:
            message = item.get("message") or item.get("channel_post") or {}
            chat = message.get("chat", {})
            print(f"chat_id={chat.get('id')} | type={chat.get('type')} | title={chat.get('title') or chat.get('username') or chat.get('first_name')}")
        return

    notifier.send_message("<b>Teste Clube 3D Brasil</b>\n\nConexao com Telegram funcionando.")
    print("Mensagem de teste enviada para o Telegram.")


if __name__ == "__main__":
    main()
