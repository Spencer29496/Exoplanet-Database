import sqlite3
import os

def create_database():
    conn = sqlite3.connect('src/data/exoplanets.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exoplanets (
        id INTEGER PRIMARY KEY,
        objectid TEXT,
        pl_name TEXT,
        pl_letter TEXT,
        hostid TEXT,
        hostname TEXT,
        disc_pubdate TEXT,
        disc_year INTEGER,
        discoverymethod TEXT,
        disc_locale TEXT,
        disc_facility TEXT,
        disc_instrument TEXT,
        disc_telescope TEXT,
        image_url TEXT DEFAULT NULL,
        description TEXT DEFAULT NULL  -- Added description field
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # if not in root directory, throw an error
    if os.path.dirname(__file__) != os.path.abspath('src'):
        raise ValueError("This script must be run from the root directory, not src/")
        
    # if csv file does not exist, throw an error
    if not os.path.exists('src/data/nasa_exoplanet_data.csv'):
        raise ValueError("CSV file does not exist, did you run the download_data.py script?")
    
    print("Creating database and table...")
    create_database()
    print("Database and table created successfully.")
