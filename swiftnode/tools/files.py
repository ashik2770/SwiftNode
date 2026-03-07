"""
swiftnode/tools/files.py
=======================
File management tools: list, read, write, delete, zip.
"""
import os
import shutil
import zipfile
from pathlib import Path


def list_files(path: str = ".") -> str:
    """Lists files and directories in the specified path."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"❌ Path does not exist: {path}"
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        lines = [f"📁 **Directory: {p}**\n"]
        for item in items[:100]:
            if item.is_dir():
                lines.append(f"  📂 {item.name}/")
            else:
                size = item.stat().st_size
                size_str = f"{size:,}B" if size < 1024 else (f"{size//1024}KB" if size < 1024**2 else f"{size//1024**2}MB")
                lines.append(f"  📄 {item.name} ({size_str})")
        
        if len(list(p.iterdir())) > 100:
            lines.append("\n  ... (showing first 100 items)")
        return "\n".join(lines)
    except PermissionError:
        return f"❌ Permission denied: {path}"
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"


def read_file(filepath: str) -> str:
    """Reads and returns the content of a text file."""
    try:
        p = Path(filepath).expanduser().resolve()
        if not p.exists():
            return f"❌ File not found: {filepath}"
        if p.stat().st_size > 1024 * 1024:  # 1MB limit
            return f"⚠️ File too large ({p.stat().st_size // 1024}KB). Please specify a smaller file."
        content = p.read_text(encoding='utf-8', errors='replace')
        if len(content) > 6000:
            return content[:6000] + f"\n\n[...truncated. Full file has {len(content)} characters]"
        return content
    except PermissionError:
        return f"❌ Permission denied: {filepath}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Creates or overwrites a file with the given content."""
    # Block writing to critical system paths
    BLOCKED_PATHS = ['/etc/', '/sys/', '/proc/', 'C:\\Windows\\System32']
    for bp in BLOCKED_PATHS:
        if bp.lower() in str(filepath).lower():
            return f"🛡️ Blocked: Cannot write to system path '{filepath}'."
    try:
        p = Path(filepath).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return f"✅ File written: `{p}` ({len(content)} characters)"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"


def delete_file(filepath: str) -> str:
    """Deletes a file. Protected system paths are blocked."""
    BLOCKED = ['/etc/', '/sys/', '/proc/', 'C:\\Windows\\System32', '/bin/', '/usr/bin/']
    for bp in BLOCKED:
        if bp.lower() in str(filepath).lower():
            return f"🛡️ Blocked: Cannot delete system file '{filepath}'."
    try:
        p = Path(filepath).expanduser().resolve()
        if not p.exists():
            return f"⚠️ File/folder not found: {filepath}"
        if p.is_dir():
            shutil.rmtree(p)
            return f"🗑️ Directory deleted: `{p}`"
        else:
            p.unlink()
            return f"🗑️ File deleted: `{p}`"
    except PermissionError:
        return f"❌ Permission denied: {filepath}"
    except Exception as e:
        return f"❌ Error deleting: {str(e)}"


def zip_folder(path: str, output_name: str = None) -> str:
    """Zips a file or folder into a .zip archive."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"❌ Path does not exist: {path}"
        
        out_name = output_name or (p.name + ".zip")
        if not out_name.endswith(".zip"):
            out_name += ".zip"
        out_path = p.parent / out_name
        
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if p.is_file():
                zf.write(p, p.name)
            else:
                for file in p.rglob("*"):
                    zf.write(file, file.relative_to(p.parent))
        
        size_mb = out_path.stat().st_size / 1024**2
        return f"📦 Zip created: `{out_path}` ({size_mb:.2f}MB)"
    except Exception as e:
        return f"❌ Zip failed: {str(e)}"
