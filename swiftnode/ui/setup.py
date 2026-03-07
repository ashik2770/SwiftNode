"""
swiftnode/ui/setup.py
=====================
Premium 4-Step Animated Config UI Wizard for SwiftNode.
Features: animated ASCII banner, progress bar, step-by-step wizard, 
reconfiguration support, current config display.
"""
import questionary
import json
import os
import time
import secrets
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.table import Table
from rich import print as rprint
from questionary import Style

console = Console()

# ── Styles ────────────────────────────────────────────────────────────────────
QSTYLE = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:green bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:cyan bold'),
    ('separator', 'fg:blue'),
    ('instruction', 'fg:grey italic'),
])

# ── Banner ────────────────────────────────────────────────────────────────────
BANNER_FULL = """\
[bold cyan] ██╗     ██╗████████╗███████╗███╗   ███╗██╗███╗   ██╗██████╗ [/]
[cyan] ██║     ██║╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔══██╗[/]
[bright_blue] ██║     ██║   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║[/]
[blue] ██║     ██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║[/]
[bold blue] ███████╗██║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝[/]
[bold blue] ╚══════╝╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝[/]
[dim cyan]          ⚡  V4 ULTRA  ·  Personal AI Agent  ·  pip install swiftnode  ⚡[/]"""

BANNER_COMPACT = "[bold cyan]⚡ SwiftNode V4 ULTRA[/]\n[dim]Personal AI Agent[/]"


def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def _show_banner(title: str = "System Configuration"):
    _clear()
    width = console.width
    banner = BANNER_FULL if width >= 75 else BANNER_COMPACT
    console.print(Panel(
        Align.center(banner),
        border_style="cyan",
        title=f"[bold green]⚙️  {title}[/]",
        padding=(1, 2)
    ))


def _step_header(step: int, total: int, title: str, icon: str = ""):
    """Renders an animated step header with progress bar."""
    filled = "█" * step
    empty = "░" * (total - step)
    pct = int((step / total) * 100)
    console.print()
    console.print(Rule(f"[bold cyan]{icon} Step {step}/{total}: {title}[/]", style="cyan"))
    console.print(f"  [cyan]{filled}[/][dim]{empty}[/] [bold]{pct}%[/]")
    console.print()


def _show_current_config(config: dict):
    """Displays the current configuration in a pretty table."""
    if not config:
        return
    
    table = Table(title="📋 Current Configuration", border_style="cyan", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value", style="green")
    
    table.add_row("Provider", config.get("provider", "—"))
    table.add_row("Model", config.get("model", "—"))
    table.add_row("API Key", "●●●●●●●●" if config.get("api_key") else "Not Set")
    table.add_row("Bot Platform", config.get("bot_platform", "Telegram"))
    table.add_row("Telegram Token", "●●●●●●●●" if config.get("telegram_token") else "Not Set")
    table.add_row("Discord Token", "●●●●●●●●" if config.get("discord_token") else "Not Set")
    table.add_row("Owner ID", config.get("owner_id", "—"))
    table.add_row("Multi-Device", "✅ Enabled" if config.get("multi_device_enabled") else "❌ Disabled")
    console.print(Align.center(table))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# PROVIDER CONFIGURATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PROVIDERS = [
    questionary.Choice("⚡ Gemini  (Google · Free/Fast · Recommended)", value="Gemini"),
    questionary.Choice("🤖 OpenAI  (GPT-4o · Best Quality)", value="OpenAI"),
    questionary.Choice("⚙️  Grok    (X.AI · xAI Models)", value="Grok"),
    questionary.Choice("🤗 Hugging Face  (Open Models · Free Inference)", value="Hugging Face"),
    questionary.Choice("🌐 OpenRouter  (Claude, Mistral, 100+ Models)", value="OpenRouter"),
    questionary.Choice("🖥️  Ollama  (Local · Privacy First)", value="Ollama"),
    questionary.Choice("⚡ vLLM   (Self-hosted · High Speed)", value="vLLM"),
]


