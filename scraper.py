import feedparser
from datetime import datetime, timedelta

# BleepingComputer RSS Feed URL
RSS_URL = "https://www.bleepingcomputer.com/feed/"
KEYWORDS = [
    "hospital", "clinic", "healthcare", "medtech", "medical", "EMR", "ehr",
    "HHS", "pharma", "provider", "cyberattack", "ransomware", "data breach"
]

# Parse the RSS feed
feed = feedparser.parse(RSS_URL)
now = datetime.utcnow()
one_day_ago = now - timedelta(days=1)
filtered = []

# Filter entries with relevant keywords in the last 24 hours
for entry in feed.entries:
    published = datetime(*entry.published_parsed[:6])
    if published < one_day_ago:
        continue
    summary = entry.summary.lower()
    title = entry.title.lower()
    if any(keyword in summary or keyword in title for keyword in KEYWORDS):
        filtered.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": published.strftime("%Y-%m-%d %H:%M UTC")
        })

# Format HTML block for injection
news_html = f"""
<!-- START-NEWS-SECTION -->
<h2>
