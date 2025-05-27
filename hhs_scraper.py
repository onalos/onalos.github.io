import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

Path("raw.html").write_text(response.text, encoding="utf-8")

table = soup.find("table", {"id": "reportForm:reportListTable"})
if not table:
    print("❌ Table not found in HHS response.")
    Path("breaches.html").write_text("<h1>Could not find breach table</h1><p>See <a href='raw.html'>raw.html</a>.</p>", encoding="utf-8")
    exit()

headers = [th.text.strip() for th in table.find_all("th")]
rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.text.strip() for td in tr.find_all("td")]
    if len(cells) == len(headers):
        rows.append(dict(zip(headers, cells)))

df = pd.DataFrame(rows)
print(f"✅ Found {len(df)} breach rows.")

if len(df) == 0:
    print("⚠️ Table structure is correct, but no data rows found.")
    Path("breaches.html").write_text("<h1>No data rows found in breach table.</h1><p>See <a href='raw.html'>raw.html</a>.</p>", encoding="utf-8")
    exit()

df.to_csv("breaches.csv", index=False)
df.to_json("breaches.json", orient="records", indent=2)

table_html = df.to_html(classes="display", index=False, table_id="breach-table", border=0)

template = Path("base_template.html").read_text(encoding="utf-8")
start = template.find("<!-- START-BREACH-SECTION -->")
end = template.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

html_block = f"""
<div class="toolbar">
  <div class="downloads">
    <a href="breaches.csv" download>⬇️ CSV</a>
    <a href="breaches.json" download>⬇️ JSON</a>
  </div>
  <div class="source">Source: <a href="{url}" target="_blank">{url}</a></div>
  <div class="updated">Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</div>
</div>

<div class="table-wrapper">
  {table_html}
</div>

<script>
  $(document).ready(function () {{
    $('#breach-table').DataTable({{
      responsive: true,
      pageLength: 25
    }});
  }});
</script>
"""

final_html = template[:start] + "<!-- START-BREACH-SECTION -->\n" + html_block + "\n" + template[end:]
Path("breaches.html").write_text(final_html, encoding="utf-8")

print("✅ breaches.html generated.")
