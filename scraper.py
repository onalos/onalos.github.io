# ---------- scraper.py ----------

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# HHS OCR Breach Portal
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
DAYS_BACK = 30

# Step 1: Fetch HHS page
response = requests.get(url, headers=headers)
html = response.text
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# Step 2: Parse HTML table
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})
if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>")
    exit()

rows = tbody.find_all("tr")
data = []
for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        data.append([
            cells[1].text.strip(),
            cells[2].text.strip(),
            cells[3].text.strip(),
            cells[4].text.strip(),
            cells[5].text.strip(),
            cells[6].text.strip(),
            cells[7].text.strip(),
        ])

columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]
df = pd.DataFrame(data, columns=columns)
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
breach_html = f"""
<!-- START-BREACH-SECTION -->
<h1>Healthcare Breaches - Last {DAYS_BACK} Days</h1>
<p>As of {timestamp}</p>
<p class="download-links">
  📅 <a href="breaches.csv">CSV</a> |
  📅 <a href="breaches.json">JSON</a> |
  🔎 Source: <a href="{url}" target="_blank">HHS OCR Breach Portal</a>
</p>
<table id="breach-table" class="display">
{df_recent.to_html(index=False, classes="display", border=0)}
</table>
<script>
  $(document).ready(function() {{
      $('#breach-table').DataTable({{ "pageLength": 25 }});
  }});
</script>
<!-- END-BREACH-SECTION -->
"""

# HTML base template with content anchors
try:
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = """
<html>
<head>
  <meta charset='UTF-8'>
  <title>ThreatPodium</title>
  <link rel='stylesheet' href='https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css'>
  <script src='https://code.jquery.com/jquery-3.7.0.min.js'></script>
  <script src='https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js'></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f8f9fa; color: #333; }}
    table.display {{ width: 100% !important; table-layout: auto; border-collapse: collapse; }}
    table.display th, table.display td {{ border: 1px solid #ddd; padding: 8px; max-width: 240px; word-break: break-word; }}
    table.display th {{ background-color: #2c3e50; color: white; text-align: left; }}
    table.display tr:nth-child(even) {{ background-color: #f2f2f2; }}
    table.display tr:hover {{ background-color: #f1f1f1; }}
  </style>
</head>
<body>
<!-- START-BREACH-SECTION --><!-- END-BREACH-SECTION -->
<!-- START-NEWS-SECTION --><!-- END-NEWS-SECTION -->
</body></html>
"""

start = content.find("<!-- START-BREACH-SECTION -->")
end = content.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")
new_content = content[:start] + breach_html + content[end:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_content)


# ---------- news_scraper.py ----------

import feedparser
from datetime import datetime, timedelta

RSS_URL = "https://www.bleepingcomputer.com/feed/"
KEYWORDS = [
    "hospital", "clinic", "healthcare", "medtech", "medical", "EMR", "ehr",
    "HHS", "pharma", "provider", "cyberattack", "ransomware", "data breach"
]

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

news_html = f"""
<!-- START-NEWS-SECTION -->
<h2>📰 Recent Healthcare Threat News</h2>
<p>As of {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | Source: <a href='{RSS_URL}'>BleepingComputer RSS</a></p>
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
