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

# Fetch and save raw HTML from HHS
response = requests.get(url, headers=headers)
html = response.text
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# Parse breach table
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})
if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>")
    exit()

# Extract rows
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

# Create DataFrame and filter
columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]
df = pd.DataFrame(data, columns=columns)
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# Save exports
df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

# Build breach section HTML
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
breach_html = f"""
<!-- START-BREACH-SECTION -->
<h1>Healthcare Breaches - Last {DAYS_BACK} Days</h1>
<p>As of {timestamp}</p>
<p class=\"download-links\">
  📥 <a href=\"breaches.csv\">CSV</a> |
  📥 <a href=\"breaches.json\">JSON</a> |
  🔎 Source: <a href=\"{url}\" target=\"_blank\">HHS OCR Breach Portal</a>
</p>
<table id=\"breach-table\" class=\"display\">
{df_recent.to_html(index=False, classes="display breach-table-html", border=0)}
</table>
<script>
  $(document).ready(function() {{
    if (!$.fn.dataTable.isDataTable('#breach-table')) {{
      $('#breach-table').DataTable({{ "pageLength": 25 }});
    }}
  }});
</script>
<!-- END-BREACH-SECTION -->
"""

# Replace breach section in index.html
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
