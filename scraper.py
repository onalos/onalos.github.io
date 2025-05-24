import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

# HHS OCR Breach Portal
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"

# Browser-like headers for request
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# How many days back to show
DAYS_BACK = 30

# -----------------------------
# STEP 1: FETCH HHS HTML
# -----------------------------
response = requests.get(url, headers=headers)
html = response.text

# Save raw response to debug file
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# -----------------------------
# STEP 2: PARSE THE BREACH TABLE
# -----------------------------
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

# Exit if table is not found
if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1><p>Check <a href='raw.html'>raw.html</a></p>")
    exit()

# Parse each row of the table
rows = tbody.find_all("tr")
data = []

for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        data.append([
            cells[1].text.strip(),  # Name
            cells[2].text.strip(),  # State
            cells[3].text.strip(),  # Entity Type
            cells[4].text.strip(),  # Individuals Affected
            cells[5].text.strip(),  # Date Added
            cells[6].text.strip(),  # Type of Breach
            cells[7].text.strip(),  # Location
        ])

# -----------------------------
# STEP 3: STRUCTURE & FILTER
# -----------------------------
columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]

df = pd.DataFrame(data, columns=columns)
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# Save CSV and JSON for reuse
df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

# -----------------------------
# STEP 4: BUILD HTML OUTPUT
# -----------------------------
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
    body {{
      font-family: Arial, sans-serif;
      margin: 2rem;
      background: #f8f9fa;
      color: #333;
    }}
    h1 {{
      color: #2c3e50;
    }}
    .download-links a {{
      margin-right: 1em;
    }}
    table.display {{
      width: 100% !important;
      table-layout: auto;
      background: white;
      border-collapse: collapse;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      word-wrap: break-word;
    }}
    table.display th,
    table.display td {{
      border: 1px solid #ddd;
      padding: 8px;
      vertical-align: top;
      max-width: 240px;
      word-break: break-word;
    }}
    table.display th {{
      background-color: #2c3e50;
      color: white;
      text-align: left;
    }}
    table.display tr:nth-child(even) {{
      background-color: #f2f2f2;
    }}
    table.display tr:hover {{
      background-color: #f1f1f1;
    }}
  </style>
</head>
<body>
  <h1>Healthcare Breaches - Last {DAYS_BACK} Days</h1>
  <p>As of {timestamp}</p>
  <p class="download-links">
    📥 <a href="breaches.csv">CSV</a> |
    📥 <a href="breaches.json">JSON</a> |
    🔎 Source: <a href="{url}" target="_blank">HHS OCR Breach Portal</a>
  </p>
  <table id="breach-table" class="display">
"""

# Add table of breaches
html_output += df_recent.to_html(index=False, classes="display", border=0)

# Close table and add DataTables JS
html_output += """
  </table>
  <script>
    $(document).ready(function() {
        $('#breach-table').DataTable({
            "pageLength": 25
        });
    });
  </script>
"""

# -----------------------------
# STEP 5: APPEND NEWS SECTION IF EXISTS
# -----------------------------
try:
    with open("news.html", "r", encoding="utf-8") as news_file:
        news_section = news_file.read()
    html_output += "<hr>" + news_section
except FileNotFoundError:
    html_output += "<hr><p><em>No news content found.</em></p>"

# Close HTML
html_output += """
</body>
</html>
"""

# Write full output to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
