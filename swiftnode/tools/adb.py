"""
swiftnode/tools/adb.py
=====================
Android ADB tools: shell, tap, swipe, type, install APK, screenshot, screen record.
"""
import subprocess
import os
from pathlib import Path


def _adb(cmd: str, timeout: int = 20) -> str:
    """Helper to run an adb command."""
    try:
        result = subprocess.run(
            f"adb {cmd}", shell=True, capture_output=True, text=True,
            timeout=timeout, encoding='utf-8', errors='replace'
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        return output or error or "(no output)"
    except subprocess.TimeoutExpired:
        return f"⏱️ ADB command timed out."
    except Exception as e:
        return f"❌ ADB error: {str(e)}"


def adb_list_devices() -> str:
    """Lists all ADB-connected Android devices."""
    result = _adb("devices -l")
    return f"📱 **Connected ADB Devices:**\n{result}"


def adb_shell(command: str) -> str:
    """Executes a raw ADB shell command on the connected Android device."""
    BLOCKED = ['rm -rf /system', 'format', 'factory_reset']
    if any(b in command.lower() for b in BLOCKED):
        return "🛡️ Command blocked for safety."
    return _adb(f"shell {command}")


def adb_tap(x: int, y: int) -> str:
    """Taps at the specified screen coordinates on Android."""
    result = _adb(f"shell input tap {x} {y}")
    return f"👆 Tapped at ({x}, {y}). {result}"


def adb_swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> str:
    """Performs a swipe gesture from (x1,y1) to (x2,y2)."""
    result = _adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}")
    return f"👆 Swiped ({x1},{y1}) → ({x2},{y2}). {result}"


def adb_type_text(text: str) -> str:
    """Types text on the Android device (replaces spaces with %s for ADB compatibility)."""
    safe_text = text.replace(' ', '%s').replace("'", "\\'")
    result = _adb(f"shell input text '{safe_text}'")
    return f"⌨️ Typed text on device. {result}"


def adb_install_apk(apk_path: str) -> str:
    """Installs an APK on the connected Android device."""
    p = Path(apk_path).expanduser().resolve()
    if not p.exists():
        return f"❌ APK not found: {apk_path}"
    result = _adb(f"install -r \"{p}\"", timeout=120)
    return f"📦 APK Install Result:\n{result}"


def adb_screenshot() -> str:
    """Captures a screenshot of the connected Android device via ADB."""
    save_path = Path.home() / ".swiftnode" / "screenshots"
    save_path.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    filename = f"android_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    local_path = save_path / filename
    
    _adb("shell screencap -p /sdcard/swiftnode_shot.png")
    result = _adb(f"pull /sdcard/swiftnode_shot.png \"{local_path}\"")
    _adb("shell rm /sdcard/swiftnode_shot.png")
    return f"📸 Android screenshot saved: `{local_path}`\n{result}"


def adb_screen_record(duration_seconds: int = 10) -> str:
    """Records the Android screen for specified duration."""
    save_path = Path.home() / ".swiftnode" / "recordings"
    save_path.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    filename = f"screenrec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    local_path = save_path / filename
    
    _adb(f"shell screenrecord --time-limit {duration_seconds} /sdcard/swiftnode_rec.mp4", 
         timeout=duration_seconds + 10)
    result = _adb(f"pull /sdcard/swiftnode_rec.mp4 \"{local_path}\"")
    _adb("shell rm /sdcard/swiftnode_rec.mp4")
    return f"🎥 Screen recording saved ({duration_seconds}s): `{local_path}`\n{result}"
