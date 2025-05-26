import feedparser
from datetime import datetime
import html

# Define RSS feeds and sources
feeds = {
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "HealthITSecurity": "https://healthitsecurity.com/rss",
    "HelpNetSecurity": "https://www.helpnetsecurity.com/feed/",
    "HIPAA Journal": "https://www.hipaajournal.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Becker's Hospital Review": "https://www.beckershospitalreview.com/rss/rss.html",
    "CISA": "https://www.cisa.gov/news.xml"
}

# Keywords to filter for
keywords = [
    "health", "healthcare", "clinic", "patients", "hospital",
    "medical", "ehr", "pharma", "pharmaceutical", "drug"
]

# Match keyword
def is_relevant(text):
    return any(kw in text.lower() for kw in keywords)

# Parse feeds
items = []
for source, url in feeds.items():
    parsed = feedparser.parse(url)
    for entry in parsed.entries[:20]:
        text = f"{entry.get('title', '')} {entry.get('summary', '')}"
        if is_relevant(text):
            date = entry.get('published', 'Unknown')
            try:
                parsed_date = datetime(*entry.published_parsed[:6])
                date_str = parsed_date.strftime("%B %d, %Y")
            except:
                date_str = date

            items.append({
                "title": html.escape(entry.get("title", "No Title")),
                "link": entry.get("link", "#"),
                "date": date_str,
                "source": source
            })

# Sort by most recent
def parse_date(entry):
    try:
        return datetime.strptime(entry["date"], "%B %d, %Y")
    except:
        return datetime.min

items = sorted(items, key=parse_date, reverse=True)

# Generate news card HTML
news_html = ""
for item in items:
    news_html += f"""
    <div class="news-item">
      <h3><a href="{item['link']}" target="_blank" rel="noopener noreferrer">{item['title']}</a></h3>
      <p><em>{item['date']} — {item['source']}</em></p>
    </div>
    """

# Inject into base_template_news.html
with open("base_template_news.html", "r", encoding="utf-8") as f:
    template = f.read()

start = template.find("<!-- START-NEWS-SECTION -->")
end = template.find("<!-- END-NEWS-SECTION -->") + len("<!-- END-NEWS-SECTION -->")
new_html = template[:start] + "<!-- START-NEWS-SECTION -->\n" + news_html + "\n" + template[end:]

with open("news.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"✅ news.html generated with {len(items)} secure, filtered headlines.")
