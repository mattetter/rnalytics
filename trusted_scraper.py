from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import os
import datetime

# Set up Selenium driver
driver = webdriver.Chrome()

# Log into Trusted Health
driver.get("https://app.trustedhealth.com/login")
time.sleep(2)

email = driver.find_element(by=By.NAME, value="email")
password = driver.find_element(by=By.NAME, value="password")
email.send_keys("etterthefirst@gmail.com")
password.send_keys("1Fakeaccount.")
password.send_keys(Keys.RETURN)

# Wait for page to load
wait_time = 4
time.sleep(wait_time)

# Navigate to contracts page
driver.get("https://app.trustedhealth.com/matches/filtering")

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'JobCard')))




# Scroll to the bottom of the page

# Get the initial scroll height
last_height = driver.execute_script('return document.body.scrollHeight;')

# Define the scroll increment and wait time
scroll_increment = 500
wait_time = 3

while True:
    # Scroll to the bottom of the page
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    # Wait for new content to load
    time.sleep(wait_time)

    # Check if there is more content to load
    scroll_height = driver.execute_script('return document.body.scrollHeight;')
    if scroll_height == last_height:
        break
    last_height = scroll_height
    
# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Create the "trusted" directory if it doesn't exist
output_dir = 'trusted'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get the current date as a string
current_date = datetime.datetime.today().strftime('%Y-%m-%d')

# Save the results to a file in the "trusted" directory with the current date
output_file_path = os.path.join(output_dir, f'trusted_{current_date}.html')
with open(output_file_path, 'w') as f:
    f.write(str(soup))

# Send a message to console and close out driver
print(f"Webpage loaded to {output_file_path}")
driver.quit()