"""
swiftnode/cli.py
================
Main CLI entry point for SwiftNode.
Commands:
  swiftnode run              → Start Telegram bot
  swiftnode config           → Run/re-run setup wizard
  swiftnode serve            → Start multi-device HTTP server  
  swiftnode connect <ip>     → Connect to a remote SwiftNode device
  swiftnode tools            → List available tools
  swiftnode version          → Show version info
"""
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

console = Console()

ASCII_LOGO = """\
[bold cyan] ██╗     ██╗████████╗███████╗███╗   ███╗██╗███╗   ██╗██████╗[/]
[cyan] ██║     ██║╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔══██╗[/]
[bright_blue] ██║     ██║   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║[/]
[blue] ██║     ██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║[/]
[bold blue] ███████╗██║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝[/]
[bold blue] ╚══════╝╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝[/]"""


def _show_welcome():
    console.clear()
    console.print(Panel(
        Align.center(
            ASCII_LOGO + "\n\n"
            "[dim cyan]V5 ULTRA  ·  Personal AI Agent  ·  100+ LLM Providers  ·  30+ Tools[/dim cyan]"
        ),
        border_style="cyan",
        padding=(1, 2)
    ))


def cmd_run(args):
    """Start the specified bot."""
    from swiftnode.config import config_exists, load_config
    from swiftnode.ui.setup import run_setup
    
    if not config_exists():
        console.print("[yellow]⚠️  No config found. Running setup wizard...[/]")
        run_setup()
        
    config = load_config()
    
    bot_choice = args.bot or config.get("bot_platform", "Telegram")
    bot_choice = bot_choice.lower()
    
    # Beautiful start banner
    console.print(Panel(f"[bold green]🚀 Starting {bot_choice.title()} Bot...[/]", border_style="green"))
    
    if bot_choice == "telegram":
        from swiftnode.bot.telegram_bot import run_bot
        run_bot()
    elif bot_choice == "discord":
        try:
            from swiftnode.bot.discord_bot import run_discord_bot
            run_discord_bot()
        except ImportError:
            console.print("[bold red]❌ Discord bot module not found. Did you run pip install -e .?[/]")
            sys.exit(1)
    elif bot_choice == "whatsapp":
        try:
            from swiftnode.bot.whatsapp_bot import run_whatsapp_bot
            run_whatsapp_bot()
        except ImportError:
            console.print("[bold red]❌ WhatsApp bot module not found. Did you run pip install -e .?[/]")
            sys.exit(1)
    else:
        console.print(f"[bold red]❌ Unknown bot platform: {bot_choice}[/]")
        sys.exit(1)


def cmd_config(args):
    """Run the interactive setup/reconfiguration wizard."""
    from swiftnode.config import load_config
    from swiftnode.ui.setup import run_setup
    
    existing = load_config()
    run_setup(existing_config=existing if existing else None)


def cmd_serve(args):
    """Start the multi-device HTTP API server."""
    from swiftnode.config import load_config
    from swiftnode.multi_device.server import start_server
    
    config = load_config()
    if not config:
        console.print("[bold red]❌ No config found. Run `swiftnode config` first.[/]")
        sys.exit(1)
    
    token = config.get("multi_device_token") or args.token
    port = args.port or config.get("multi_device_port", 7799)
    
    if not config.get("multi_device_enabled") and not args.force:
        console.print("[yellow]⚠️  Multi-device not enabled in config.[/]")
        console.print("[dim]Use `swiftnode config` to enable it, or add --force to run anyway.[/]")
        sys.exit(1)
    
    start_server(host="0.0.0.0", port=port, token=token)


def cmd_connect(args):
    """Connect to a remote SwiftNode device."""
    from swiftnode.config import load_config
    from swiftnode.multi_device.client import start_interactive_client
    
    target = args.target
    if not target:
        console.print("[bold red]❌ Usage: swiftnode connect <ip:port>[/]")
        sys.exit(1)
    
    # Parse host:port
    if ":" in target:
        host, port_str = target.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            console.print("[red]❌ Invalid port.[/]")
            sys.exit(1)
    else:
        host = target
        port = 7799
    
    token = args.token
    start_interactive_client(host=host, port=port, token=token)


