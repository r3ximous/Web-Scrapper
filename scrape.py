import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Step 1: Use Selenium to open the URL and click "Load More" 5 times
url = "https://www.rit.edu/dubai/directory"

# Set up Chrome webdriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get(url)

# Click the "Load More" button 5 times (each click loads 30 more employees)
for i in range(5):
    try:
        # Wait for the button to be clickable; adjust the XPath if necessary based on the page structure
        load_more = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Load More')]"))
        )
        load_more.click()
        time.sleep(2)  # wait a bit after clicking for new content to load
    except Exception as e:
        print(f"Error during clicking 'Load More' on iteration {i + 1}: {e}")
        break

# Step 2: Use Requests to fetch the page HTML.
# To simulate the updated browser session, transfer cookies from Selenium to the Requests session.
session = requests.Session()
for cookie in driver.get_cookies():
    session.cookies.set(cookie['name'], cookie['value'])

driver.quit()  # close the selenium browser

response = session.get(url)
html = response.text

# Step 3: Use BeautifulSoup to extract names, titles, and emails of employees.
soup = BeautifulSoup(html, 'html.parser')

# Assumption: Each employee info is contained in an element with class "views-row"
employees = soup.find_all("div", class_="views-row")
data = []

for emp in employees:
    # Extract the employee name; adjust the tag and class based on actual page structure.
    name_tag = emp.find("h3")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"
    
    # Extract the title; note that some employees may have missing titles.
    # Adjust the tag/class as per the actual structure.
    title_tag = emp.find("div", class_="views-field-field-title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    # Extract the email: look for a link with href containing "mailto:"
    email_tag = emp.find("a", href=lambda href: href and "mailto:" in href)
    email = email_tag.get_text(strip=True) if email_tag else ""
    
    data.append({"Name": name, "Title": title, "Email": email})

# Step 4: Use Pandas to store the scraped data into a CSV file.
df = pd.DataFrame(data)
df.to_csv("employees.csv", index=False)
print("Scraping completed. Data stored in employees.csv")