import sqlite3
import datetime
import re
from bs4 import BeautifulSoup


# Connect to the database
conn = sqlite3.connect('rnalytics.db')
c = conn.cursor()

# Create the contracts table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS trusted_contracts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              start_date TEXT,
              contract_length TEXT,
              shift_time TEXT,
              shift_type TEXT,
              facility_name TEXT,
              location TEXT,
              weekly_pay REAL,
              specialty TEXT,
              date_added DATE,
              date_last_seen DATE,
              num_positions INTEGER,
              agency TEXT,
              web_address TEXT,
              job_type TEXT)''')

# Open the html file and parse with beautiful soup
with open('trusted.html', 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')


# Find all job listings on the page
job_listings = soup.find_all('div', {'class': 'JobCard'})

# Loop through each job listing and extract information
for job_listing in job_listings:
    # Extract job title
    job_title = job_listing.find('div', {'class': 'JobCardFlex'}).text.strip()
    
    # extract start date, contract length, and shift from job title in format "Apr 03 (13 wks)·Night· 4x12"
    opening_paren_index = job_title.find("(")
    closing_paren_index = job_title.find(")")
    
    # Extract job link
    job_link = "https://app.trustedhealth.com"
    job_link += job_listing.find('a')['href'] 

    # Get the substring before the opening parentheses
    start_date = job_title[:opening_paren_index].strip()
    
    # Get the substring between the parentheses
    contract_length = job_title[opening_paren_index + 1:closing_paren_index].strip()
    
    # Extract shift info
    shift = job_title[closing_paren_index + 1:].strip().replace("·", "")
    shift_parts = shift.split()
    shift_type = shift_parts[0]
    shift_time = shift_parts[1]

    # Extract specialty
    specialty = job_listing.find('div', {'class': 'jsx-4257161705', 'style': 'margin-bottom: 0.5em;'}).text.strip()
    
    # Extract facility name
    facility_name = job_listing.find('div', {'class': 'JobCardFacilityName'}).text.strip()
    
    # Extract location
    location = job_listing.find('div', {'class': 'JobCardLocation'}).text.strip()
   
    # Extract pay rate
    weekly_pay_str = job_listing.find('div', {'class': 'JobCardPayLabel'}).text.strip()
    weekly_pay = float(re.sub(r'[^\d.]+', '', weekly_pay_str))
    
    # Check if a job listing with the same details exists in the database
    c.execute('''SELECT * FROM trusted_contracts 
                 WHERE start_date = ? AND contract_length = ? AND shift_time = ? 
                 AND shift_type = ? AND facility_name = ? AND location = ? AND weekly_pay = ? AND specialty = ?''', 
              (start_date, contract_length, shift_time, shift_type, facility_name, location, weekly_pay, specialty))
    existing_listing = c.fetchone()
    
    # The number of this position open
    num_positions = 1
    if existing_listing:
        # If the listing exists, check whether date_last_seen is today's date
        today = datetime.date.today()
        last_seen_date = datetime.datetime.strptime(existing_listing[10], "%Y-%m-%d").date()
        
        if last_seen_date == today:
            # If the date_last_seen is today's date, increment num_positions by 1
            num_positions = existing_listing[11] + 1
        
            # If the date_last_seen is not today's date, leave num_positions at 1
            
        # Update the existing listing with the new values
        c.execute('''UPDATE trusted_contracts SET date_last_seen = ?, num_positions = ? WHERE id = ?''',
                  (today.strftime("%Y-%m-%d"), num_positions, existing_listing[0]))

    else:
        # If the listing does not exist, add a new listing to the database
        date_added = datetime.date.today().strftime("%Y-%m-%d")
        c.execute('''INSERT INTO trusted_contracts (start_date, contract_length, shift_time, shift_type, 
                     facility_name, location, weekly_pay, specialty, date_added, date_last_seen, num_positions, agency, web_address, job_type) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (start_date, contract_length, shift_time, shift_type, facility_name, location, weekly_pay, specialty, date_added, date_added, num_positions, "Trusted", job_link, "Travel"))
    
# Commit the changes and close the database connection
conn.commit()
conn.close()
    