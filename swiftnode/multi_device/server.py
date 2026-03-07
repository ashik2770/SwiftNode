"""
swiftnode/multi_device/server.py
================================
FastAPI HTTP API server for multi-device control.
Run with: `swiftnode serve`
Other devices can POST to /query to use this device's AI agent.
"""
import secrets
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from swiftnode.config import load_config
from swiftnode.core.agent import SwiftNodeCore
from swiftnode.tools import AVAILABLE_TOOLS, DEVICE_OS
import platform
from datetime import datetime

app = FastAPI(
    title="SwiftNode Multi-Device API",
    description="Control this SwiftNode device remotely from any device on your network.",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)
_agent: SwiftNodeCore = None
_secret_token: str = None


def get_agent() -> SwiftNodeCore:
    global _agent
    if _agent is None:
        config = load_config()
        _agent = SwiftNodeCore(config)
    return _agent


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    global _secret_token
    if _secret_token and (credentials is None or credentials.credentials != _secret_token):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token.")
    return True


class QueryRequest(BaseModel):
    message: str
    session_id: str = "default"


class QueryResponse(BaseModel):
    reply: str
    device: str
    model: str
    timestamp: str


@app.get("/")
def root():
    return {
        "service": "SwiftNode Multi-Device Bridge",
        "version": "4.0.0",
        "device_os": DEVICE_OS,
        "hostname": platform.node(),
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/tools")
def list_tools(auth: bool = Depends(verify_token)):
    """Lists all available tools on this device."""
    tools = list(AVAILABLE_TOOLS.keys())
    return {
        "device_os": DEVICE_OS,
        "tool_count": len(tools),
        "tools": sorted(tools)
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, auth: bool = Depends(verify_token)):
    """Send a query to this device's SwiftNode agent."""
    agent = get_agent()
    config = load_config()
    try:
        reply = agent.process_query(request.message)
        return QueryResponse(
            reply=reply,
            device=f"{platform.node()} ({DEVICE_OS})",
            model=config.get("model", "unknown"),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sysinfo")
def sysinfo(auth: bool = Depends(verify_token)):
    """Returns system stats of this device."""
    from swiftnode.tools.system import get_system_stats
    return {"stats": get_system_stats(), "device": platform.node(), "os": DEVICE_OS}


def start_server(host: str = "0.0.0.0", port: int = 7799, token: str = None):
    """Starts the FastAPI uvicorn server."""
    import uvicorn
    global _secret_token
    _secret_token = token
    
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    console.print(Panel(
        f"[bold cyan]SwiftNode Multi-Device Server[/]\n"
        f"[dim]Listening on http://{host}:{port}[/dim]\n"
        f"[dim]API Docs: http://localhost:{port}/docs[/dim]\n"
        f"[dim]Token: {'🔒 Enabled' if token else '⚠️  No auth (not recommended)'}[/dim]",
        border_style="cyan",
        title="[bold green]🌐 Multi-Device Bridge[/]"
    ))
    uvicorn.run(app, host=host, port=port, log_level="warning")
