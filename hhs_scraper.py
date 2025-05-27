from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path

# Load raw.html from disk instead of downloading
raw_path = Path("raw.html")
if not raw_path.exists():
    print("❌ raw.html not found. You must run a request first or provide a known good version.")
    exit()

soup = BeautifulSoup(raw_path.read_text(encoding="utf-8"), "html.parser")

# Extract breach table
table = soup.find("table", {"id": "reportForm:reportListTable"})
if not table:
    print("❌ Could not find table in raw.html.")
    Path("breaches.html").write_text("<h1>Could not find breach table</h1><p>See <a href='raw.html'>raw.html</a>.</p>", encoding="utf-8")
    exit()

# Parse table rows
headers = [th.text.strip() for th in table.find_all("th")]
rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.text.strip() for td in tr.find_all("td")]
    if len(cells) == len(headers):
        rows.append(dict(zip(headers, cells)))

df = pd.DataFrame(rows)
print(f"✅ Parsed {len(df)} rows from raw.html")

df.to_csv("breaches.csv", index=False)
df.to_json("breaches.json", orient="records", indent=2)

# Create table HTML
table_html = df.to_html(classes="display", index=False, table_id="breach-table", border=0)

# Load template
template = Path("base_template.html").read_text(encoding="utf-8")
start = template.find("<!-- START-BREACH-SECTION -->")
end = template.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

# Inject HTML
html_block = f"""
<div class="toolbar">
  <div class="downloads">
    <a href="breaches.csv" download>⬇️ CSV</a>
    <a href="breaches.json" download>⬇️ JSON</a>
  </div>
  <div class="source">Source: local raw.html</div>
  <div class="updated">Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</div>
</div>

<div class="table-wrapper">
  {table_html}
</div>

<script>
  $(document).ready(function () {{
    $('#breach-table').DataTable({{
      responsive: true,
      pageLength: 25,
      dom: 'lfrtip'
    }});
  }});
</script>
"""

# Final render
final_html = template[:start] + "<!-- START-BREACH-SECTION -->\n" + html_block + "\n" + template[end:]
Path("breaches.html").write_text(final_html, encoding="utf-8")

print("✅ breaches.html generated using raw.html as source.")
