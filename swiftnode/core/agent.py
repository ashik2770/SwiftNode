"""
swiftnode/core/agent.py
=======================
SwiftNodeCore V5 — AI agent powered by litellm for 100+ provider support.
"""
import json
import time
from typing import Callable, Optional
from swiftnode.config import load_config, SwiftNodeSettings
from swiftnode.tools import AVAILABLE_TOOLS, AI_TOOL_SCHEMA, DEVICE_OS
from swiftnode.core.memory import EnhancedVectorMemory
from swiftnode.core.prompt import generate_system_prompt

try:
    import litellm
    from litellm import completion as litellm_completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

# Fallback to requests if litellm not installed yet
import requests


class SwiftNodeCore:
    def __init__(self, config: dict = None):
        self.config = config or load_config()
        if not self.config:
            raise RuntimeError("No config found. Run `swiftnode config` to set up.")

        # Load via Pydantic for validation + defaults
        try:
            settings = SwiftNodeSettings(**self.config)
        except Exception:
            # Gracefully handle unknown fields from legacy configs
            settings = SwiftNodeSettings()

        self.api_key = settings.api_key or self.config.get("api_key", "")
        self.base_url = settings.base_url
        self.model = settings.model
        self.provider = settings.provider
        self.max_tool_iterations = settings.max_tool_iterations
        self.temperature = settings.temperature
        self.reasoning_effort = settings.reasoning_effort
        self.multi_device_enabled = settings.multi_device_enabled
        self.connected_devices = settings.connected_devices

        self.memory = EnhancedVectorMemory(self.api_key)

        # Build OS-specific tool set
        self._available_tools = AVAILABLE_TOOLS.copy()
        self._available_tools["save_to_long_term_memory"] = self.memory.save_memory

        self._tool_schema = AI_TOOL_SCHEMA + [{
            "type": "function",
            "function": {
                "name": "save_to_long_term_memory",
                "description": "Saves critical facts, user preferences, or important data to the persistent long-term memory database.",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "The exact text to save to memory"}},
                    "required": ["text"]
                }
            }
        }]

    @property
    def available_tools(self):
        return self._available_tools

    def _call_litellm(self, messages: list, max_retries: int = 3) -> dict:
        """Call LLM via litellm (supports 100+ providers)."""
        # Set API credentials via litellm env-style
        import os
        os.environ["OPENAI_API_KEY"] = self.api_key

        extra_kwargs = {}
        if self.reasoning_effort:
            extra_kwargs["reasoning_effort"] = self.reasoning_effort

        # Build model string with provider prefix if needed
        model_str = self.model
        provider_lower = self.provider.lower()
        if provider_lower == "openrouter" and not model_str.startswith("openrouter/"):
            model_str = f"openrouter/{model_str}"
            os.environ["OPENROUTER_API_KEY"] = self.api_key
        elif provider_lower == "anthropic" and not model_str.startswith("anthropic/"):
            model_str = f"anthropic/{model_str}"
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
        elif provider_lower == "groq" and not model_str.startswith("groq/"):
            model_str = f"groq/{model_str}"
            os.environ["GROQ_API_KEY"] = self.api_key
        elif provider_lower == "gemini" and not model_str.startswith("gemini/"):
            model_str = f"gemini/{model_str}"
            os.environ["GEMINI_API_KEY"] = self.api_key
        elif provider_lower == "deepseek" and not model_str.startswith("deepseek/"):
            model_str = f"deepseek/{model_str}"
            os.environ["DEEPSEEK_API_KEY"] = self.api_key

        for attempt in range(max_retries):
            try:
                response = litellm_completion(
                    model=model_str,
                    messages=messages,
                    tools=self._tool_schema,
                    tool_choice="auto",
                    temperature=self.temperature,
                    api_base=self.base_url if self.provider.lower() == "custom" else None,
                    **extra_kwargs,
                )
                # Convert to dict-like for compatibility
                return response.model_dump()
            except Exception as e:
                err = str(e)
                if "RateLimitError" in err or "429" in err:
                    wait = 5 * (attempt + 1)
                    print(f"⏳ Rate limit. Waiting {wait}s... ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                elif "AuthenticationError" in err or "401" in err or "403" in err:
                    raise Exception(f"❌ Authentication error: check your API key. ({err[:100]})")
                else:
                    if attempt < max_retries - 1:
                        print(f"⏳ Error: {err[:80]}. Retrying... ({attempt+1}/{max_retries})")
                        time.sleep(3)
                    else:
                        raise Exception(f"❌ LLM failed after {max_retries} retries: {err[:200]}")

        raise Exception("❌ API failed after maximum retries.")

    def _call_requests(self, messages: list, max_retries: int = 3) -> dict:
        """Fallback: call via raw requests (legacy behaviour)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if "openrouter" in self.provider.lower():
            headers["HTTP-Referer"] = "https://github.com/ashik2770/SwiftNode"
            headers["X-Title"] = "SwiftNode"

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self._tool_schema,
            "tool_choice": "auto",
        }
        for attempt in range(max_retries):
            try:
                res = requests.post(self.base_url, headers=headers, json=payload, timeout=90)
                if res.status_code == 200:
                    return res.json()
                elif res.status_code == 429:
                    wait = 5 * (attempt + 1)
                    print(f"⏳ Rate limit. Waiting {wait}s... ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                elif res.status_code in (401, 403):
                    raise Exception(f"❌ Authentication error {res.status_code}. Check your API key.")
                else:
                    raise Exception(f"API Error {res.status_code}: {res.text[:200]}")
            except requests.exceptions.Timeout:
                print(f"⏳ Request timeout. Retrying... ({attempt+1}/{max_retries})")
                time.sleep(3)
            except requests.exceptions.ConnectionError:
                print(f"🌐 Connection failed. Retrying... ({attempt+1}/{max_retries})")
                time.sleep(3)
        raise Exception("❌ API failed after maximum retries.")

    def call_llm(self, messages: list, max_retries: int = 3) -> dict:
        """Unified LLM call: prefers litellm, falls back to requests."""
        if LITELLM_AVAILABLE:
            return self._call_litellm(messages, max_retries)
        return self._call_requests(messages, max_retries)

    def process_query(
        self,
        user_text: str,
        on_tool_call: Optional[Callable] = None,
    ) -> str:
        """
        Main agentic loop: sends query through LLM, handles tool calls,
        and returns the final response.

        Args:
            user_text:   The user's input text.
            on_tool_call: Optional callback(name, args) fired on each tool execution.
        """
        relevant_past = self.memory.search_memory(user_text)
        sys_msg = generate_system_prompt(
            relevant_memory=relevant_past,
            available_tools=list(self._available_tools.keys()),
            connected_devices=self.connected_devices if self.multi_device_enabled else None,
        )

        messages = [{"role": "system", "content": sys_msg}]
        messages.extend(self.memory.get_context(limit=10))
        messages.append({"role": "user", "content": f"<user_input>\n{user_text}\n</user_input>"})

        self.memory.log_chat("user", user_text)

        for iteration in range(self.max_tool_iterations):
            response = self.call_llm(messages)

            # Support both litellm model_dump() and raw OpenAI dict
            choices = response.get("choices", [])
            if not choices:
                break
            ai_msg = choices[0].get("message", {})

            if not ai_msg.get("content"):
                ai_msg["content"] = ""

            messages.append(ai_msg)

            tool_calls = ai_msg.get("tool_calls") or []
            if tool_calls:
                for tool_call in tool_calls:
                    fn = tool_call.get("function", {})
                    name = fn.get("name", "")
                    try:
                        args = json.loads(fn.get("arguments", "{}"))
                        if on_tool_call:
                            on_tool_call(name, args)

                        print(
                            f"  🔧 [{DEVICE_OS}] {name}("
                            + ", ".join(f"{k}={repr(v)[:30]}" for k, v in args.items())
                            + ")"
                        )

                        if name in self._available_tools:
                            result = self._available_tools[name](**args)
                        else:
                            result = f"❌ Tool '{name}' not found."
                    except json.JSONDecodeError:
                        result = "❌ Invalid tool arguments received."
                    except TypeError as e:
                        result = f"❌ Tool argument error: {str(e)}"
                    except Exception as e:
                        result = f"❌ Tool execution error: {str(e)}"

                    tc_id = (
                        tool_call.get("id")
                        if isinstance(tool_call, dict)
                        else getattr(tool_call, "id", str(iteration))
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "name": name,
                        "content": str(result)[:16000],  # Increased cap for richer results
                    })
                time.sleep(0.3)
            else:
                final_reply = ai_msg.get("content", "⚠️ No response generated.")
                self.memory.log_chat("assistant", final_reply)
                return final_reply

        fallback = "⚠️ Maximum processing iterations reached. The task may be too complex."
        self.memory.log_chat("assistant", fallback)
        return fallback
