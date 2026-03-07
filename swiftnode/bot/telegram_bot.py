"""
swiftnode/bot/telegram_bot.py
=============================
Telegram bot interface for SwiftNode.
Handles commands, file sending, and streaming typing indicators.
"""
import os
import telebot
from rich.console import Console
from rich.panel import Panel
from swiftnode.config import load_config
from swiftnode.core.agent import SwiftNodeCore

console = Console()


def run_bot():
    """Initializes and starts the SwiftNode Telegram bot."""
    config = load_config()
    if not config:
        console.print("[bold red]❌ No config found. Run `swiftnode config` first.[/]")
        return

    try:
        agent = SwiftNodeCore(config)
        bot = telebot.TeleBot(config["telegram_token"])
        owner_id = str(config.get("owner_id", ""))
    except Exception as e:
        console.print(f"[bold red]❌ Initialization Error:[/] {e}")
        return

    console.clear()
    console.print(Panel(
        "[bold cyan]SwiftNode V4 is ONLINE[/bold cyan]\n"
        f"[dim]Provider: {config.get('provider', 'Unknown')} | Model: {config.get('model', 'Unknown')}[/dim]\n"
        f"[dim]Tools: {len(agent.available_tools)} active[/dim]\n"
        "[dim]Press Ctrl+C to shutdown.[/dim]",
        border_style="cyan",
        title="[bold green]⚡ SwiftNode V4 ULTRA[/]"
    ))

    def is_owner(message) -> bool:
        if owner_id and str(message.chat.id) != owner_id:
            console.print(f"[bold red]⛔ Unauthorized: {message.chat.id}[/]")
            bot.reply_to(message, "⛔ Access Denied. Unauthorized.")
            return False
        return True

    @bot.message_handler(commands=['start', 'help'])
    def start_cmd(message):
        if not is_owner(message): return
        tools = list(agent.available_tools.keys())
        help_text = (
            "⚡ **SwiftNode V4 ULTRA** — Personal AI Agent\n\n"
            "**Commands:**\n"
            "• `/start` / `/help` — This menu\n"
            "• `/clear` — Clear conversation memory\n"
            "• `/sys` — System stats report\n"
            "• `/tools` — List all active tools\n"
            "• `/devices` — Show connected devices\n"
            "• `/config` — Show current config\n\n"
            "**Capabilities:**\n"
            "• 🌐 Web Research, Wikipedia, News, YouTube\n"
            "• 📁 File Management (read/write/delete/zip)\n"
            "• 📊 System Monitor, Process Manager\n"
            "• 📋 Clipboard Control, Notifications\n"
            "• 📸 Screenshot (PC & Android)\n"
            "• 🤖 Android ADB Automation\n"
            "• 🌍 Network Scanner, Speed Test\n"
            "• 🐍 Python Code Runner & Linter\n"
            "• 🧠 Long-Term RAG Memory"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")

    @bot.message_handler(commands=['sys'])
    def sys_cmd(message):
        if not is_owner(message): return
        from swiftnode.tools.system import get_system_stats
        bot.reply_to(message, get_system_stats(), parse_mode="Markdown")

    @bot.message_handler(commands=['tools'])
    def tools_cmd(message):
        if not is_owner(message): return
        tools = list(agent.available_tools.keys())
        text = "🔧 **Active Tools ({}):**\n".format(len(tools))
        text += "\n".join(f"  • `{t}`" for t in sorted(tools))
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=['devices'])
    def devices_cmd(message):
        if not is_owner(message): return
        devices = config.get("connected_devices", [])
        if devices:
            text = "📡 **Connected Devices:**\n" + "\n".join(f"  • {d}" for d in devices)
        else:
            text = "📡 No remote devices connected.\nUse `swiftnode serve` on master device and `swiftnode connect <ip>` on this device."
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=['config'])
    def config_cmd(message):
        if not is_owner(message): return
        text = (
            f"⚙️ **Current Config:**\n"
            f"• Provider: `{config.get('provider')}`\n"
            f"• Model: `{config.get('model')}`\n"
            f"• Multi-Device: `{config.get('multi_device_enabled', False)}`\n"
            f"• Memory DB: `~/.swiftnode/memory.sqlite`"
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=['clear'])
    def clear_cmd(message):
        if not is_owner(message): return
        agent.memory.clear_history()
        bot.reply_to(message, "🧹 Conversation memory cleared. Long-term vector memory intact.")

    @bot.message_handler(content_types=['document', 'photo'])
    def file_handler(message):
        """Handles file/image uploads from Telegram."""
        if not is_owner(message): return
        try:
            if message.content_type == 'document':
                file_info = bot.get_file(message.document.file_id)
                fname = message.document.file_name
            else:
                file_info = bot.get_file(message.photo[-1].file_id)
                fname = f"photo_{message.photo[-1].file_id}.jpg"

            dl_path = bot.download_file(file_info.file_path)
            import tempfile, os
            from pathlib import Path
            save_dir = Path.home() / ".swiftnode" / "uploads"
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / fname
            save_path.write_bytes(dl_path)

            caption = message.caption or f"Analyze this file: {fname}"
            query = f"{caption}\n[File saved at: {save_path}]"
            
            bot.send_chat_action(message.chat.id, 'typing')
            reply = agent.process_query(query)
            _safe_reply(bot, message, reply)
        except Exception as e:
            bot.reply_to(message, f"⚠️ File handling error: {str(e)}")

    @bot.message_handler(func=lambda m: True)
    def chat_handler(message):
        if not is_owner(message): return
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            console.print(f"[bold blue]👤 User:[/] {message.text}")

            reply = agent.process_query(message.text)
            _safe_reply(bot, message, reply)
            console.print(f"[bold green]🤖 Agent:[/] {reply[:200]}{'...' if len(reply) > 200 else ''}\n")
        except Exception as e:
            error_msg = f"⚠️ System error: {str(e)}"
            bot.reply_to(message, error_msg)
            console.print(f"[bold red]{error_msg}[/]")

    def _safe_reply(bot, message, text):
        """Send reply, splitting into chunks if > 4096 chars."""
        MAX_LEN = 4096
        if len(text) <= MAX_LEN:
            try:
                bot.reply_to(message, text, parse_mode="Markdown")
            except Exception:
                bot.reply_to(message, text)
        else:
            chunks = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
            for chunk in chunks:
                try:
                    bot.send_message(message.chat.id, chunk, parse_mode="Markdown")
                except Exception:
                    bot.send_message(message.chat.id, chunk)

    console.print(f"[bold green]🚀 Bot polling started...[/]")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