def _configure_provider(config: dict, existing: dict = None) -> dict:
    """Step 1: AI Provider selection."""
    existing = existing or {}
    _step_header(1, 4, "AI Provider", "🧠")
    
    provider = questionary.select(
        "Choose your AI Provider:",
        choices=PROVIDERS,
        style=QSTYLE,
        default=existing.get("provider") if existing else None
    ).ask()
    if not provider:
        raise KeyboardInterrupt()

    config["provider"] = provider
    rprint(f"  [cyan]Selected:[/] [bold green]{provider}[/]\n")

    if provider == "Gemini":
        config["base_url"] = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        config["model"] = questionary.text(
            "Model name:", default=existing.get("model", "gemini-2.5-flash"), style=QSTYLE
        ).ask() or "gemini-2.5-flash"
        config["api_key"] = questionary.password("🔑 Gemini API Key:", style=QSTYLE).ask()

    elif provider == "OpenAI":
        config["base_url"] = "https://api.openai.com/v1/chat/completions"
        config["model"] = questionary.text(
            "Model name:", default=existing.get("model", "gpt-4o"), style=QSTYLE
        ).ask() or "gpt-4o"
        config["api_key"] = questionary.password("🔑 OpenAI API Key:", style=QSTYLE).ask()

    elif provider == "Grok":
        config["base_url"] = "https://api.x.ai/v1/chat/completions"
        config["model"] = questionary.text(
            "Model name:", default=existing.get("model", "grok-2-1212"), style=QSTYLE
        ).ask() or "grok-2-1212"
        config["api_key"] = questionary.password("🔑 xAI (Grok) API Key:", style=QSTYLE).ask()

    elif provider == "Hugging Face":
        config["base_url"] = "https://api-inference.huggingface.co/v1/chat/completions"
        config["model"] = questionary.text(
            "HF Model ID:", default=existing.get("model", "meta-llama/Llama-3.2-3B-Instruct"), style=QSTYLE
        ).ask()
        config["api_key"] = questionary.password("🔑 Hugging Face API Token:", style=QSTYLE).ask()

    elif provider == "OpenRouter":
        config["base_url"] = "https://openrouter.ai/api/v1/chat/completions"
        config["model"] = questionary.text(
            "OpenRouter Model:", default=existing.get("model", "anthropic/claude-3.5-sonnet"), style=QSTYLE
        ).ask()
        config["api_key"] = questionary.password("🔑 OpenRouter API Key:", style=QSTYLE).ask()

    elif provider == "Ollama":
        config["base_url"] = questionary.text(
            "Ollama endpoint:", default=existing.get("base_url", "http://localhost:11434/v1/chat/completions"), style=QSTYLE
        ).ask()
        config["model"] = questionary.text(
            "Local model name:", default=existing.get("model", "llama3"), style=QSTYLE
        ).ask()
        config["api_key"] = "ollama"

    elif provider == "vLLM":
        config["base_url"] = questionary.text(
            "vLLM endpoint:", default=existing.get("base_url", "http://localhost:8000/v1/chat/completions"), style=QSTYLE
        ).ask()
        config["model"] = questionary.text(
            "vLLM model name:", default=existing.get("model", "facebook/opt-125m"), style=QSTYLE
        ).ask()
        config["api_key"] = "vllm"

    return config


def _configure_bot(config: dict, existing: dict = None) -> dict:
    """Step 2: Bot Platform Setup."""
    existing = existing or {}
    _step_header(2, 4, "Bot Platform Integration", "📡")
    
    platforms = [
        questionary.Choice("📱 Telegram (Recommended)", value="Telegram"),
        questionary.Choice("🎮 Discord", value="Discord"),
        questionary.Choice("💬 WhatsApp (QR Code)", value="WhatsApp"),
    ]
    
    platform = questionary.select(
        "Choose your primary Bot Platform:",
        choices=platforms,
        style=QSTYLE,
        default=existing.get("bot_platform", "Telegram") if existing else "Telegram"
    ).ask()
    if not platform:
        raise KeyboardInterrupt()
        
    config["bot_platform"] = platform
    rprint(f"  [cyan]Selected:[/] [bold green]{platform}[/]\n")
    
    if platform == "Telegram":
        rprint("  [dim]Create a bot via [link=https://t.me/BotFather]@BotFather[/link] on Telegram to get your token.[/dim]\n")
        config["telegram_token"] = questionary.password(
            "🤖 Telegram Bot Token:", style=QSTYLE
        ).ask() or (existing.get("telegram_token", "") if existing else "")
        
        rprint("\n  [dim]Get your Telegram User ID by messaging [link=https://t.me/userinfobot]@userinfobot[/link][/dim]\n")
        config["owner_id"] = questionary.text(
            "👤 Your Telegram User ID (numeric):",
            default=existing.get("owner_id", "") if existing else "",
            style=QSTYLE
        ).ask() or ""
        
    elif platform == "Discord":
        rprint("  [dim]Create a bot on the Discord Developer Portal to get your token.[/dim]\n")
        config["discord_token"] = questionary.password(
            "🎮 Discord Bot Token:", style=QSTYLE
        ).ask() or (existing.get("discord_token", "") if existing else "")
        config["owner_id"] = "" # Could add Discord Owner ID if needed later
        
    elif platform == "WhatsApp":
        rprint("  [dim]WhatsApp bot will use Selenium to open WhatsApp Web.[/dim]")
        rprint("  [dim]You will need to scan the QR code with your phone on startup.[/dim]\n")
        config["owner_id"] = "" # Can be filled automatically matching number later

    return config


