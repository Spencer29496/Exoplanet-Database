import sqlite3

def create_database():
    conn = sqlite3.connect('exoplanets.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exoplanets (
        id INTEGER PRIMARY KEY,
        name TEXT,
        host_star TEXT,
        orbital_period REAL,
        mass REAL,
        radius REAL,
        distance REAL,
        discovery_method TEXT,
        discovery_year INTEGER              
    )
   ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and table created successfully.")