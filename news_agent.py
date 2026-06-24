import os
import requests
import feedparser
from google import genai

# -----------------------------
# ENV VARIABLES (SAFE CHECK)
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GEMINI_API_KEY or not BOT_TOKEN or not CHAT_ID:
    raise Exception("Missing environment variables")

# -----------------------------
# NEWS SOURCES
# -----------------------------
feeds = [
    "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "https://feeds.feedburner.com/TechCrunch",
]

# -----------------------------
# FETCH HEADLINES
# -----------------------------
headlines = []

for url in feeds:
    try:
        feed = feedparser.parse(url)
        for item in feed.entries[:10]:
            if item.title not in headlines:
                headlines.append(item.title)
    except Exception as e:
        print("Feed error:", e)

# Limit noise
headlines = headlines[:30]

news_text = "\n".join(headlines)

# -----------------------------
# SMART PROMPT (UPGRADED)
# -----------------------------
prompt = f"""
You are an AI Market Intelligence Analyst.

TASK:
Create a HIGH QUALITY Telegram intelligence report.

RULES:
- Only keep high-impact global news
- Remove useless or repetitive news
- Focus on economy, war, crypto, AI, markets
- Assign market impact properly

FORMAT:

📰 DAILY INTELLIGENCE REPORT

🌍 WORLD NEWS
- Headline
- 1 line summary
- Impact: 🟢 Bullish / 🔴 Bearish / ⚪ Neutral
- Market: BTC / NIFTY / GOLD / OIL / GLOBAL

🪙 CRYPTO & MARKETS
(same format)

📊 FINAL SUMMARY
- Global Sentiment Score (1–10)
- Market Bias (Risk-on / Risk-off)
- Top Story

MAX 12 STORIES ONLY

NEWS:
{news_text}
"""

# -----------------------------
# GEMINI CALL
# -----------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    message = response.text
except Exception as e:
    message = f"AI Error: {str(e)}"

# Limit Telegram message size
message = message[:4000]

# -----------------------------
# SEND TO TELEGRAM
# -----------------------------
try:
    res = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        }
    )
    print("Telegram sent:", res.status_code)
except Exception as e:
    print("Telegram error:", e)
