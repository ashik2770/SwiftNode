"""
swiftnode/core/agent.py
=======================
SwiftNodeCore — Main AI agent with tool loop and memory integration.
"""
import json
import requests
import time
from swiftnode.config import load_config
from swiftnode.tools import AVAILABLE_TOOLS, AI_TOOL_SCHEMA, DEVICE_OS
from swiftnode.core.memory import EnhancedVectorMemory
from swiftnode.core.prompt import generate_system_prompt


class SwiftNodeCore:
    def __init__(self, config: dict = None):
        self.config = config or load_config()
        if not self.config:
            raise RuntimeError("No config found. Run `swiftnode config` to set up.")

        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config["base_url"]
        self.model = self.config["model"]
        self.provider = self.config.get("provider", "Unknown")
        self.multi_device_enabled = self.config.get("multi_device_enabled", False)
        self.connected_devices = self.config.get("connected_devices", [])

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

    def call_llm(self, messages: list, max_retries: int = 3) -> dict:
        """Calls the configured LLM API with retry and rate-limit handling."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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

    def process_query(self, user_text: str, on_tool_call=None) -> str:
        """
        Main processing loop: sends query through LLM, handles tool calls,
        and returns the final response.

        Args:
            user_text: The user's input
            on_tool_call: Optional callback(name, args) called on each tool execution
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

        max_iterations = 8

        for iteration in range(max_iterations):
            response = self.call_llm(messages)
            ai_msg = response["choices"][0]["message"]

            if not ai_msg.get("content"):
                ai_msg["content"] = ""

            messages.append(ai_msg)

            if ai_msg.get("tool_calls"):
                for tool_call in ai_msg["tool_calls"]:
                    name = tool_call["function"]["name"]
                    try:
                        args = json.loads(tool_call["function"]["arguments"])
                        if on_tool_call:
                            on_tool_call(name, args)
                        
                        print(f"  🔧 [{DEVICE_OS}] {name}({', '.join(f'{k}={repr(v)[:30]}' for k,v in args.items())})")
                        
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

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": name,
                        "content": str(result)[:8000]  # Cap result size
                    })
                time.sleep(0.5)
            else:
                final_reply = ai_msg.get("content", "⚠️ No response generated.")
                self.memory.log_chat("assistant", final_reply)
                return final_reply

        fallback = "⚠️ Maximum processing iterations reached. The task may be too complex."
        self.memory.log_chat("assistant", fallback)
        return fallback
