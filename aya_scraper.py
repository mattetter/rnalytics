"""This scrapes ayahealthcare.com for all nursing contracts. Parameters such as location can be modified at top of file.

    Returns:
        a directory of files containing the entire html of all pages scraped for nursing contracts.
    """
    
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
import time

# modify parameters 
STATE = "California"

#folder in which to save the html files inside of the current directory
folder_path = "./aya"

#TODO add functionalty to select individual specialties

def set_up_driver():
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox") # Bypass OS security model

    # This will automatically manage the chrome driver (download, update, path management, etc.)
    webdriver_service = Service(ChromeDriverManager().install())

    # Set the driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    return driver


# def set_up_driver():
#     driver = webdriver.Chrome()
#     return driver


def load_website(driver):
    driver.get("https://www.ayahealthcare.com/travel-nursing/travel-nursing-jobs/")


def select_location(driver, STATE):
    # Wait for the dropdown menu to be visible
    wait = WebDriverWait(driver, 10)
    specialty_wrapper = wait.until(EC.visibility_of_element_located((By.ID, "specialtyWrapper")))

    # Click the location to open the dropdown menu
    location_dropdown = driver.find_element(by=By.CLASS_NAME, value="select-btn--location")
    location_dropdown.click()

    # Wait for the state options to be visible
    wait.until(EC.visibility_of_element_located((By.ID, "locationListContainer")))

    # Select a state
    state_element = driver.find_element(By.XPATH, f'//a[contains(@class, "state") and text()="{STATE}"]')

    state_element.click()

    # Scroll down so that button is clickable
    driver.execute_script('window.scrollTo(0, 2000);')
    time.sleep(1)  # add a small delay to let the content load

    # wait for the search button to become clickable
    wait = WebDriverWait(driver, 10)
    # put it in a list because it has the same name and id as the other search button
    search_buttons = driver.find_elements(By.CLASS_NAME, "searchnow")

    # Click the "search now" button, which is second of two items on this list
    search_buttons[1].click()


# Select any or all nursing specialties from dropdown
def select_specialty(driver):
    
    # Click the specialty to open the dropdown menu
    specialty_button = driver.find_element(by=By.CLASS_NAME, value="select-btn--container")
    specialty_button.click()

    # Wait for the options to be visible
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "options")))

    # Click the Nursing element in the dropdown
    nursing_element = driver.find_element(By.XPATH, '//li/a[text()="Nursing"]')
    nursing_element.click()

    # Wait for the second dropdown to be visible
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "options--professions")))

    # Click the Registered Nurse element in the second dropdown
    registered_nurse_element = driver.find_element(By.XPATH, '//a[contains(@class, "profession") and text()="Registered Nurse"]')
    registered_nurse_element.click()

    # Wait for third dropdown 
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "options--expertises")))

    #TODO add functionalty to select individual specialties
    # Click 'all specialties' in the third dropdown
    expertise = driver.find_element(By.CLASS_NAME, "expertise--all")
    expertise.click()

    # wait for the search button to become clickable
    wait = WebDriverWait(driver, 10)
    search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "searchnow")))

    # Scroll down so that button is clickable
    driver.execute_script('window.scrollTo(0, 2000);')
    time.sleep(1)  # add a small delay to let the content load

    # Click the "search now" button
    search_button.click()


def navigate_pages(driver):
    
    # Scrape the first page
    html_content = ""

    # get the next button
    next_button = driver.find_element(By.XPATH, "//button[@id='nextButton']")
    
    # Counter for number of pages scraped since last save
    page_count = 1

    while next_button.is_enabled():
        
        # Save the contents of this page
        html_content += driver.page_source
        
        #  save the current content to a new file
        file_name = f"aya_{datetime.today().strftime('%Y-%m-%d')}_page_{page_count}.html"
        save_html_content(html_content, folder_path, file_name)
        html_content = ""

        # Find the next button, or break out of the loop if it doesn't exist
        try:
            next_button = driver.find_element(By.XPATH, "//button[@id='nextButton']")
        except NoSuchElementException:
            break
        
        if next_button.is_displayed() and next_button.is_enabled():
            # Scroll to the next button
            x = next_button.location["x"]
            y = next_button.location["y"]
            driver.execute_script(f"window.scrollTo({x}, {y - 500})")

            # Click the next button using WebDriverWait
            try:
                time.sleep(1)
                wait = WebDriverWait(driver, 10)  # Adjust the timeout value as needed (10 seconds here)
                wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, "button#nextButton.is-loading")))
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='nextButton']")))
                next_button.click()
            except ElementClickInterceptedException:
                print("Had to scroll again to click element.")
                
                # Try to scroll to button again, wait a little longer this time.
                x = next_button.location["x"]
                y = next_button.location["y"]
                driver.execute_script(f"window.scrollTo({x}, {y - 500})")
                time.sleep(3)
                
                # try clicking again
                next_button.click()

            time.sleep(1)  # wait for the page to load
            page_count += 1
        else:
            break
        
    # Save any remaining HTML content to a file
    if html_content:
        file_name = f"aya_{datetime.today().strftime('%Y-%m-%d')}_page_{page_count}.html"
        save_html_content(html_content, folder_path, file_name)

    return html_content


def save_html_content(html_content, directory, file_name):
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Save the HTML content to a file in the specified directory
    file_path = os.path.join(directory, file_name)
    with open(file_path, "w") as f:
        f.write(html_content)
    print(f"Data loaded to {file_path}")

def main():
    driver = set_up_driver()
    load_website(driver)
    #select_location(driver, STATE)
    select_specialty(driver)
    navigate_pages(driver)
    driver.quit()


if __name__ == "__main__":
    main()
