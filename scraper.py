import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
HHS_URL = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
DAYS_BACK = 7

# --- FETCH HTML ---
response = requests.get(HHS_URL, headers=HEADERS)
html = response.text

# Save raw HTML for debugging
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# --- PARSE TABLE ---
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

if not tbody:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1><p>Check <a href='raw.html'>raw.html</a></p>")
    exit()

rows = tbody.find_all("tr")
parsed_data = []

for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        parsed_data.append([
            cells[1].text.strip(),  # Name of Covered Entity
            cells[2].text.strip(),  # State
            cells[3].text.strip(),  # Entity Type
            cells[4].text.strip(),  # Individuals Affected
            cells[5].text.strip(),  # Breach Submission Date
            cells[6].text.strip(),  # Type of Breach
            cells[7].text.strip(),  # Location of Breached Info
        ])

# --- TO DATAFRAME ---
columns = [
    "Name of Covered Entity", "State", "Entity Type", "Individuals Affected",
    "Date Added", "Type of Breach", "Location of Breached Info"
]

df = pd.DataFrame(parsed_data, columns=columns)

# Convert "Date Added" column to datetime
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")

# Filter for breaches added in the last 7 days
now = datetime.utcnow()
cutoff = now - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# --- OUTPUT ---
timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")

if df_recent.empty:
    html_output = f"<h1>No breach entries in the last {DAYS_BACK} days (as of {timestamp})</h1>"
else:
    html_output = f"<h1>Healthcare Breaches in the Last {DAYS_BACK} Days</h1>"
    html_output += f"<p>As of {timestamp} — Source: <a href='{HHS_URL}'>HHS OCR Portal</a></p>"
    html_output += df_recent.to_html(index=False, border=1)

# Write to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
