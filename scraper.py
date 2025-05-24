import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}
DAYS_BACK = 30

response = requests.get(url, headers=headers)
html = response.text
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})
if not tbody:
    with open("breaches.html", "w", encoding="utf-8") as f:
        f.write("<h1>Could not find breach table</h1>")
    exit()

rows = tbody.find_all("tr")
data = []
for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 8:
        data.append([cell.text.strip() for cell in cells[1:8]])

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

table_rows = ""
for _, row in df_recent.iterrows():
    table_rows += f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>"

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
breach_html = f"""
<!-- START-BREACH-SECTION -->
<h2>\ud83d\udcca Healthcare Breaches \u2014 Last {DAYS_BACK} Days</h2>
<p>As of {timestamp}</p>
<p class=\"download-links\">
  \ud83d\udcc5 <a href=\"breaches.csv\">CSV</a> |
  \ud83d\udcc5 <a href=\"breaches.json\">JSON</a> |
  \ud83d\udd0e Source: <a href=\"{url}\" target=\"_blank\">HHS OCR Breach Portal</a>
</p>
<table id=\"breach-table\" class=\"display\">
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

try:
    with open("base_template.html", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    raise Exception("Missing base_template.html. Please create it from ThreatPodium_Upgrade.")

start = content.find("<!-- START-BREACH-SECTION -->")
end = content.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")
new_content = content[:start] + breach_html + content[end:]

with open("breaches.html", "w", encoding="utf-8") as f:
    f.write(new_content)
