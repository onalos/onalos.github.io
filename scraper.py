import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Setup headless Chrome using Selenium Manager ---
options = Options()
options.add_argument("--headless=new")  # newer headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)  # Selenium Manager handles the driver
driver.get("https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf")
time.sleep(5)  # Allow JS to load

# Click Search
search_btn = driver.find_element("id", "reportForm:searchButton")
search_btn.click()
time.sleep(5)

# Parse results
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

# Create HTML
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html_output = f"<h1>New Healthcare Breaches as of {timestamp}</h1>"
html_output += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf' target='_blank'>HHS OCR Breach Portal</a></p>"
html_output += df.head(20).to_html(index=False)

# Save HTML
with open("index.html", "w") as f:
    f.write(html_output)

driver.quit()
