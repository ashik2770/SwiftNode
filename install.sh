#!/usr/bin/env bash
# SwiftNode V5 Installer — Termux (Android) + Linux/macOS

set -e

echo -e "\033[1;36m"
echo " ███████╗██╗    ██╗██╗███████╗████████╗███╗   ██╗ ██████╗ ██████╗ ███████╗"
echo " ██╔════╝██║    ██║██║██╔════╝╚══██╔══╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝"
echo " ███████╗██║ █╗ ██║██║█████╗     ██║   ██╔██╗ ██║██║   ██║██║  ██║█████╗  "
echo " ╚════██║██║███╗██║██║██╔══╝     ██║   ██║╚██╗██║██║   ██║██║  ██║██╔══╝  "
echo " ███████║╚███╔███╔╝██║██║        ██║   ██║ ╚████║╚██████╔╝██████╔╝███████╗"
echo " ╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝"
echo -e "\033[0m"
echo -e "\033[1;32m🚀 Starting SwiftNode V5 Installation...\033[0m\n"

# OS Detection
OS_TYPE=$(uname -o 2>/dev/null || uname -s)
IS_TERMUX=false

if [[ "$PREFIX" == *com.termux* || "$OS_TYPE" == *"Android"* ]]; then
    IS_TERMUX=true
fi

if [ "$IS_TERMUX" = true ]; then
    echo -e "\033[1;33m📱 Termux (Android) Detected!\033[0m"
    echo -e "Installing required Termux native packages...\n"
    pkg update -y
    # litellm needs Rust build tools & libopenblas for tokenizer deps
    pkg install -y python python-pip clang libffi libjpeg-turbo openssl rust libopenblas
    
    echo -e "\n\033[1;34m📦 Installing pip dependencies for Termux...\033[0m"
    # Ensure rust and cargo aren't strictly required by using precompiled or disabling strict build flags where possible
    MATHLIB="m" pip install -e .
else
    echo -e "\033[1;34m💻 Standard OS ($OS_TYPE) Detected.\033[0m"
    if ! command -v python3 &> /dev/null; then
        echo -e "\033[1;31m❌ Python 3 is not installed. Please install Python 3.9+ to continue.\033[0m"
        exit 1
    fi
    
    echo -e "\033[1;34m📦 Setting up Python virtual environment...\033[0m"
    python3 -m venv venv
    source venv/bin/activate
    
    echo -e "\033[1;34m📦 Installing pip dependencies...\033[0m"
    pip install --upgrade pip
    pip install -e .
fi

echo -e "\n\033[1;32m✅ SwiftNode V5 installed successfully!\033[0m"
echo -e "Run: \033[1;36mswiftnode config\033[0m  →  \033[1;36mswiftnode run\033[0m  (or \033[1;36mswiftnode chat\033[0m for terminal mode)"
