import sqlite3
import pandas as pd

def get_all_exoplanets():
    conn = sqlite3.connect('exoplanets.db')
    #cursor = conn.cursor()

    #cursor.execute("SELECT name, host_star FROM exoplanets")
    query = "SELECT pl_name, hostname, disc_year FROM exoplanets"
    df = pd.read_sql_query(query, conn)
    #rows = cursor.fetchall()

    #for row in rows:
    #    print(row)
    
    print(df)

    conn.close()

def get_exoplanets_by_discovery_method(method):
    conn = sqlite3.connect('exoplanets.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exoplanets WHERE discovery_method = ?", (method,))
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    print("All Exoplanets:")
    get_all_exoplanets

    print("\nExoplanets Discovered by Transit Method:")
    get_exoplanets_by_discovery_method('Transit')