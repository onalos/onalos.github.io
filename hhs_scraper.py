import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path

# Fetch the live HHS breach portal page
url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Save raw HTML for debugging
Path("raw.html").write_text(response.text, encoding="utf-8")

# Extract the breach table
table = soup.find("table", {"id": "reportForm:reportListTable"})
if not table:
    Path("index.html").write_text("<h1>Could not find breach table</h1><p>Inspect <a href='raw.html'>raw.html</a> to debug.</p>", encoding="utf-8")
    exit()

# Parse the rows
rows = []
headers = [th.text.strip() for th in table.find_all("th")]
for row in table.find_all("tr")[1:]:
    cells = [td.text.strip() for td in row.find_all("td")]
    if len(cells) == len(headers):
        rows.append(dict(zip(headers, cells)))

df = pd.DataFrame(rows)
df.to_csv("breaches.csv", index=False)
df.to_json("breaches.json", orient="records", indent=2)

# Build HTML table
table_html = df.to_html(classes="display", index=False, table_id="breach-table", border=0)

# Load base template
template = Path("base_template.html").read_text(encoding="utf-8")
start = template.find("<!-- START-BREACH-SECTION -->")
end = template.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

# Build the toolbar content
toolbar = f"""
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

# Final HTML injection
final = template[:start] + "<!-- START-BREACH-SECTION -->\n" + toolbar + "\n" + template[end:]

# Write to index.html (you can rename if desired)
Path("breaches.html").write_text(final, encoding="utf-8")

print("✅ breaches.html generated.")
