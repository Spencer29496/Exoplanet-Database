import sqlite3

def create_database():
    conn = sqlite3.connect('exoplanets.db')
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
    create_database()
    print("Database and table created successfully.")
