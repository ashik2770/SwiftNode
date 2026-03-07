"""
swiftnode/tools/web.py
======================
Web research tools: DuckDuckGo search, URL fetch, Wikipedia, News, YouTube transcript.
"""
import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET


def search_internet(query: str) -> str:
    """Searches DuckDuckGo for real-time information and returns top results."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = [
            f"📌 {a.text.strip()}\n🔗 {a.get('href', '')}"
            for a in soup.find_all('a', class_='result__snippet', limit=5)
        ]
        return "\n\n".join(results) if results else "No clear results found."
    except Exception as e:
        return f"❌ Search failed: {str(e)}"


def fetch_webpage(url: str) -> str:
    """Extracts and returns main text content from a given URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "ads"]):
            tag.extract()
        text = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True))
        return text[:5000] + ("\n\n[...content truncated...]" if len(text) > 5000 else "")
    except Exception as e:
        return f"❌ Failed to fetch webpage: {str(e)}"


def get_wikipedia_summary(topic: str) -> str:
    """Gets a Wikipedia summary for a given topic using the Wikipedia REST API."""
    try:
        encoded = urllib.parse.quote(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        headers = {"User-Agent": "SwiftNode/4.0 (https://github.com/ashik2770/SwiftNode)"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 404:
            return f"❌ No Wikipedia article found for '{topic}'."
        data = res.json()
        title = data.get("title", topic)
        extract = data.get("extract", "No summary available.")
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        return f"📖 **{title}**\n\n{extract}\n\n🔗 {page_url}"
    except Exception as e:
        return f"❌ Wikipedia lookup failed: {str(e)}"


def get_top_news(category: str = "technology") -> str:
    """Gets top news headlines by category via Google News RSS."""
    category_map = {
        "technology": "TECHNOLOGY", "world": "WORLD", "sports": "SPORTS",
        "science": "SCIENCE", "business": "BUSINESS", "health": "HEALTH",
        "entertainment": "ENTERTAINMENT",
    }
    topic_code = category_map.get(category.lower(), "TECHNOLOGY")
    try:
        url = f"https://news.google.com/rss/headlines/section/topic/{topic_code}?hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")[:8]
        news = []
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            if title_el is not None:
                headline = title_el.text or ""
                link = link_el.text if link_el is not None else ""
                pub = pub_el.text if pub_el is not None else ""
                news.append(f"📰 {headline}\n   📅 {pub[:25] if pub else ''}\n   🔗 {link}")
        return f"📡 **Top {category.title()} News:**\n\n" + "\n\n".join(news) if news else "No news found."
    except Exception as e:
        return f"❌ News fetch failed: {str(e)}"


def get_youtube_transcript(url: str) -> str:
    """Attempts to get the transcript from a YouTube video."""
    try:
        # Extract video ID
        vid_id = None
        if "youtu.be/" in url:
            vid_id = url.split("youtu.be/")[1].split("?")[0]
        elif "v=" in url:
            vid_id = url.split("v=")[1].split("&")[0]
        
        if not vid_id:
            return "❌ Could not extract YouTube video ID from URL."

        # Use youtube-transcript-api if available
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(vid_id)
            full_text = " ".join([item['text'] for item in transcript_list])
            return f"📝 **YouTube Transcript** (video: {vid_id}):\n\n{full_text[:4000]}" + \
                   ("\n\n[...transcript truncated...]" if len(full_text) > 4000 else "")
        except ImportError:
            return "⚠️ youtube-transcript-api not installed. Run: pip install youtube-transcript-api"
        except Exception as e:
            return f"❌ Could not get transcript: {str(e)}"
    except Exception as e:
        return f"❌ YouTube transcript failed: {str(e)}"