def cmd_tools(args):
    """List all available tools on this device."""
    from swiftnode.tools import AVAILABLE_TOOLS, DEVICE_OS
    
    table = Table(
        title=f"🔧 SwiftNode Tools — {DEVICE_OS}",
        border_style="cyan",
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Tool Name", style="bold green")
    table.add_column("Category")
    
    category_map = {
        "search_internet": "🌐 Web", "fetch_webpage": "🌐 Web",
        "get_wikipedia_summary": "🌐 Web", "get_top_news": "🌐 Web", "get_youtube_transcript": "🌐 Web",
        "get_system_stats": "💻 System", "take_screenshot": "💻 System",
        "execute_command": "💻 System", "list_processes": "💻 System",
        "kill_process": "💻 System", "get_clipboard": "💻 System",
        "set_clipboard": "💻 System", "send_notification": "💻 System",
        "list_files": "📁 Files", "read_file": "📁 Files", "write_file": "📁 Files",
        "delete_file": "📁 Files", "zip_folder": "📁 Files",
        "get_public_ip": "🌍 Network", "ping_host": "🌍 Network",
        "scan_lan_devices": "🌍 Network", "run_speed_test": "🌍 Network",
        "run_python_snippet": "🐍 Code", "lint_code": "🐍 Code",
        "save_to_long_term_memory": "🧠 Memory",
        "adb_shell": "📱 ADB", "adb_tap": "📱 ADB", "adb_swipe": "📱 ADB",
        "adb_type_text": "📱 ADB", "adb_install_apk": "📱 ADB",
        "adb_screenshot": "📱 ADB", "adb_list_devices": "📱 ADB", "adb_screen_record": "📱 ADB",
        # V5 Extras
        "math_calc": "🔢 Extras", "base64_encode": "🔢 Extras", "base64_decode": "🔢 Extras",
        "hash_text": "🔢 Extras", "get_weather": "🌤 Extras", "translate_text": "🌐 Extras",
    }
    
    for i, name in enumerate(sorted(AVAILABLE_TOOLS.keys()), 1):
        cat = category_map.get(name, "🔧 Tool")
        table.add_row(str(i), name, cat)
    
    console.print()
    console.print(table)
    console.print(f"\n[dim]Total: {len(AVAILABLE_TOOLS)} tools active on {DEVICE_OS}[/]\n")


def cmd_version(args):
    """Show version information."""
    from swiftnode import __version__
    from swiftnode.tools import DEVICE_OS
    import platform
    
    _show_welcome()
    console.print(Panel(
        f"[bold]Version:[/]  [green]{__version__}[/]\n"
        f"[bold]Device:[/]   [cyan]{DEVICE_OS}[/]\n"
        f"[bold]Python:[/]   [dim]{platform.python_version()}[/]\n"
        f"[bold]GitHub:[/]   [link=https://github.com/ashik2770/SwiftNode]github.com/ashik2770/SwiftNode[/link]",
        border_style="cyan",
        title="[bold cyan]ℹ️  SwiftNode Info[/]"
    ))


def cmd_chat(args):
    """Start an interactive terminal chat session (no Telegram required)."""
    from swiftnode.config import config_exists, load_config
    from swiftnode.ui.setup import run_setup
    from swiftnode.core.agent import SwiftNodeCore
    import readline  # noqa: F401 — enables arrow-key history on Linux/macOS

    if not config_exists():
        console.print("[yellow]⚠️  No config found. Running setup wizard...[/]")
        run_setup()

    config = load_config()
    try:
        agent = SwiftNodeCore(config)
    except Exception as e:
        console.print(f"[bold red]❌ Agent init failed: {e}[/]")
        sys.exit(1)

    from swiftnode.tools import DEVICE_OS
    console.print(Panel(
        f"[bold green]SwiftNode V5 Terminal Chat[/bold green]\n"
        f"[dim]Provider: {config.get('provider')} | Model: {config.get('model')}[/dim]\n"
        f"[dim]Tools: {len(agent.available_tools)} active on {DEVICE_OS}[/dim]\n"
        "[dim]Type [bold]/clear[/bold] to reset memory, [bold]/exit[/bold] or Ctrl+C to quit.[/dim]",
        border_style="green",
        title="[bold cyan]💬 Chat Mode[/]"
    ))

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/exit", "exit", "quit"):
            console.print("[dim]Session ended. Goodbye! 👋[/dim]")
            break
        if user_input.lower() == "/clear":
            agent.memory.clear_history()
            console.print("[yellow]🧹 Memory cleared.[/yellow]")
            continue

        try:
            console.print("[dim]🤔 Thinking...[/dim]")
            reply = agent.process_query(user_input)
            console.print(f"[bold green]🤖 SwiftNode:[/bold green] {reply}\n")
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Interrupted.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]\n")


