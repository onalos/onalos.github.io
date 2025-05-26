import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}
DAYS_BACK = 30

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

rows = tbody.find_all("tr") if tbody else []
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
    table_rows += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

last_updated = datetime.utcnow().strftime("%B %d, %Y")

html = f"""
<div class="toolbar">
  <div class="downloads">
    📥 <a href="breaches.csv">CSV</a>
    📥 <a href="breaches.json">JSON</a>
  </div>
  <div class="source">
    🔎 Source: <a href="{url}" target="_blank">HHS OCR Breach Portal</a>
  </div>
</div>

<div class="updated">
  Last updated: <strong>{last_updated}</strong>
</div>

<div class="table-wrapper">
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
</div>

<script>
  $(document).ready(function () {{
    $('#breach-table').DataTable({{ pageLength: 25 }});
  }});
</script>
"""

with open("base_template.html", "r", encoding="utf-8") as f:
    template = f.read()

start = template.find("<!-- START-BREACH-SECTION -->")
end = template.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

new_html = template[:start] + "<!-- START-BREACH-SECTION -->\n" + html + "\n" + template[end:]

with open("breaches.html", "w", encoding="utf-8", errors="surrogatepass") as f:
    f.write(new_html)

print(f"✅ breaches.html generated with {len(df_recent)} entries on {last_updated}")
