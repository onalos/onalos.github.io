import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}
DAYS_BACK = 30

# Step 1: Download page
response = requests.get(url, headers=headers)
html = response.text

# Step 2: Save raw HTML (for debugging if needed)
with open("raw.html", "w", encoding="utf-8") as f:
    f.write(html)

# Step 3: Parse HTML table
soup = BeautifulSoup(html, "html.parser")
tbody = soup.find("tbody", {"id": "ocrForm:reportResultTable_data"})

if not tbody:
    raise ValueError("Could not locate the HHS breach table.")

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

# Step 4: Filter by date
df["Date Added"] = pd.to_datetime(df["Date Added"], format="%m/%d/%Y", errors="coerce")
cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)
df_recent = df[df["Date Added"] >= cutoff].copy()

# Step 5: Export data files
df_recent.to_csv("breaches.csv", index=False)
df_recent.to_json("breaches.json", orient="records", indent=2)

# Step 6: Build HTML breach table
table_rows = ""
for _, row in df_recent.iterrows():
    table_rows += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

table_html = f"""
<div class="toolbar">
  <div class="downloads">
    📥 <a href="breaches.csv">CSV</a>
    📥 <a href="breaches.json">JSON</a>
  </div>
  <div class="source">
    🔎 Source: <a href="{url}" target="_blank">HHS OCR Breach Portal</a>
  </div>
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

# Step 7: Inject into base_template.html
with open("base_template.html", "r", encoding="utf-8") as f:
    base = f.read()

start = base.find("<!-- START-BREACH-SECTION -->")
end = base.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

if start == -1 or end == -1:
    raise ValueError("Missing START-BREACH-SECTION or END-BREACH-SECTION in base_template.html")

output = base[:start] + "<!-- START-BREACH-SECTION -->\n" + table_html + "\n" + base[end:]

with open("breaches.html", "w", encoding="utf-8", errors="surrogatepass") as f:
    f.write(output)
