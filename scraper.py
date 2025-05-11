import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
response = requests.get(url)

if response.status_code != 200:
    with open("index.html", "w") as f:
        f.write(f"<h1>Failed to load HHS OCR page</h1><p>Status Code: {response.status_code}</p>")
    exit()

soup = BeautifulSoup(response.content, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})

rows = table.find_all("tr")[1:]  # Skip header
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
html_output = f"<h1>New Healthcare Breaches as of {timestamp}</h1>"
html_output += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf'>HHS OCR Breach Portal</a></p>"
html_output += df.head(20).to_html(index=False)

with open("index.html", "w") as f:
    f.write(html_output)
