"""
swiftnode/multi_device/client.py
================================
HTTP client for connecting to a master SwiftNode device.
Run with: `swiftnode connect <ip:port>`
"""
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


class SwiftNodeClient:
    def __init__(self, host: str, port: int = 7799, token: str = None):
        self.base_url = f"http://{host}:{port}"
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def check_connection(self) -> bool:
        """Checks if the remote server is reachable."""
        try:
            res = requests.get(f"{self.base_url}/health", timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def get_server_info(self) -> dict:
        try:
            res = requests.get(f"{self.base_url}/", timeout=5)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self) -> list:
        try:
            res = requests.get(f"{self.base_url}/tools", headers=self.headers, timeout=10)
            return res.json().get("tools", [])
        except Exception as e:
            return [f"Error: {e}"]

    def query(self, message: str) -> str:
        try:
            res = requests.post(
                f"{self.base_url}/query",
                json={"message": message},
                headers=self.headers,
                timeout=120
            )
            if res.status_code == 200:
                data = res.json()
                return data.get("reply", "No reply.")
            elif res.status_code == 401:
                return "❌ Authentication failed. Check your token."
            else:
                return f"❌ Server error {res.status_code}: {res.text[:200]}"
        except requests.exceptions.ConnectionError:
            return "❌ Connection lost. Check if the server is still running."
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def get_sysinfo(self) -> str:
        try:
            res = requests.get(f"{self.base_url}/sysinfo", headers=self.headers, timeout=10)
            return res.json().get("stats", "No stats available.")
        except Exception as e:
            return f"❌ Error: {str(e)}"


def start_interactive_client(host: str, port: int = 7799, token: str = None):
    """Starts an interactive REPL session connected to a remote SwiftNode device."""
    client = SwiftNodeClient(host, port, token)

    console.clear()
    console.print(Panel(
        f"[bold cyan]SwiftNode Remote Client[/]\n"
        f"[dim]Connecting to: {host}:{port}[/dim]",
        border_style="cyan"
    ))

    if not client.check_connection():
        console.print(f"[bold red]❌ Cannot connect to {host}:{port}[/]")
        console.print("[dim]Make sure the master device is running `swiftnode serve`[/]")
        return

    info = client.get_server_info()
    console.print(Panel(
        f"[bold green]✅ Connected![/]\n"
        f"[dim]Device: {info.get('hostname', 'Unknown')} ({info.get('device_os', 'Unknown')})[/dim]\n"
        f"[dim]Type 'exit' or press Ctrl+C to disconnect.[/dim]\n"
        f"[dim]Commands: :tools | :sys | :help | :exit[/dim]",
        border_style="green"
    ))

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/]").strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit', ':exit', ':quit'):
                console.print("[yellow]👋 Disconnected from remote device.[/]")
                break
            elif user_input == ":tools":
                tools = client.list_tools()
                console.print(f"[dim]Tools ({len(tools)}): {', '.join(tools)}[/dim]")
            elif user_input == ":sys":
                console.print(client.get_sysinfo())
            elif user_input == ":help":
                console.print("[dim]:tools | :sys | :exit — Remote commands[/dim]")
            else:
                with console.status("[bold green]Thinking...[/]"):
                    reply = client.query(user_input)
                console.print(f"[bold green]🤖 SwiftNode[/] ({host}):\n{reply}\n")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Disconnected.[/]")
            break
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/]")
