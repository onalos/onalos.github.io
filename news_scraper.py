import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

TEMPLATE_FILE = "base_template.html"
OUTPUT_FILE = "news.html"

# 📰 Replace this list with actual scraping or RSS parsing
news_items = [
    {
        "title": "Ransomware hits major hospital chain",
        "link": "https://example.com/article1",
        "date": "2025-06-01"
    },
    {
        "title": "Healthcare data leak exposes 500k patients",
        "link": "https://example.com/article2",
        "date": "2025-06-02"
    },
    {
        "title": "New threat actor targets patient portals",
        "link": "https://example.com/article3",
        "date": "2025-06-03"
    }
]

# Generate HTML for each news card
news_html = ""
for item in news_items:
    news_html += f"""
    <div class="news-item">
      <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
      <p><em>{item['date']}</em></p>
    </div>
    """

# Load base template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

start_marker = "<!-- START-NEWS-SECTION -->"
end_marker = "<!-- END-NEWS-SECTION -->"

start = template.find(start_marker)
end = template.find(end_marker) + len(end_marker)

if start == -1 or end == -1:
    raise ValueError("Missing START-NEWS-SECTION or END-NEWS-SECTION markers in base_template.html")

# Inject HTML between the markers
new_html = (
    template[:start]
    + start_marker
    + "\n" + news_html + "\n"
    + template[end:]
)

# Write the final page
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"✅ Generated {OUTPUT_FILE} with {len(news_items)} news items.")
