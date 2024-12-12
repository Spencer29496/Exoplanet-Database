import sqlite3

def inspect_columns():
    conn = sqlite3.connect('exoplanets.db')
    cursor = conn.cursor()
    
    # Get column names from the exoplanets table
    cursor.execute("PRAGMA table_info(exoplanets)")
    columns = cursor.fetchall()
    
    print("Columns in the exoplanets table:")
    for col in columns:
        print(f"{col[1]}")
    
    conn.close()

if __name__ == "__main__":
    inspect_columns()
