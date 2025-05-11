import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Setup headless Chrome using Selenium Manager ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf")

# ✅ Wait for the Search button to appear
search_btn = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "reportForm:searchButton"))
)
search_btn.click()

# ✅ Wait for the results table to load
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "reportForm:reportResultTable"))
)

# --- Scrape table contents ---
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})
rows = table.find_all("tr")[1:]  # skip header

data = []
for row in rows:
    cols = [col.text.strip() for col in row.find_all("td")]
    if cols:
        data.append(cols)

columns = [
    "Name of Covered Entity", "State", "Covered Entity Type", "Individuals Affected",
    "Type of Breach", "Location of Breached Information", "Date of Breach", "Date Added"
]

df = pd.DataFrame(data, columns=columns)

# --- Output HTML ---
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html_output = f"<h1>New Healthcare Breaches as of {timestamp}</h1>"
html_output += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf'>HHS OCR Breach Portal</a></p>"
html_output += df.head(20).to_html(index=False)

with open("index.html", "w") as f:
    f.write(html_output)

driver.quit()
