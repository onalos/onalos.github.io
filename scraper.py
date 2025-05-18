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

# Save the full page for debugging
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(response.text)

# Parse with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})

if not table:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>\n")
        f.write("<p>Inspect <a href='raw.html'>raw.html</a> to debug.</p>\n")
    exit()

# Parse rows from the table
rows = table.find_all("tr")[1:]  # skip header
data = []

for row in rows:
    cols = [col.get_text(strip=True) for col in row.find_all("td")]
    if cols:
        data.append(cols)

# Define column names
columns = [
    "Name of Covered Entity", "State", "Covered Entity Type", "Individuals Affected",
    "Type of Breach", "Location of Breached Information", "Date of Breach", "Date Added"
]

# Convert to DataFrame
df = pd.DataFrame(data, columns=columns)

# Convert 'Date Added' column to datetime
df['Date Added'] = pd.to_datetime(df['Date Added'], format='%m/%d/%Y', errors='coerce')

# Filter for the last 7 days
now = datetime.utcnow()
cutoff = now - timedelta(days=7)
df_recent = df[df['Date Added'] >= cutoff].copy()

# Generate HTML output
timestamp = now.strftime('%Y-%m-%d %H:%M:%S UTC')

if df_recent.empty:
    html = f"<h1>No breach entries added in the last 7 days (as of {timestamp})</h1>"
else:
    html = f"<h1>Healthcare Breaches Added in the Last 7 Days</h1>\n"
    html += f"<p>As of {timestamp}</p>\n"
    html += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf'>HHS OCR Breach Portal</a></p>\n"
    html += df_recent.to_html(index=False, border=1)

# Save to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