def cmd_update(args):
    """Self-update SwiftNode via pip."""
    import subprocess
    console.print(Panel(
        "[bold cyan]🔄 Updating SwiftNode to latest version...[/bold cyan]\n"
        "[dim]Running: pip install --upgrade swiftnode[/dim]",
        border_style="cyan"
    ))
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "swiftnode"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print("[bold green]✅ SwiftNode updated successfully![/bold green]")
            # Show new version
            out_lines = result.stdout.strip().splitlines()
            for line in out_lines[-5:]:
                console.print(f"[dim]{line}[/dim]")
        else:
            console.print(f"[bold red]❌ Update failed:[/bold red]\n{result.stderr[:500]}")
    except Exception as e:
        console.print(f"[bold red]❌ Update error: {e}[/bold red]")


def main():
    parser = argparse.ArgumentParser(
        prog="swiftnode",
        description="⚡ SwiftNode V5 ULTRA — Personal AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  swiftnode config               # First-time setup or reconfigure\n"
            "  swiftnode run                  # Start the bot (Telegram/Discord/WhatsApp)\n"
            "  swiftnode chat                 # Interactive terminal chat (no Telegram)\n"
            "  swiftnode serve                # Start multi-device server\n"
            "  swiftnode connect 192.168.1.5  # Connect to master device\n"
            "  swiftnode tools                # List all available tools\n"
            "  swiftnode update               # Update SwiftNode to latest version\n"
        )
    )
    
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = False

    # run
    sp_run = subparsers.add_parser("run", help="🚀 Start the SwiftNode bot")
    sp_run.add_argument("--bot", type=str, choices=["telegram", "discord", "whatsapp"], help="Override config platform to run specific bot")
    sp_run.set_defaults(func=cmd_run)

    # config
    sp_cfg = subparsers.add_parser("config", help="⚙️  Run the setup/reconfiguration wizard")
    sp_cfg.set_defaults(func=cmd_config)

    # serve
    sp_srv = subparsers.add_parser("serve", help="🌐 Start the multi-device HTTP API server")
    sp_srv.add_argument("--port", type=int, default=None, help="Port (default: 7799)")
    sp_srv.add_argument("--token", type=str, default=None, help="Auth token")
    sp_srv.add_argument("--force", action="store_true", help="Force start even if not configured")
    sp_srv.set_defaults(func=cmd_serve)

    # connect
    sp_con = subparsers.add_parser("connect", help="📡 Connect to a remote SwiftNode device")
    sp_con.add_argument("target", nargs="?", help="Remote device IP or IP:port (e.g. 192.168.1.5:7799)")
    sp_con.add_argument("--token", type=str, default=None, help="Auth token")
    sp_con.set_defaults(func=cmd_connect)

    # tools
    sp_tools = subparsers.add_parser("tools", help="🔧 List all available tools")
    sp_tools.set_defaults(func=cmd_tools)

    # chat
    sp_chat = subparsers.add_parser("chat", help="💬 Interactive terminal chat (no Telegram needed)")
    sp_chat.set_defaults(func=cmd_chat)

    # update
    sp_update = subparsers.add_parser("update", help="🔄 Update SwiftNode to the latest version")
    sp_update.set_defaults(func=cmd_update)

    # version
    sp_ver = subparsers.add_parser("version", help="ℹ️  Show version information")
    sp_ver.add_argument("-v", "--version", action="store_true")
    sp_ver.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if args.command is None:
        # Default: show welcome and help
        _show_welcome()
        console.print()
        parser.print_help()
        console.print()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
