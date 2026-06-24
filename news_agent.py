import os
import requests
import feedparser
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# News Sources
feeds = [
    "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "https://feeds.feedburner.com/TechCrunch",
]

headlines = []

for url in feeds:
    try:
        feed = feedparser.parse(url)
        for item in feed.entries[:15]:
            headlines.append(item.title)
    except:
        pass

news_text = "\n".join(headlines[:50])

prompt = f"""
Create a Telegram-ready intelligence report.

Format:

📰 DAILY INTELLIGENCE REPORT

🌍 World News
💼 Business News
🤖 AI & Technology
🪙 Crypto & Markets

For each story:
- Headline
- One-line summary
- Impact: 🟢 Bullish / 🔴 Bearish / ⚪ Neutral

At the end include:

📈 Global Sentiment Score (1-10)
🔥 Top Story of the Day

Rules:
- No introductions
- No markdown
- Professional formatting
- Maximum 20 stories

News:
{news_text}
"""

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

message = response.text[:4000]

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": message
    }
)
