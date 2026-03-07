"""
swiftnode/core/memory.py
=======================
EnhancedVectorMemory: SQLite + Google Embedding API with keyword fallback.
"""
import sqlite3
import json
import math
import requests
from datetime import datetime
from pathlib import Path


class EnhancedVectorMemory:
    def __init__(self, api_key: str):
        self.api_key = api_key
        db_dir = Path.home() / ".swiftnode"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_dir / "memory.sqlite")
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                text TEXT NOT NULL,
                embedding TEXT
            )
        ''')
        self.conn.commit()

    def get_embedding(self, text: str) -> list:
        """Gets embedding from Google's API. Falls back to None on failure."""
        if not self.api_key or self.api_key in ("ollama", "vllm", ""):
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
            payload = {"model": "models/text-embedding-004", "content": {"parts": [{"text": text}]}}
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                return res.json()['embedding']['values']
        except Exception:
            pass
        return None

    def cosine_similarity(self, v1: list, v2: list) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a**2 for a in v1))
        mag2 = math.sqrt(sum(b**2 for b in v2))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0.0

    def keyword_similarity(self, query: str, text: str) -> float:
        """Simple keyword-based similarity as fallback when no embeddings."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        overlap = query_words & text_words
        return len(overlap) / max(len(query_words), 1)

    def save_memory(self, text: str) -> str:
        """Saves a piece of information to long-term vector memory."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emb = self.get_embedding(text)
        self.cursor.execute(
            "INSERT INTO vectors (timestamp, text, embedding) VALUES (?, ?, ?)",
            (timestamp, text, json.dumps(emb) if emb else None)
        )
        self.conn.commit()
        return f"🧠 Memory saved at {timestamp}: '{text[:80]}...'" if len(text) > 80 else f"🧠 Memory saved: '{text}'"

    def search_memory(self, query: str, top_k: int = 3) -> str:
        """Searches vector memory for relevant past context."""
        self.cursor.execute("SELECT timestamp, text, embedding FROM vectors")
        rows = self.cursor.fetchall()
        if not rows:
            return ""

        query_emb = self.get_embedding(query)
        results = []

        for ts, text, emb_json in rows:
            if query_emb and emb_json:
                score = self.cosine_similarity(query_emb, json.loads(emb_json))
            else:
                score = self.keyword_similarity(query, text)
            results.append((score, f"[{ts}] {text}"))

        results.sort(key=lambda x: x[0], reverse=True)
        threshold = 0.3 if query_emb else 0.1
        top = [r[1] for r in results[:top_k] if r[0] > threshold]
        return "\n".join(top)

    def log_chat(self, role: str, content: str):
        """Logs a chat message to the history table."""
        self.cursor.execute(
            "INSERT INTO history (role, content) VALUES (?, ?)", (role, content)
        )
        self.conn.commit()

    def get_context(self, limit: int = 10) -> list:
        """Returns recent chat history as a list of message dicts."""
        self.cursor.execute(
            "SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [{"role": row[0], "content": row[1]} for row in self.cursor.fetchall()[::-1]]

    def clear_history(self):
        """Clears short-term chat history while keeping long-term memory."""
        self.cursor.execute("DELETE FROM history")
        self.conn.commit()
