import feedparser
from datetime import datetime, timedelta

# RSS feed URL from BleepingComputer
RSS_URL = "https://www.bleepingcomputer.com/feed/"

# Define keywords that signal relevance to healthcare threats
KEYWORDS = [
    "hospital", "clinic", "healthcare", "medtech", "medical", "EMR", "ehr",
    "HHS", "pharma", "provider", "cyberattack", "ransomware", "data breach"
]

# Parse RSS feed
feed = feedparser.parse(RSS_URL)

# Filter articles from the last 24 hours that mention healthcare
now = datetime.utcnow()
one_day_ago = now - timedelta(days=1)
filtered = []

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

# Build HTML
timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
html = f"""
<h2>📰 Recent News: Healthcare-Related Threats</h2>
<p>As of {timestamp} | Source: <a href="{RSS_URL}">BleepingComputer RSS</a></p>
<ul>
"""

if not filtered:
    html += "<li>No healthcare-relevant news found in the last 24 hours.</li>"
else:
    for article in filtered:
        html += f"""
        <li>
            <strong><a href="{article['link']}" target="_blank">{article['title']}</a></strong><br>
            <em>{article['published']}</em><br>
            {article['summary'][:300]}...
        </li>
        <br>
        """

html += "</ul>"

# Save output to file
with open("news.html", "w", encoding="utf-8") as f:
    f.write(html)
