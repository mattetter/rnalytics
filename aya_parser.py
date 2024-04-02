from bs4 import BeautifulSoup
import concurrent.futures
import sqlite3
import multiprocessing
from itertools import chain
from datetime import datetime, timedelta
import os
import re
import cProfile

# select the date of the files to parse, default to today
DATE = datetime.today().strftime('%Y-%m-%d')


# Connect to the database
def create_db_and_table():
    conn = sqlite3.connect('contract_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS aya_contracts
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

    # Create a table for logging processed files
    c.execute('''CREATE TABLE IF NOT EXISTS processed_files
                 (file_name TEXT PRIMARY KEY,
                  processed_date DATE)''')
    return conn, c

# get all the files in the folder
def get_all_files(c, folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        if not has_been_processed(c, file_name):
            print(f"File {file_name} being added to list for processing.")
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".html"):
                created_date = datetime.fromtimestamp(os.path.getctime(file_path))
                files.append((file_path, created_date))
    return files


# Check if a file has been processed before
def has_been_processed(c, file_name):
    c.execute('SELECT * FROM processed_files WHERE file_name = ?', (file_name,))
    return c.fetchone() is not None


# Mark a file as processed
def mark_as_processed(c, file_name):
    processed_date = datetime.now().strftime('%Y-%m-%d')
    file_name = os.path.basename(file_name)  # Extract file name from path
    c.execute('INSERT INTO processed_files (file_name, processed_date) VALUES (?, ?)', (file_name, processed_date))


# get the last added date from the database
def get_last_added_date(c):
    c.execute('SELECT MAX(date_added) FROM aya_contracts')
    last_added_date = c.fetchone()[0]
    if last_added_date is not None:
        return datetime.strptime(last_added_date, '%Y-%m-%d')
    else:
        return None


# grab the aya files for a given date, default to today
def get_files_by_date(folder_path, DATE):
    date = str(DATE)
    print(date)
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            created_date = str(datetime.fromtimestamp(os.path.getctime(file_path)).date())
            if created_date == date:
                files.append(file_path)
    return files


# Open the html files and parse with beautiful soup
def parse_html_file(file_path):
    with open(file_path, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def extract_job_details(job_listing):
    # Extract job title
    job_title = job_listing.find('h2', {'class': 'ico-job-details ico-job-details--location'}).text.strip()

    try:
        # extract job type (travel vs permanent)
        words = job_title.split()
        job_type = words[0]
    except Exception as e:
        print(f"Error extracting job title/type: {e}")
        job_type = 'Unknown'

    # Extract location from job_title (string looks like this: 'Travel Echo Tech/Cardiac Sonographer Radiology / Cardiology job in Broomfield, CO - $2,846.42 to $3,009.86 weekly')
    location_pattern = r"job\s+in\s+([\w\s\.,'-]+)"

    location_match = re.search(location_pattern, job_title)

    if location_match:
        location = location_match.group(1)
    else:
        location = "Unknown"  # Assign a default value if the pattern does not match
        print(f"Error extracting location: {job_title}")
    try:
        # Extract job link
        job_link = job_listing.find('a')['href']
    except Exception as e:
        print(f"Error extracting job link: {e}")
        job_link = 'Unknown'

    try:
        # Extract specialty
        specialty = job_listing.find('span', {'class': 'ico-job-details ico-job-details--specialty'}).text.strip()
    except Exception as e:
        print(f"Error extracting specialty: {e}")
        specialty = 'Unknown'

    # Extract pay rate
    pay_element = job_listing.find('span', {'class': 'ico-job-details ico-job-details--pay'})

    if pay_element is not None:
        pay = pay_element.text.strip()
        pattern = r'\$([\d,]+(\.\d{2})?)'
        match = re.search(pattern, pay)
        weekly_pay = float(match.group(1).replace(',', ''))
    else:
        pay = "Unknown"  # Assign a default value if the element does not exist
        weekly_pay = None

    # Extract number openings for this position
    openings_element = job_listing.find('span', {'class': 'ico-job-details ico-job-details--openings'})
    # If number of openings not listed, assume 1
    if openings_element:
        openings_string = openings_element.text.strip()
    else:
        openings_string = '1'
    # Extract the integer value from the string
    openings = int(re.search(r'\d+', openings_string).group())

    try:
        # Extract schedule
        schedule = job_listing.find('span', {'class': 'ico-job-details ico-job-details--schedule'}).text.strip()
        # extract from that the type of shift e.g. '3x12' (days/week x hours/day)
        shift_time = schedule.split('-', 1)[0].strip()
        
        # extract shift_type (e.g. days, nights)
        start_time = schedule.split('-', 1)[1].strip().split()[1]
        
        # Convert the start_time string to a datetime object
        start_time_obj = datetime.strptime(start_time, "%H:%M")

        # Define day shift and night shift time ranges
        day_shift_start = datetime.strptime("05:00", "%H:%M")
        day_shift_end = datetime.strptime("18:00", "%H:%M")

        # Check if the start_time is within the day shift or night shift time range
        if day_shift_start <= start_time_obj <= day_shift_end:
            shift_type = 'days'
        else:
            shift_type = 'nights'
    except Exception as e:
        print(f"Error extracting schedule information: {e}")
        shift_time = 'Unknown'
        shift_type = 'Unknown'

    return {
        'job_title': job_title,
        'location': location,
        'job_link': job_link,
        'specialty': specialty,
        'weekly_pay': weekly_pay,
        'openings': openings,
        'shift_time': shift_time,
        'shift_type': shift_type,
        'job_type': job_type
    }


def extract_date_from_file_name(file_name):
    """Extracts the date from a file name in the format 'aya_{date}_page_{page}.html'."""
    date_string = file_name.split("_")[1]
    return datetime.strptime(date_string, '%Y-%m-%d')


# process the job listings, check for existing listings in the database, and add new listings to the database.
def process_job_listings(c, job_details, date_from_file):
    #print(f"Processing job listing: {job_details['job_title']}")

    # Check if a job listing with the same details exists in the database   
    current_date = date_from_file

    c.execute('''SELECT * FROM aya_contracts 
                WHERE shift_time = ? AND shift_type = ? AND location = ? AND weekly_pay = ? AND specialty = ? AND job_type = ?''', 
            (job_details['shift_time'], job_details['shift_type'], job_details['location'], job_details['weekly_pay'], job_details['specialty'], job_details['job_type']))
    existing_listing = c.fetchone()

    # Check if the existing_listing is not None and if the date_added is more than 3 months old
    if existing_listing:
        date_added_str = existing_listing[9]  # date_added is the 10th column in the table
        date_added = datetime.strptime(date_added_str, '%Y-%m-%d %H:%M:%S')

        date_difference = current_date - date_added

        if date_difference > timedelta(days=90):  # Check if the difference is more than 90 days (3 months)
            # assume actually a new listing if older than 90 days
            existing_listing = None

    # The number of this position open
    num_positions = job_details['openings']
    if existing_listing:
        # If the listing exists, check whether date_last_seen is today's date
        last_seen_date = datetime.strptime(existing_listing[10], '%Y-%m-%d %H:%M:%S')
        if last_seen_date == current_date:
            # If the date_last_seen is today's date, increment num_positions by 1
            num_positions += existing_listing[11]

        # Update the existing listing with the new values
        c.execute('''UPDATE aya_contracts SET date_last_seen = ?, num_positions = ? WHERE id = ?''',
                (current_date, num_positions, existing_listing[0]))

    else:
        # If the listing does not exist, add a new listing to the database
        date_added = date_from_file
        c.execute('''INSERT INTO aya_contracts (shift_time, shift_type, location, weekly_pay, specialty, date_added, date_last_seen, num_positions, agency, web_address, job_type) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (job_details['shift_time'], job_details['shift_type'], job_details['location'], job_details['weekly_pay'], job_details['specialty'], date_added, date_added, num_positions, "Aya", job_details['job_link'], job_details['job_type']))
    

    pass
    

def process_files(chunk):
    all_jobs_data = []
    for file_name, created_date in chunk:  # Unpack the tuple here
        try:
            with open(file_name, 'r') as f:
                print(f"extracting data from file: {file_name}")
                soup = BeautifulSoup(f, 'html.parser')
                job_listings = soup.find_all('div', {'class': 'card job'})
                date_from_file = extract_date_from_file_name(file_name)
                for job_listing in job_listings:
                    job_data = extract_job_details(job_listing)
                    all_jobs_data.append((file_name, job_data, date_from_file))
        except Exception as e:
            print(f"Error processing file {file_name}: {str(e)}")
    return all_jobs_data


def main():
    folder_path = './aya'
    conn, c = create_db_and_table()
    files = get_all_files(c, folder_path)
    print(f"Number of files to be processed: {len(files)}")

    # Divide the files into chunks
    num_cores = multiprocessing.cpu_count()
    chunks = [files[i::num_cores] for i in range(num_cores)]
    
    # Create a multiprocessing Pool and process the files in parallel
    with multiprocessing.Pool(num_cores) as pool:
        all_jobs_data = pool.map(process_files, chunks)

    # Flatten the list of lists
    all_jobs_data = list(chain.from_iterable(all_jobs_data))

    processed_files = set()  
    print(f"Number of job listings to be saved: {len(all_jobs_data)}"   )   
    for file_name, job_data, date_from_file in all_jobs_data:  # here job_data is the extracted job details
        # Here we pass the extracted job details to process_job_listings
        process_job_listings(c, job_data, date_from_file) 
        processed_files.add(file_name)

     # Commit changes to the database and mark files as processed
    for file_name in processed_files:
        mark_as_processed(c, file_name)
    conn.commit()

    conn.close()
    print("All new files added to database.")

#cProfile.run('main()')

if __name__ == '__main__':
    main()

