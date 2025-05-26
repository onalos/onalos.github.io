import feedparser
from datetime import datetime
import re

# Define your sources
feeds = {
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "HealthITSecurity": "https://healthitsecurity.com/rss",
    "HelpNetSecurity": "https://www.helpnetsecurity.com/feed/",
    "HIPAA Journal": "https://www.hipaajournal.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Becker's Hospital Review": "https://www.beckershospitalreview.com/rss/rss.html",
    "CISA": "https://www.cisa.gov/news.xml"
}

# Keywords to filter against
keywords = [
    "health", "healthcare", "clinic", "patients", "hospital",
    "medical", "ehr", "pharma", "pharmaceutical", "drug"
]

# Match any keyword in a string
def is_relevant(text):
    return any(kw in text.lower() for kw in keywords)

# Parse feeds and filter
items = []
for source, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:20]:
        text = f"{entry.get('title', '')} {entry.get('summary', '')}"
        if is_relevant(text):
            date = entry.get('published', 'Unknown')
            try:
                parsed_date = datetime(*entry.published_parsed[:6])
                date_str = parsed_date.strftime("%B %d, %Y")
            except:
                date_str = date

            items.append({
                "title": entry.get("title", "No Title"),
                "link": entry.get("link", "#"),
                "date": date_str,
                "source": source
            })

# Sort newest first (where possible)
def parse_date(item):
    try:
        return datetime.strptime(item["date"], "%B %d, %Y")
    except:
        return datetime.min

items = sorted(items, key=parse_date, reverse=True)

# Generate HTML for news cards
news_html = ""
for item in items:
    news_html += f"""
    <div class="news-item">
      <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
      <p><em>{item['date']} — {item['source']}</em></p>
    </div>
    """

# Inject into base template
with open("base_template_news.html", "r", encoding="utf-8") as f:
    template = f.read()

start = template.find("<!-- START-NEWS-SECTION -->")
end = template.find("<!-- END-NEWS-SECTION -->") + len("<!-- END-NEWS-SECTION -->")
final_html = template[:start] + "<!-- START-NEWS-SECTION -->\n" + news_html + "\n" + template[end:]

with open("news.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"✅ news.html generated with {len(items)} items.")
