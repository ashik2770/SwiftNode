"""
swiftnode/tools/system.py
========================
System control tools: stats, screenshot, shell command, process manager,
clipboard, and desktop notifications.
"""
import subprocess
import os
import platform
import psutil
import sys

def _get_os() -> str:
    if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
        return "Android"
    return platform.system()

DEVICE_OS = _get_os()


def get_system_stats() -> str:
    """Gets real-time CPU, RAM, Disk, and Battery usage."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:\\')
        battery = psutil.sensors_battery()
        net = psutil.net_io_counters()
        batt_str = f"{battery.percent:.0f}% {'🔌 Charging' if battery.power_plugged else '🔋 Discharging'}" if battery else "N/A"
        
        return (
            f"💻 **System Stats**\n"
            f"├─ 🖥️  CPU: {cpu}%\n"
            f"├─ 🧠 RAM: {ram.percent}% ({ram.used // 1024**2}MB / {ram.total // 1024**2}MB)\n"
            f"├─ 💾 Disk: {disk.percent}% ({disk.used // 1024**3:.1f}GB / {disk.total // 1024**3:.1f}GB)\n"
            f"├─ 🔋 Battery: {batt_str}\n"
            f"├─ 📤 Net Sent: {net.bytes_sent // 1024**2}MB\n"
            f"└─ 📥 Net Recv: {net.bytes_recv // 1024**2}MB"
        )
    except Exception as e:
        return f"❌ Failed to get stats: {str(e)}"


def take_screenshot() -> str:
    """Captures the current screen and saves as 'screenshot.png'."""
    try:
        save_path = os.path.join(os.path.expanduser("~"), ".swiftnode", "screenshots")
        os.makedirs(save_path, exist_ok=True)
        from datetime import datetime
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        full_path = os.path.join(save_path, filename)
        
        if DEVICE_OS == "Android":
            subprocess.run("adb shell screencap -p /sdcard/screenshot.png", shell=True)
            subprocess.run(f"adb pull /sdcard/screenshot.png \"{full_path}\"", shell=True)
            return f"📸 Android screenshot saved: {full_path}"
        else:
            try:
                from PIL import ImageGrab
                snapshot = ImageGrab.grab()
                snapshot.save(full_path)
            except ImportError:
                import pyautogui
                pyautogui.screenshot(full_path)
            return f"📸 Screenshot saved: `{full_path}`"
    except Exception as e:
        return f"❌ Screenshot failed: {str(e)}"


def execute_command(command: str) -> str:
    """Executes a shell/CMD/bash command and returns the output."""
    # Safety block
    BLOCKED = ['rm -rf /', 'format c:', 'del /f /s /q c:\\', 'mkfs', ':(){ :|:& };:']
    if any(b in command.lower() for b in BLOCKED):
        return "🛡️ Command blocked for safety. This command could cause irreversible damage."
    try:
        is_windows = platform.system() == "Windows"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=30, encoding='utf-8', errors='replace'
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if output and error:
            return f"✅ Output:\n{output}\n\n⚠️ Stderr:\n{error}"
        return output or error or "(No output)"
    except subprocess.TimeoutExpired:
        return "⏱️ Command timed out after 30 seconds."
    except Exception as e:
        return f"❌ Command failed: {str(e)}"


def list_processes() -> str:
    """Lists running processes sorted by CPU usage."""
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        top = procs[:20]
        lines = ["🔧 **Top 20 Running Processes** (sorted by CPU):\n"]
        lines.append(f"{'PID':<8} {'Name':<28} {'CPU%':<8} {'MEM%':<8} {'Status'}")
        lines.append("-" * 65)
        for p in top:
            lines.append(
                f"{p['pid']:<8} {(p['name'] or 'N/A')[:27]:<28} "
                f"{p.get('cpu_percent', 0):<8.1f} {p.get('memory_percent', 0):<8.1f} {p.get('status', '')}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Failed to list processes: {str(e)}"


def kill_process(name_or_pid: str) -> str:
    """Kills a process by name or PID."""
    PROTECTED = ['system', 'svchost', 'wininit', 'csrss', 'lsass', 'smss', 'kernel']
    if name_or_pid.lower() in PROTECTED:
        return f"🛡️ Cannot kill '{name_or_pid}' — it's a protected system process."
    try:
        killed = []
        if name_or_pid.isdigit():
            p = psutil.Process(int(name_or_pid))
            p.terminate()
            killed.append(f"PID {name_or_pid} ({p.name()})")
        else:
            for p in psutil.process_iter(['pid', 'name']):
                if p.info.get('name', '').lower() == name_or_pid.lower():
                    p.terminate()
                    killed.append(f"PID {p.pid} ({p.info['name']})")
        return f"✅ Terminated: {', '.join(killed)}" if killed else f"⚠️ No process found: '{name_or_pid}'"
    except Exception as e:
        return f"❌ Kill failed: {str(e)}"


def get_clipboard() -> str:
    """Reads the current clipboard text content."""
    try:
        import pyperclip
        content = pyperclip.paste()
        return f"📋 **Clipboard content:**\n{content}" if content else "📋 Clipboard is empty."
    except ImportError:
        return "⚠️ pyperclip not installed. Run: pip install pyperclip"
    except Exception as e:
        return f"❌ Clipboard read failed: {str(e)}"


def set_clipboard(text: str) -> str:
    """Writes text to the system clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return f"✅ Clipboard updated ({len(text)} characters)."
    except ImportError:
        return "⚠️ pyperclip not installed. Run: pip install pyperclip"
    except Exception as e:
        return f"❌ Clipboard write failed: {str(e)}"


def send_notification(title: str, message: str) -> str:
    """Sends a desktop push notification."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="SwiftNode",
            timeout=10,
        )
        return f"🔔 Notification sent: '{title}'"
    except ImportError:
        return "⚠️ plyer not installed. Run: pip install plyer"
    except Exception as e:
        # Fallback for termux/android
        try:
            subprocess.run(
                ["termux-notification", "--title", title, "--content", message],
                check=True, timeout=5
            )
            return f"🔔 Termux notification sent: '{title}'"
        except Exception:
            return f"❌ Notification failed: {str(e)}"
