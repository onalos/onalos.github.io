import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# HHS OCR Breach Portal
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {
    "User-Agent": "Mozilla/5.0"
}
DAYS_BACK = 30

# Fetch breach data
response = requests.get(url, headers=headers)
html = response.text
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# Parse HTML
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

# Convert to DataFrame
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

# Format rows for HTML
table_rows = ""
for _, row in df_recent.iterrows():
    table_rows += f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>"

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
breach_html = f"""
<!-- START-BREACH-SECTION -->
<h2>📊 Healthcare Breaches — Last {DAYS_BACK} Days</h2>
<p>As of {timestamp}</p>
<p class="download-links">
  📥 <a href="breaches.csv">CSV</a> |
  📥 <a href="breaches.json">JSON</a> |
  🔎 Source: <a href="{url}" target="_blank">HHS OCR Breach Portal</a>
</p>
<table id="breach-table" class="display">
  <thead>
    <tr>
      <th>Name of Covered Entity</th>
      <th>State</th>
      <th>Entity Type</th>
      <th>Individuals Affected</th>
      <th>Date Added</th>
      <th>Type of Breach</th>
      <th>Location of Breached Info</th>
    </tr>
  </thead>
  <tbody>
    {table_rows}
  </tbody>
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

# Read or create index.html
try:
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = """
<html>
<head>
  <meta charset='UTF-8'>
  <title>ThreatPodium — Healthcare Cyber Threat Intelligence</title>
  <link rel='stylesheet' href='https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css'>
  <script src='https://code.jquery.com/jquery-3.7.0.min.js'></script>
  <script src='https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js'></script>
  <style>
    body { font-family: 'Segoe UI', sans-serif; margin: 2rem; background: #f7f9fb; color: #333; line-height: 1.6; }
    h2 { color: #2c3e50; border-bottom: 2px solid #ccc; padding-bottom: 0.3rem; }
    table.display th { background-color: #0077b6; color: white; }
    table.display tr:nth-child(even) { background-color: #f0f8ff; }
  </style>
</head>
<body>
<header>
  <h1>ThreatPodium</h1>
  <p>Your daily source for healthcare breach and threat intelligence.</p>
</header>
<div class="section" id="breach-section"> <!-- START-BREACH-SECTION --><!-- END-BREACH-SECTION --> </div>
<div class="section" id="news-section"> <!-- START-NEWS-SECTION --><!-- END-NEWS-SECTION --> </div>
<footer>
  &copy; 2025 ThreatPodium. Data sourced from HHS & trusted cybersecurity news.
</footer>
</body>
</html>
"""

# Replace breach section
start = content.find("<!-- START-BREACH-SECTION -->")
end = content.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")
new_content = content[:start] + breach_html + content[end:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_content)
