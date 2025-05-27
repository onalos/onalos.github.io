import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path

url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
headers = {"User-Agent": "Mozilla/5.0"}
table = None
source_note = ""

# Attempt live request
try:
    print("🌐 Fetching live breach report...")
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    Path("raw.html").write_text(response.text, encoding="utf-8")

    table = soup.find("table", {"id": "reportForm:reportListTable"})
    if table:
        source_note = f"Source: <a href='{url}' target='_blank'>{url}</a> (live scrape)"
    else:
        raise ValueError("Live scrape failed to find table.")
except Exception as e:
    print(f"⚠️ Live scrape failed: {e}")
    # Fallback to raw.html
    try:
        print("📂 Falling back to raw.html...")
        soup = BeautifulSoup(Path("raw.html").read_text(encoding="utf-8"), "html.parser")
        table = soup.find("table", {"id": "reportForm:reportListTable"})
        source_note = "Source: raw.html fallback"
    except Exception as fallback_error:
        print("❌ Fallback to raw.html also failed.")
        Path("breaches.html").write_text("<h1>Could not load breach table from HHS or raw.html</h1>", encoding="utf-8")
        exit()

# Extract rows
headers = [th.text.strip() for th in table.find_all("th")]
rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.text.strip() for td in tr.find_all("td")]
    if len(cells) == len(headers):
        rows.append(dict(zip(headers, cells)))

df = pd.DataFrame(rows)
print(f"✅ Parsed {len(df)} breach rows.")

df.to_csv("breaches.csv", index=False)
df.to_json("breaches.json", orient="records", indent=2)
table_html = df.to_html(classes="display", index=False, table_id="breach-table", border=0)

# Load base template
template = Path("base_template.html").read_text(encoding="utf-8")
start = template.find("<!-- START-BREACH-SECTION -->")
end = template.find("<!-- END-BREACH-SECTION -->") + len("<!-- END-BREACH-SECTION -->")

# Toolbar and table injection
toolbar_html = f"""
<div class="toolbar">
  <div class="downloads">
    <a href="breaches.csv" download>⬇️ CSV</a>
    <a href="breaches.json" download>⬇️ JSON</a>
  </div>
  <div class="source">{source_note}</div>
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

# Final HTML output
final_html = template[:start] + "<!-- START-BREACH-SECTION -->\n" + toolbar_html + "\n" + template[end:]
Path("breaches.html").write_text(final_html, encoding="utf-8")

print("✅ breaches.html generated (using live scrape or raw.html fallback).")
