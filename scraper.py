import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive",
}

# Fetch the page
response = requests.get(url, headers=headers)

# Save raw HTML for debugging
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(response.text)

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Dynamically find the correct breach table (has 8 columns)
candidate_tables = soup.find_all("table")
target_table = None

for table in candidate_tables:
    rows = table.find_all("tr")
    if not rows:
        continue
    header_cells = rows[0].find_all("th")
    if len(header_cells) == 8:
        target_table = table
        break

if not target_table:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>\n")
        f.write("<p>Inspect <a href='raw.html'>raw.html</a> to debug the table structure.</p>\n")
    exit()

# Extract rows from the table
rows = target_table.find_all("tr")[1:]  # skip header
data = []

for row in rows:
    cols = [col.get_text(strip=True) for col in row.find_all("td")]
    if cols and len(cols) == 8:
        data.append(cols)

# Define column names
columns = [
    "Name of Covered Entity", "State", "Covered Entity Type", "Individuals Affected",
    "Type of Breach", "Location of Breached Information", "Date of Breach", "Date Added"
]

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Parse and filter by Date Added (last 7 days)
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=7)
df_recent = df[df["Date Added"] >= cutoff].copy()

# Output HTML
timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

if df_recent.empty:
    html = f"<h1>No breach entries added in the last 7 days (as of {timestamp})</h1>"
else:
    html = f"<h1>Healthcare Breaches Added in the Last 7 Days</h1>\n"
    html += f"<p>As of {timestamp}</p>\n"
    html += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf'>HHS OCR Breach Portal</a></p>\n"
    html += df_recent.to_html(index=False, border=1)

# Save final output
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
