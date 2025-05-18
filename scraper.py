import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

# URL of the HHS OCR breach portal
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"

# Headers to make the request look like it's coming from a real browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Number of days back to filter breach records (e.g., last 30 days)
DAYS_BACK = 30

# -----------------------------
# FETCH HTML CONTENT
# -----------------------------

# Make a GET request to the HHS portal
response = requests.get(url, headers=headers)
html = response.text

# Save raw HTML to file for debugging or manual inspection
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# -----------------------------
# PARSE THE BREACH TABLE
# -----------------------------

# Use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(html, "html.parser")

# The breach table is contained within a specific <tbody> tag
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

# Exit early if the breach table isn't found
if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1><p>Check <a href='raw.html'>raw.html</a></p>")
    exit()

# Extract table rows
rows = tbody.find_all("tr")
data = []

# Parse relevant data columns from each row
for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        data.append([
            cells[1].text.strip(),  # Name of Covered Entity
            cells[2].text.strip(),  # State
            cells[3].text.strip(),  # Entity Type
            cells[4].text.strip(),  # Individuals Affected
            cells[5].text.strip(),  # Date Added
            cells[6].text.strip(),  # Type of Breach
            cells[7].text.strip(),  # Location of Breached Info
        ])

# -----------------------------
# CREATE STRUCTURED DATAFRAME
# -----------------------------

# Define column names to match table structure
columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]

# Convert list of rows into a DataFrame
df = pd.DataFrame(data, columns=columns)

# Parse "Date Added" to datetime and filter for the last N days
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# -----------------------------
# SAVE CSV AND JSON OUTPUTS
# -----------------------------

df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

# -----------------------------
# GENERATE HTML OUTPUT
# -----------------------------

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# Start building the HTML document
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
    🔎 Source: <a href="https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf" target="_blank">HHS OCR Breach Portal</a>
  </p>
  <table id="breach-table" class="display">
"""

# Append the formatted DataFrame as an HTML table
html_output += df_recent.to_html(index=False, classes="display", border=0)

# Close out the HTML with a script to enable DataTables functionality
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

# Save final HTML output
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
