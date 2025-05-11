import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- Setup Headless Chrome for GitHub Actions ---
options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver installed in /usr/local/bin by GitHub Actions job
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# --- Load the HHS OCR Breach Portal ---
driver.get("https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf")
time.sleep(5)  # Wait for JavaScript to load

# Click the "Search" button to show all results
search_button = driver.find_element("id", "reportForm:searchButton")
search_button.click()
time.sleep(5)  # Wait for table to load

# --- Scrape the Results Table ---
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find("table", {"id": "reportForm:reportResultTable"})

if not table:
    raise Exception("Could not find results table. HHS portal may have changed.")

rows = table.find_all("tr")[1:]  # Skip header row

# Parse each row into a list of text values
data = []
for row in rows:
    columns = [col.text.strip() for col in row.find_all("td")]
    if columns:
        data.append(columns)

# Define expected headers
headers = [
    "Name of Covered Entity",
    "State",
    "Covered Entity Type",
    "Individuals Affected",
    "Type of Breach",
    "Location of Breached Information",
    "Date of Breach",
    "Date Added"
]

# Create a DataFrame
df = pd.DataFrame(data, columns=headers)

# --- Create and Save HTML Output ---
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
html = f"<h1>New Healthcare Breaches as of {timestamp}</h1>"
html += "<p>Source: <a href='https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf' target='_blank'>HHS OCR Breach Portal</a></p>"
html += df.head(20).to_html(index=False, border=1)

# Save to index.html for GitHub Pages
with open("index.html", "w") as f:
    f.write(html)

# Clean up
driver.quit()
