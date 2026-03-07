"""
swiftnode/tools/code.py
======================
Code execution and linting tools (sandboxed Python runner).
"""
import io
import sys
import traceback
import ast
import builtins


# Allowed built-in names for sandboxed execution
_SAFE_BUILTINS = {
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray',
    'bytes', 'callable', 'chr', 'complex', 'dict', 'dir', 'divmod',
    'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals',
    'hasattr', 'hash', 'help', 'hex', 'int', 'isinstance', 'issubclass',
    'iter', 'len', 'list', 'locals', 'map', 'max', 'min', 'next', 'object',
    'oct', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed',
    'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str',
    'sum', 'super', 'tuple', 'type', 'vars', 'zip',
    'True', 'False', 'None',
    'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError', 'AttributeError',
    '__name__', '__doc__', '__package__', '__spec__',
}

_BLOCKED_IMPORTS = {'os', 'subprocess', 'shutil', 'sys', 'socket', 'multiprocessing', 'threading'}


def run_python_snippet(code: str) -> str:
    """
    Safely executes a Python code snippet in a restricted sandbox.
    Returns stdout output and any errors.
    """
    # Check for blocked imports
    for blocked in _BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return f"🛡️ Import of '{blocked}' is blocked for security. Use the dedicated tools instead."
    
    # Check for dangerous patterns
    BLOCKED_PATTERNS = ['__import__', 'eval(', 'exec(', 'compile(', 'open(', '__builtins__']
    for pattern in BLOCKED_PATTERNS:
        if pattern in code:
            return f"🛡️ Pattern '{pattern}' is blocked in the sandbox."
    
    # Syntax check first
    try:
        ast.parse(code)
    except SyntaxError as e:
        return f"❌ **Syntax Error:** {e}"
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    
    try:
        safe_globals = {
            "__builtins__": {k: getattr(builtins, k) for k in _SAFE_BUILTINS if hasattr(builtins, k)},
        }
        exec(code, safe_globals)
        output = captured.getvalue()
        return f"✅ **Output:**\n```\n{output}\n```" if output else "✅ Code executed successfully (no output)."
    except Exception as e:
        return f"❌ **Runtime Error:**\n```\n{traceback.format_exc()}\n```"
    finally:
        sys.stdout = old_stdout


def lint_code(code: str) -> str:
    """
    Checks Python code for syntax errors using AST parsing.
    Returns warnings and suggestions.
    """
    try:
        tree = ast.parse(code)
        
        issues = []
        
        # Check for common bad patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ('eval', 'exec', 'compile'):
                        issues.append(f"⚠️ Line {node.lineno}: Dangerous function '{node.func.id}' detected.")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _BLOCKED_IMPORTS:
                        issues.append(f"⚠️ Line {node.lineno}: Import of '{alias.name}' is potentially unsafe.")
        
        if issues:
            return "🔍 **Lint Results — Issues Found:**\n" + "\n".join(issues)
        
        # Count stats
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        lines = len(code.split('\n'))
        
        return (
            f"✅ **No syntax errors found!**\n"
            f"📊 Stats: {lines} lines, {len(funcs)} function(s), {len(classes)} class(es)"
        )
    except SyntaxError as e:
        return f"❌ **Syntax Error** at line {e.lineno}: {e.msg}\n   → `{e.text.strip() if e.text else ''}`"
    except Exception as e:
        return f"❌ Lint failed: {str(e)}"
