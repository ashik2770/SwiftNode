# SwiftNode V5 ⚡

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android%20(Termux)-lightgrey)

**An autonomous, pip-installable AI personal agent powered by Litellm (100+ providers), with interactive terminal chat, Discord/Telegram/WhatsApp integration, multi-device control, long-term RAG memory, and 30+ powerful tools.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [CLI Commands](#%EF%B8%8F-cli-commands) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**SwiftNode V5** is a cutting-edge personal computing intelligence framework. It acts as your localized AI assistant capable of automating your daily workflow across multiple devices. Powered by `litellm`, it seamlessly integrates with 100+ AI providers. SwiftNode scales from a simple CLI terminal chat to a comprehensive multi-node automation network.

**Topics/Tags:** `ai-agent` `automation` `llm` `multi-device` `telegram-bot` `discord-bot` `whatsapp-bot` `rag` `python` `termux`

---

## 🚀 Features

| Category | Capabilities |
|----------|--------------|
| 🧠 **AI Engine** | Powered by `litellm` — supports 100+ providers (OpenAI, Anthropic, Gemini, Groq, DeepSeek, local models, etc.) |
| 💬 **Terminal Chat** | Interactive, rich terminal chat mode directly from CLI without needing a bot platform. |
| 🤖 **Bot Integrations**| Seamless connections with **Telegram**, **Discord**, and **WhatsApp** (Selenium QR Auth). |
| 🌐 **Web Research**| DuckDuckGo search, URL fetch, Wikipedia, Top News, YouTube transcript extraction. |
| 💻 **System Control**| CPU/RAM/Disk polling, Screenshots, Subprocess management, Process termination. |
| 📦 **Files & Folders** | Read/write files, Desktop push notifications, file zipping and management. |
| 🌍 **Network Tasks** | Public IP retrieval, ICMP Ping, LAN device scanner, Bandwidth speed tests, real-time Weather. |
| 🐍 **Code & Math**| Secure execution of Python snippets, automated Linting, safe Math evaluation, Base64 encode/decode, hashing. |
| 📱 **Android / Termux**| Native support for Android (Termux) + ADB control (Tap, Swipe, Type, APK Install, Screenshots, Screen Recording). |
| 💾 **Persistent Memory**| Long-term RAG vector memory backed by Google Embeddings and SQLite. |
| 🔗 **Multi-Device Grid**| HTTP API to control any connected worker node across your Local Area Network. |

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- For Windows/macOS/Linux standard installation
- For Android: Install [Termux](https://termux.dev/en/)

### Install via pip (Recommended)
```bash
pip install swiftnode
```

### Install via Source (Development)
```bash
git clone https://github.com/ashik2770/SwiftNode.git
cd SwiftNode
pip install -e .
```

### Install on Termux (Android)
```bash
git clone https://github.com/ashik2770/SwiftNode.git
cd SwiftNode
./install.sh
```

---

## ⚡ Quick Start

### 1. Initial Configuration

Run the automated setup wizard to link your preferred LLM Provider (via litellm), configure your bot platform, and set up your multi-device network.

```bash
swiftnode config
```

### 2. Start Your Agent

```bash
# Start an interactive terminal chat (No bot setup required!)
swiftnode chat

# Start the messaging bot (Telegram/Discord/WhatsApp configured in setup)
swiftnode run 

# Explicitly start a specific bot platform
swiftnode run --bot telegram
swiftnode run --bot discord
```

---

## 🖥️ CLI Commands

| Command | Description |
|---------|-------------|
| `swiftnode chat` | 💬 Start interactive terminal chat session |
| `swiftnode run` | 🚀 Start the default messaging bot |
| `swiftnode run --bot <name>` | 🌐 Start a specific bot (telegram/discord/whatsapp) |
| `swiftnode config` | ⚙️ Setup or reconfigure your environment |
| `swiftnode serve` | 🌐 Start multi-device HTTP server node |
| `swiftnode connect <ip>` | 📡 Connect to a remote SwiftNode master device |
| `swiftnode tools` | 🔧 List all active context tools |
| `swiftnode update` | 🔄 Update SwiftNode via pip |
| `swiftnode version` | ℹ️ Show version and system diagnostics |

---

## 🌐 Multi-Device Control Architecture

Control **multiple physical devices** from a central brain. Works on PC, Termux (Android), Raspberry Pi, and macOS.

**1. Launch the Server Node (Master/Worker)**
```bash
swiftnode serve
# Starts a secure HTTP API on port 7799
```

**2. Form the Grid (Client)**
```bash
swiftnode connect 192.168.1.100
# Connects directly to the remote agent
```

---

## 🤝 Contributing

We welcome contributions! Please review our [Contribution Guidelines](CONTRIBUTING.md) before submitting pull requests. 
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---
<div align="center">
  <i>Built with 💡 & ☕ by the SwiftNode Team</i>
</div>
