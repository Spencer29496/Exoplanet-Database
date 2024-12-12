import sqlite3

def create_database():
    conn = sqlite3.connect('exoplanets.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exoplanets (
        objectid INTEGER PRIMARY KEY,
        pl_name TEXT,
        hostname TEXT,
        orbital_period REAL,
        mass REAL,
        radius REAL,
        distance REAL,
        discoverymethod TEXT,
        discovery_year INTEGER              
    )
   ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and table created successfully.")