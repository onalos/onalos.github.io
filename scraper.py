import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# Configuration
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
DAYS_BACK = 30

# Fetch HTML
response = requests.get(url, headers=headers)
html = response.text

# Save raw HTML for debugging
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# Parse and locate the table body
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1><p>Check <a href='raw.html'>raw.html</a></p>")
    exit()

# Extract rows
rows = tbody.find_all("tr")
parsed_data = []

for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        parsed_data.append([
            cells[1].text.strip(),
            cells[2].text.strip(),
            cells[3].text.strip(),
            cells[4].text.strip(),
            cells[5].text.strip(),
            cells[6].text.strip(),
            cells[7].text.strip(),
        ])

# Build DataFrame
columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]

df = pd.DataFrame(parsed_data, columns=columns)
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# Save CSV and JSON
df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

# HTML Header with DataTables
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
html_output = f"""
<html>
<head>
  <meta charset="UTF-8">
  <title>Healthcare Breaches - Last {DAYS_BACK} Days</title>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
  <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f8f9fa; }}
    h1 {{ color: #2c3e50; }}
    .download-links a {{ margin-right: 1em; }}
    table {{ background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
  </style>
</head>
<body>
  <h1>Healthcare Breaches - Last {DAYS_BACK} Days</h1>
  <p>As of {timestamp}</p>
  <p class="download-links">
    📥 <a href="breaches.csv">CSV</a> |
    📥 <a href="breaches.json">JSON</a> |
    🔎 Source: <a href="https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf" target="_blank">HHS OCR Breach Portal</a>
  </p>
  <table id="breach-table" class="display" style="width:100%">
"""

# Table Body
html_output += df_recent.to_html(index=False, classes="display", border=0)

# Close HTML
html_output += """
  </table>
  <script>
    $(document).ready(function() {
        $('#breach-table').DataTable({
            "pageLength": 25
        });
    });
  </script>
</body>
</html>
"""

# Save to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
