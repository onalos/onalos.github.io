import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

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

response = requests.get(url, headers=headers)

# ✅ Save raw HTML for inspection
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(response.text)

# ✅ Try to parse the page
soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})

if not table:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>\n")
        f.write("<p>Inspect <a href='raw.html'>raw.html</a> to debug.</p>\n")
    exit()

# ✅ Parse and write breach table to index.html
rows = table.find_all("tr")[1:]  # skip header
data = []

for row in rows:
    cols = [col.get_text(strip=True) for col in row.find_all("td")]
    if cols:
        data.append(cols)

columns = [
    "Name of Covered Entity", "State", "Covered Entity Type", "Individuals Affected",
    "Type of Breach", "Location of Breached Information", "Date of Breach", "Date Added"
]

df = pd.DataFrame(data, columns=columns)

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html = f"<h1>New Healthcare Breaches as of {timestamp}</h1>\n"
html += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf'>HHS OCR Breach Portal</a></p>\n"
html += df.head(20).to_html(index=False)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
