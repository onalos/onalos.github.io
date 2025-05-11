import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

# Setup headless browser for GitHub Actions
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf")
time.sleep(5)

# Click Search
driver.find_element("id", "reportForm:searchButton").click()
time.sleep(5)

# Scrape results
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})
rows = table.find_all("tr")[1:]  # skip header

data = []
for row in rows:
    cols = [td.text.strip() for td in row.find_all("td")]
    if cols:
        data.append(cols)

columns = [
    "Name of Covered Entity", "State", "Covered Entity Type", "Individuals Affected",
    "Type of Breach", "Location of Breached Information", "Date of Breach", "Date Added"
]
df = pd.DataFrame(data, columns=columns)
driver.quit()

# Save as HTML
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html_output = f"<h1>New Healthcare Breaches @ {timestamp}</h1>\n"
html_output += df.head(20).to_html(index=False)

with open("index.html", "w") as f:
    f.write(html_output)
