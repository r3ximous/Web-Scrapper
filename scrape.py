import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# URL to scrape
url = "https://www.rit.edu/dubai/directory"
print("Starting the scraper...")

# Set up Chrome webdriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get(url)
print("Browser opened successfully")

# Click the "Load More" button 5 times with verification
for i in range(5):
    try:
        # Get current count of employees for verification
        current_count = len(driver.find_elements(By.CSS_SELECTOR, "div.views-row"))
        
        # Wait for button to be clickable
        load_more = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Load More')]"))
        )
        load_more.click()
        print(f"Clicked 'Load More' button ({i+1}/5)")
        
        # Verify new content was loaded
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.views-row")) > current_count
        )
        time.sleep(2)  # wait a bit for everything to render properly
    except Exception as e:
        print(f"Load More process stopped: {e}")
        break

# Get the page source after all content is loaded
print("Fetching complete HTML after loading all content")
html = driver.page_source

# Create BeautifulSoup object
print("Creating BeautifulSoup object")
soup = BeautifulSoup(html, 'html.parser')

# Extract employee information
employees = soup.find_all("div", class_="views-row")
print(f"Found {len(employees)} employee records to process")
data = []

for i, emp in enumerate(employees):
    # Extract name
    name_tag = emp.find("h3")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"
    
    # Extract title
    title_tag = emp.find("div", class_="views-field-field-title")
    if title_tag:
        title_content = title_tag.find("div", class_="field-content")
        title = title_content.get_text(strip=True) if title_content else ""
    else:
        title = ""
    
    # Extract email
    email_tag = emp.find("a", href=lambda href: href and "mailto:" in href)
    email = email_tag.get_text(strip=True) if email_tag else ""
    
    data.append({"Name": name, "Title": title, "Email": email})
    
    # Print progress occasionally
    if (i+1) % 30 == 0:
        print(f"Processed {i+1} employee records")

# Close the browser
driver.quit()
print("Browser closed")

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv("employees.csv", index=False)
print(f"Scraping completed. {len(data)} records stored in employees.csv")