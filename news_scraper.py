import feedparser
from datetime import datetime, timedelta

# RSS feed from BleepingComputer
RSS_URL = "https://www.bleepingcomputer.com/feed/"
KEYWORDS = [
    "hospital", "clinic", "healthcare", "medtech", "medical", "EMR", "ehr",
    "HHS", "pharma", "provider", "cyberattack", "ransomware", "data breach"
]

# Parse RSS and filter relevant stories
feed = feedparser.parse(RSS_URL)
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

# Build news HTML section
news_html = f"""
<!-- START-NEWS-SECTION -->
<h2>📰 Recent Healthcare Threat News</h2>
<p>As of {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | Source: <a href="{RSS_URL}">BleepingComputer RSS</a></p>
<ul>
"""

if not filtered:
    news_html += "<li>No healthcare-relevant news found in the last 24 hours.</li>"
else:
    for article in filtered:
        news_html += f"""
        <li>
            <strong><a href="{article['link']}" target="_blank">{article['title']}</a></strong><br>
            <em>{article['published']}</em><br>
            {article['summary'][:300]}...
        </li><br>
        """

news_html += "</ul>\n<!-- END-NEWS-SECTION -->"

# Insert into index.html
try:
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = "<html><head><title>ThreatPodium</title></head><body><!-- START-BREACH-SECTION --><!-- END-BREACH-SECTION --><!-- START-NEWS-SECTION --><!-- END-NEWS-SECTION --></body></html>"

start = content.find("<!-- START-NEWS-SECTION -->")
end = content.find("<!-- END-NEWS-SECTION -->") + len("<!-- END-NEWS-SECTION -->")
new_content = content[:start] + news_html + content[end:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_content)
