import sqlite3
import pandas as pd

def import_data(csv_file='nasa_exoplanet_data.csv'):
    data = pd.read_csv(csv_file)
    data['description'] = 'No description available.' 
    conn = sqlite3.connect('exoplanets.db')
    data.to_sql('exoplanets', conn, if_exists='replace', index=False)
    conn.close()
    print("Data imported successfully.")

if __name__ == "__main__":
    import_data()