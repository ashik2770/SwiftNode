<#
.SYNOPSIS
SwiftNode Advanced Installer for Windows
#>

Write-Host " ███████╗██╗    ██╗██╗███████╗████████╗███╗   ██╗ ██████╗ ██████╗ ███████╗" -ForegroundColor Cyan
Write-Host " ██╔════╝██║    ██║██║██╔════╝╚══██╔══╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝" -ForegroundColor Cyan
Write-Host " ███████╗██║ █╗ ██║██║█████╗     ██║   ██╔██╗ ██║██║   ██║██║  ██║█████╗  " -ForegroundColor Cyan
Write-Host " ╚════██║██║███╗██║██║██╔══╝     ██║   ██║╚██╗██║██║   ██║██║  ██║██╔══╝  " -ForegroundColor Cyan
Write-Host " ███████║╚███╔███╔╝██║██║        ██║   ██║ ╚████║╚██████╔╝██████╔╝███████╗" -ForegroundColor Cyan
Write-Host " ╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝" -ForegroundColor Cyan
Write-Host "`n🚀 Starting SwiftNode Installation...`n" -ForegroundColor Green

# Check for Python
$pythonExists = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonExists) {
    Write-Host "❌ Python is not installed or not in PATH. Please install Python 3.9+." -ForegroundColor Red
    exit 1
}

Write-Host "💻 Windows OS Detected." -ForegroundColor DarkCyan
Write-Host "📦 Setting up Python virtual environment..." -ForegroundColor DarkCyan

python -m venv venv
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "📦 Installing pip dependencies..." -ForegroundColor DarkCyan
python -m pip install --upgrade pip
pip install -e .

Write-Host "`n✅ SwiftNode installed successfully!" -ForegroundColor Green
Write-Host "To start, run: " -NoNewline
Write-Host ".\venv\Scripts\swiftnode.exe config" -ForegroundColor Cyan
