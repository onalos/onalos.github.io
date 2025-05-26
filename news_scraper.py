from datetime import datetime
import os

# Example mock news data
news_items = [
    {
        "title": "Ransomware hits major hospital chain",
        "link": "https://example.com/article1",
        "date": "June 1, 2025"
    },
    {
        "title": "Healthcare data breach affects 500k patients",
        "link": "https://example.com/article2",
        "date": "May 31, 2025"
    },
    {
        "title": "New threat actor targets patient portals",
        "link": "https://example.com/article3",
        "date": "May 30, 2025"
    }
]

news_html = ""
for item in news_items:
    news_html += f"""
    <div class="news-item">
      <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
      <p><em>{item['date']}</em></p>
    </div>
    """

# Load and inject into template
with open("base_template_news.html", "r", encoding="utf-8") as f:
    template = f.read()

start = template.find("<!-- START-NEWS-SECTION -->")
end = template.find("<!-- END-NEWS-SECTION -->") + len("<!-- END-NEWS-SECTION -->")
new_html = template[:start] + "<!-- START-NEWS-SECTION -->\n" + news_html + "\n" + template[end:]

with open("news.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"✅ news.html generated with {len(news_items)} items.")