def _configure_features(config: dict, existing: dict = None) -> dict:
    """Step 3: Memory and Features configuration."""
    existing = existing or {}
    _step_header(3, 4, "Memory & Features", "🧠")

    rprint("  [dim]SwiftNode uses Google Embeddings for semantic memory search.[/dim]")
    rprint("  [dim]If you're using Ollama/vLLM, you can add a Gemini key here, or skip (uses keyword search).[/dim]\n")
    
    use_gemini_memory = questionary.confirm(
        "Use Gemini Embeddings for long-term memory? (requires Gemini API key)",
        default=bool(config.get("api_key") and config.get("provider") == "Gemini"),
        style=QSTYLE
    ).ask()
    
    if use_gemini_memory and config.get("api_key", "") in ("ollama", "vllm", ""):
        memory_key = questionary.password("🔑 Gemini API Key for memory:", style=QSTYLE).ask()
        config["memory_api_key"] = memory_key
    else:
        config["memory_api_key"] = config.get("api_key", "")
    
    return config


def _configure_multidevice(config: dict, existing: dict = None) -> dict:
    """Step 4: Multi-Device Setup."""
    existing = existing or {}
    _step_header(4, 4, "Multi-Device Control (Optional)", "🌐")
    
    rprint("  [dim]Enable to control this device from other devices on your network.[/dim]")
    rprint("  [dim]Use [bold]swiftnode serve[/bold] on the master device.[/dim]\n")
    
    enable_md = questionary.confirm(
        "Enable Multi-Device mode?",
        default=existing.get("multi_device_enabled", False) if existing else False,
        style=QSTYLE
    ).ask()
    
    config["multi_device_enabled"] = enable_md
    
    if enable_md:
        default_token = existing.get("multi_device_token") if existing else secrets.token_urlsafe(16)
        token = questionary.text(
            "🔐 Secret access token (or press Enter for auto-generated):",
            default=default_token,
            style=QSTYLE
        ).ask()
        config["multi_device_token"] = token or default_token
        config["multi_device_port"] = int(questionary.text(
            "Port for server:", default=str(existing.get("multi_device_port", 7799) if existing else 7799), style=QSTYLE
        ).ask() or "7799")
        
        rprint(f"\n  [bold green]✅ Multi-Device enabled![/]")
        rprint(f"  [dim]Master command:[/] [cyan]swiftnode serve[/]")
        rprint(f"  [dim]Client command:[/] [cyan]swiftnode connect <master-ip>:{config['multi_device_port']}[/]")
        rprint(f"  [dim]Token: [bold]{config['multi_device_token']}[/][/dim]\n")
    
    config["connected_devices"] = existing.get("connected_devices", []) if existing else []
    return config


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SETUP FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def run_setup(existing_config: dict = None) -> dict:
    """
    Runs the full interactive setup wizard.
    existing_config: if provided, uses it as defaults for reconfiguration.
    """
    from swiftnode.config import save_config
    
    config = {}
    
    try:
        _show_banner("System Configuration Wizard")

        if existing_config:
            rprint()
            _show_current_config(existing_config)
            proceed = questionary.confirm(
                "⚙️  Existing config found. Reconfigure?",
                default=True, style=QSTYLE
            ).ask()
            if not proceed:
                rprint("[green]✅ Keeping existing configuration.[/]")
                return existing_config

        # ── Run 4 steps ───────────────────────────────────────────────────────
        _show_banner("Step 1/4 — AI Provider")
        config = _configure_provider(config, existing_config)

        _show_banner("Step 2/4 — Bot Platform Integration")
        config = _configure_bot(config, existing_config)

        _show_banner("Step 3/4 — Memory & Features")
        config = _configure_features(config, existing_config)

        _show_banner("Step 4/4 — Multi-Device Control")
        config = _configure_multidevice(config, existing_config)

        # ── Save ──────────────────────────────────────────────────────────────
        _show_banner("Saving Configuration")
        with console.status("[bold green]💾 Saving configuration to ~/.swiftnode/config.json...", spinner="dots2"):
            time.sleep(1.2)
            save_config(config)

        # ── Summary ───────────────────────────────────────────────────────────
        _clear()
        console.print()
        console.print(Panel(
            Align.center(
                "[bold green]✅ SwiftNode V4 is Ready![/bold green]\n\n"
                f"[dim]Provider: [bold]{config.get('provider')}[/bold]  |  Model: [bold]{config.get('model')}[/bold][/dim]\n"
                f"[dim]Bot Platform: [bold]{config.get('bot_platform', 'Telegram')}[/bold]  |  Multi-Device: [bold]{'✅' if config.get('multi_device_enabled') else '❌'}[/bold][/dim]\n\n"
                "[bold cyan]Quick Start:[/bold cyan]\n"
                "  [green]swiftnode run[/green]    → Start the configured bot\n"
                "  [green]swiftnode serve[/green]  → Start multi-device server\n"
                "  [green]swiftnode config[/green] → Reconfigure\n"
            ),
            border_style="green",
            title="[bold cyan]⚡ Setup Complete[/]",
            padding=(1, 4)
        ))
        console.print()
        return config

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Setup cancelled.[/]")
        return existing_config or {}


if __name__ == "__main__":
    run_setup()
