# SwiftNode ⚡

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**An autonomous, pip-installable AI personal agent with multi-device control, Discord/Telegram/WhatsApp integration, long-term RAG memory, and 23+ powerful tools.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-cli-commands) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**SwiftNode** is a cutting-edge personal computing intelligence framework. It acts as your localized AI assistant capable of automating your daily workflow across multiple devices. With out-of-the-box support for leading LLMs, memory persistence, and deep OS-level integration, SwiftNode scales from a simple CLI chatbot to a comprehensive multi-node automation network.

**Topics/Tags:** `ai-agent` `automation` `llm` `multi-device` `telegram-bot` `discord-bot` `whatsapp-bot` `rag` `python`

---

## 🚀 Features

| Category | Capabilities |
|----------|--------------|
| 🤖 **Bot Integrations** | Seamless connections with **Telegram**, **Discord**, and **WhatsApp** (Selenium QR Auth). |
| 🌐 **Web Research** | DuckDuckGo search, URL fetch, Wikipedia, Top News, YouTube transcript extraction. |
| 💻 **System Control** | CPU/RAM/Disk polling, Screenshots, Subprocess management, Process termination. |
| 📋 **Clipboard & OS** | Read & Write clipboard, Desktop push notifications, file zipping and management. |
| 🌍 **Network Ops** | Public IP retrieval, ICMP Ping, LAN device scanner, Bandwidth speed tests. |
| 🐍 **Code Execution** | Secure execution of Python snippets, automated Linting and syntax validation. |
| 📱 **Android via ADB** | Tap, Swipe, Type, APK Install, Screenshots, Screen Recording, internal Shell access. |
| 🧠 **Persistent Memory** | Long-term RAG vector memory backed by Google Embeddings and SQLite. |
| 🔗 **Multi-Device Grid** | HTTP API to control any connected worker node across your Local Area Network. |

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Chrome/ChromeDriver (for WhatsApp Bot functionality)

### Install via Source (Development/Current)

```bash
git clone https://github.com/ashik2770/SwiftNode.git
cd SwiftNode
pip install -e .
```

---

## ⚡ Quick Start

### 1. Initial Configuration

Run the automated setup wizard to link your LLM Provider, configure your bot platform, and set up your multi-device network.

```bash
swiftnode config
```

### 2. Start Your Agent

```bash
# Starts the default bot platform specified during config
swiftnode run 

# Or explicitly start a specific platform
swiftnode run --bot telegram
swiftnode run --bot discord
swiftnode run --bot whatsapp
```

---

## 🖥️ CLI Commands

| Command | Description |
|---------|-------------|
| `swiftnode run` | 🚀 Start the default messaging bot |
| `swiftnode run --bot <name>` | 🌐 Start a specific bot (telegram/discord/whatsapp) |
| `swiftnode config` | ⚙️ Setup or reconfigure your environment |
| `swiftnode serve` | 🌐 Start multi-device HTTP server node |
| `swiftnode connect <ip:port>` | 📡 Connect to a remote SwiftNode device |
| `swiftnode tools` | 🔧 List all active system tools |
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
swiftnode connect 192.168.1.100:7799
# Interactive REPL connected directly to the remote agent
```

---

## 🧠 Supported AI Engine Providers

SwiftNode is model-agnostic and seamlessly connects to:
- **Gemini** (Google API) ✅ *Default Recommended*
- **OpenAI** (GPT-4o, o1)
- **Grok** (xAI)
- **Hugging Face** (Serverless Inference API)
- **OpenRouter** (Unified API for Claude, Mistral, etc.)
- **Ollama** (Local execution, absolute privacy)
- **vLLM** (Self-hosted high-performance execution)

---

## 🛡️ Security Posture

- **Owner Authorization** — Hardware and bot requests are strictly tied to configured `owner_id`.
- **System Guardrails** — RegEx and path validation prevent OS-level catastrophic deletion.
- **Secret Token Auth** — Multi-device nodes authenticate using encrypted preshared tokens.
- **Local Vectors** — Search and embedding memory stays local using SQLite.

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

Distributed under the MIT License. See `LICENSE` for more information.

---
<div align="center">
  <i>Built with 💡 & ☕ by the SwiftNode Team</i>
</div>
