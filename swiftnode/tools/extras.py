"""
swiftnode/tools/extras.py
=========================
SwiftNode V5 — Extra utility tools:
  math_calc, base64_encode, base64_decode, translate_text, get_weather, hash_text
"""
import base64
import hashlib
import math
import re
import requests


# ── Math Calculator ───────────────────────────────────────────────────────────

def math_calc(expression: str) -> str:
    """
    Safely evaluate a mathematical expression and return the result.
    Supports: +, -, *, /, **, %, sqrt(), sin(), cos(), tan(), log(), abs(), round().
    """
    # Whitelist: only numeric and safe math tokens
    safe_expr = re.sub(r"[^0-9+\-*/().%, ]", "", expression)
    # Allow Python math functions
    allowed_names = {
        k: getattr(math, k)
        for k in dir(math)
        if not k.startswith("_")
    }
    allowed_names["abs"] = abs
    allowed_names["round"] = round

    try:
        result = eval(safe_expr, {"__builtins__": {}}, allowed_names)  # noqa: S307
        return f"🔢 Result: `{expression}` = **{result}**"
    except ZeroDivisionError:
        return "❌ Division by zero."
    except Exception as e:
        return f"❌ Math error: {str(e)}"


# ── Base64 Encode / Decode ────────────────────────────────────────────────────

def base64_encode(text: str) -> str:
    """Encode a UTF-8 string to Base64."""
    try:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f"🔐 Base64 Encoded:\n```\n{encoded}\n```"
    except Exception as e:
        return f"❌ Encode error: {str(e)}"


def base64_decode(text: str) -> str:
    """Decode a Base64 string back to UTF-8."""
    try:
        decoded = base64.b64decode(text.strip()).decode("utf-8")
        return f"🔓 Base64 Decoded:\n```\n{decoded}\n```"
    except Exception as e:
        return f"❌ Decode error: {str(e)}"


# ── Text Hasher ───────────────────────────────────────────────────────────────

SUPPORTED_ALGOS = {"md5", "sha1", "sha256", "sha512"}

def hash_text(text: str, algorithm: str = "sha256") -> str:
    """
    Generate a hash digest of the given text.
    algorithm: md5 | sha1 | sha256 | sha512  (default: sha256)
    """
    algo = algorithm.lower()
    if algo not in SUPPORTED_ALGOS:
        return f"❌ Unsupported algorithm `{algorithm}`. Choose from: {', '.join(SUPPORTED_ALGOS)}"
    try:
        h = hashlib.new(algo, text.encode("utf-8")).hexdigest()
        return f"🔑 {algo.upper()} hash of `{text[:40]}{'...' if len(text) > 40 else ''}`:\n`{h}`"
    except Exception as e:
        return f"❌ Hash error: {str(e)}"


# ── Weather ───────────────────────────────────────────────────────────────────

def get_weather(city: str) -> str:
    """
    Get current weather for a city using wttr.in (no API key needed).
    Returns a concise weather report with temperature, condition, wind, and humidity.
    """
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]
        area = data.get("nearest_area", [{}])[0]
        area_name = area.get("areaName", [{}])[0].get("value", city)
        country = area.get("country", [{}])[0].get("value", "")

        temp_c = current.get("temp_C", "?")
        temp_f = current.get("temp_F", "?")
        feels_c = current.get("FeelsLikeC", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
        humidity = current.get("humidity", "?")
        wind_kmph = current.get("windspeedKmph", "?")
        wind_dir = current.get("winddir16Point", "?")
        visibility = current.get("visibility", "?")

        return (
            f"🌤 **Weather in {area_name}, {country}**\n"
            f"• Condition: {desc}\n"
            f"• Temperature: {temp_c}°C / {temp_f}°F  (Feels like {feels_c}°C)\n"
            f"• Humidity: {humidity}%\n"
            f"• Wind: {wind_kmph} km/h {wind_dir}\n"
            f"• Visibility: {visibility} km"
        )
    except requests.exceptions.ConnectionError:
        return f"❌ Network error fetching weather for `{city}`."
    except Exception as e:
        return f"❌ Weather fetch error: {str(e)}"


# ── Translate ─────────────────────────────────────────────────────────────────

def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to the target language using the free MyMemory API.
    target_lang: ISO 639-1 language code, e.g. 'bn' (Bangla), 'fr', 'es', 'ar', 'zh'.
    """
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text[:500], "langpair": f"auto|{target_lang}"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        if not translated or "INVALID" in translated.upper():
            return f"❌ Translation failed. Check the language code `{target_lang}`."
        return f"🌐 **Translated → {target_lang.upper()}:**\n{translated}"
    except requests.exceptions.ConnectionError:
        return "❌ Network error during translation."
    except Exception as e:
        return f"❌ Translation error: {str(e)}"
