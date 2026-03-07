"""
SwiftNode Tools Registry
========================
Dynamically builds AVAILABLE_TOOLS and AI_TOOL_SCHEMA based on the device OS.
"""
import os
import platform

def get_device_os() -> str:
    """Detects if the environment is Android (Termux) or PC (Windows/Linux/Mac)"""
    if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
        return "Android"
    return platform.system()

DEVICE_OS = get_device_os()

# ── Import all tool modules ───────────────────────────────────────────────────
from swiftnode.tools.web import (
    search_internet, fetch_webpage, get_wikipedia_summary, get_top_news, get_youtube_transcript
)
from swiftnode.tools.system import (
    get_system_stats, take_screenshot, execute_command,
    list_processes, kill_process, get_clipboard, set_clipboard, send_notification
)
from swiftnode.tools.files import (
    list_files, read_file, write_file, delete_file, zip_folder
)
from swiftnode.tools.network import (
    get_public_ip, ping_host, scan_lan_devices, run_speed_test
)
from swiftnode.tools.code import run_python_snippet, lint_code

# ── Base tools available on ALL devices ──────────────────────────────────────
AVAILABLE_TOOLS: dict = {
    "search_internet": search_internet,
    "fetch_webpage": fetch_webpage,
    "get_wikipedia_summary": get_wikipedia_summary,
    "get_top_news": get_top_news,
    "get_youtube_transcript": get_youtube_transcript,
    "get_system_stats": get_system_stats,
    "take_screenshot": take_screenshot,
    "list_processes": list_processes,
    "kill_process": kill_process,
    "get_clipboard": get_clipboard,
    "set_clipboard": set_clipboard,
    "send_notification": send_notification,
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "zip_folder": zip_folder,
    "get_public_ip": get_public_ip,
    "ping_host": ping_host,
    "scan_lan_devices": scan_lan_devices,
    "run_speed_test": run_speed_test,
    "run_python_snippet": run_python_snippet,
    "lint_code": lint_code,
}

AI_TOOL_SCHEMA: list = [
    {
        "type": "function", "function": {
            "name": "search_internet",
            "description": "Search the web with DuckDuckGo for real-time information.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "fetch_webpage",
            "description": "Extract and read the main text content from any URL.",
            "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "Full URL to fetch"}}, "required": ["url"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_wikipedia_summary",
            "description": "Get a concise Wikipedia summary for any topic.",
            "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_top_news",
            "description": "Get top news headlines. Category options: technology, world, sports, science, business.",
            "parameters": {"type": "object", "properties": {"category": {"type": "string", "description": "News category", "default": "technology"}}, "required": []}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_youtube_transcript",
            "description": "Get the transcript/subtitles from a YouTube video URL.",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_system_stats",
            "description": "Get real-time CPU, RAM, Disk, and Battery usage stats.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "take_screenshot",
            "description": "Capture the current screen of PC or Android device.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "list_processes",
            "description": "List all currently running system processes with CPU and memory usage.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "kill_process",
            "description": "Kill a running process by its name or PID.",
            "parameters": {"type": "object", "properties": {"name_or_pid": {"type": "string", "description": "Process name (e.g., 'chrome.exe') or PID (e.g., '1234')"}}, "required": ["name_or_pid"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_clipboard",
            "description": "Read the current text content from the system clipboard.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "set_clipboard",
            "description": "Write text to the system clipboard.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "send_notification",
            "description": "Send a desktop/system notification popup.",
            "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}}, "required": ["title", "message"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "list_files",
            "description": "List all files and folders in a directory.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path (default: current directory)", "default": "."}}, "required": []}
        }
    },
    {
        "type": "function", "function": {
            "name": "read_file",
            "description": "Read the content of a file from the filesystem.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "write_file",
            "description": "Write or create a file with the given content.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}}, "required": ["filepath", "content"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "delete_file",
            "description": "Delete a file from the filesystem. Use with caution.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "zip_folder",
            "description": "Compress/zip a folder or file into a .zip archive.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "output_name": {"type": "string", "description": "Output zip filename (optional)"}}, "required": ["path"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "get_public_ip",
            "description": "Get the current public/external IP address of this device.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "ping_host",
            "description": "Ping a host to check connectivity and measure latency.",
            "parameters": {"type": "object", "properties": {"host": {"type": "string", "description": "Hostname or IP address"}}, "required": ["host"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "scan_lan_devices",
            "description": "Scan the local network to discover connected devices.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "run_speed_test",
            "description": "Run an internet speed test and report download/upload speeds.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", "function": {
            "name": "run_python_snippet",
            "description": "Safely execute a Python code snippet and return the output.",
            "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "Python code to execute"}}, "required": ["code"]}
        }
    },
    {
        "type": "function", "function": {
            "name": "lint_code",
            "description": "Check Python code for syntax errors and basic issues.",
            "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}
        }
    },
]

# ── Device-specific tools ─────────────────────────────────────────────────────
if DEVICE_OS == "Android":
    from swiftnode.tools.adb import (
        adb_shell, adb_tap, adb_swipe, adb_type_text,
        adb_install_apk, adb_screenshot, adb_list_devices, adb_screen_record
    )
    AVAILABLE_TOOLS.update({
        "adb_shell": adb_shell,
        "adb_tap": adb_tap,
        "adb_swipe": adb_swipe,
        "adb_type_text": adb_type_text,
        "adb_install_apk": adb_install_apk,
        "adb_screenshot": adb_screenshot,
        "adb_list_devices": adb_list_devices,
        "adb_screen_record": adb_screen_record,
    })
    AI_TOOL_SCHEMA.extend([
        {"type": "function", "function": {"name": "adb_shell", "description": "Execute an ADB shell command on connected Android device.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
        {"type": "function", "function": {"name": "adb_tap", "description": "Tap at specific screen coordinates on Android.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
        {"type": "function", "function": {"name": "adb_swipe", "description": "Swipe gesture on Android screen.", "parameters": {"type": "object", "properties": {"x1": {"type": "integer"}, "y1": {"type": "integer"}, "x2": {"type": "integer"}, "y2": {"type": "integer"}, "duration_ms": {"type": "integer", "default": 300}}, "required": ["x1", "y1", "x2", "y2"]}}},
        {"type": "function", "function": {"name": "adb_type_text", "description": "Type text on the Android device.", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
        {"type": "function", "function": {"name": "adb_install_apk", "description": "Install an APK file on Android device.", "parameters": {"type": "object", "properties": {"apk_path": {"type": "string"}}, "required": ["apk_path"]}}},
        {"type": "function", "function": {"name": "adb_screenshot", "description": "Capture screenshot of connected Android device via ADB.", "parameters": {"type": "object", "properties": {}}}},
        {"type": "function", "function": {"name": "adb_list_devices", "description": "List all ADB-connected Android devices.", "parameters": {"type": "object", "properties": {}}}},
        {"type": "function", "function": {"name": "adb_screen_record", "description": "Record Android screen for a specified duration.", "parameters": {"type": "object", "properties": {"duration_seconds": {"type": "integer", "default": 10}}, "required": []}}},
    ])
else:
    # PC-only: execute_command is already in system.py, no duplication needed
    pass
