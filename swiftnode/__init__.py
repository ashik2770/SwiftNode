"""
SwiftNode — Ultra-Powerful Personal AI Agent
=============================================
An autonomous, pip-installable AI assistant with:
- 100+ LLM provider support via litellm (OpenAI, Anthropic, Gemini, Groq, DeepSeek, etc.)
- Multi-device control (PC ↔ Android via ADB)
- Telegram, Discord, WhatsApp bot integration
- 30+ powerful tools (Web, System, Files, Network, Code, Extras)
- Interactive terminal chat mode (no bot required)
- Long-term RAG vector memory
- Termux / Android (Armv8) native support

Usage:
    pip install swiftnode
    swiftnode config        # First-time setup
    swiftnode run           # Start bot (Telegram/Discord/WhatsApp)
    swiftnode chat          # Interactive terminal chat
    swiftnode serve         # Start multi-device HTTP server
    swiftnode connect <ip>  # Connect to master device
    swiftnode tools         # List available tools
    swiftnode update        # Self-update via pip
"""

__version__ = "5.0.0"
__author__ = "SwiftNode Team"
__description__ = "Ultra-Powerful Personal AI Agent with 100+ LLM Provider Support"
