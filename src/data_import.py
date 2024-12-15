import sqlite3
import pandas as pd
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

WIKI_SUMMARY_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def fetch_wikipedia_data(planet_name):
    """
    Fetches both the summary description and a thumbnail image for the given planet name
    using the Wikipedia summary endpoint.
    """

    title = planet_name.replace(" ", "_")
    url = f"{WIKI_SUMMARY_ENDPOINT}{urllib.parse.quote(title)}"

    description = None
    image_url = None

    try:
        print(f"Fetching data from Wikipedia summary for: {planet_name}")
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()

            # Extract the description (extract field)
            if 'extract' in data:
                description = data['extract']

            # Extract thumbnail image if available
            if 'thumbnail' in data and 'source' in data['thumbnail']:
                image_url = data['thumbnail']['source']
                if image_url.startswith('http://'):
                    image_url = image_url.replace('http://', 'https://')
        else:
            print(f"No Wikipedia page found for {planet_name} (status: {r.status_code}). Using placeholder image.")
    except requests.RequestException as e:
        print(f"Error fetching Wikipedia summary for {planet_name}: {e}")

    # Fallback if no image found
    if not image_url:
        image_url = f"https://via.placeholder.com/300?text={urllib.parse.quote(planet_name)}+Image+Not+Found"

    return description, image_url

def import_data(csv_file='nasa_exoplanet_data.csv'):
    data = pd.read_csv(csv_file)

    # Parallel fetching of descriptions and images from Wikipedia summary
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_wikipedia_data, planet): planet for planet in data['pl_name']}

        results = {}
        for future in as_completed(futures):
            planet = futures[future]
            try:
                desc, img = future.result()
                results[planet] = (desc, img)
            except Exception as e:
                print(f"Error fetching data for {planet}: {e}")
                # fallback if error
                results[planet] = (None, f"https://via.placeholder.com/300?text={urllib.parse.quote(planet)}+Image+Not+Found")

    # Assign the results to the DataFrame
    data['description'] = data['pl_name'].apply(lambda p: results[p][0])
    data['image_url'] = data['pl_name'].apply(lambda p: results[p][1])

    # Connect to SQLite and write DataFrame in a batch
    conn = sqlite3.connect('exoplanets.db')
    data.to_sql('exoplanets', conn, if_exists='replace', index=False, chunksize=1000)
    conn.close()
    print("Data imported successfully with Wikipedia summary and thumbnail images.")

if __name__ == "__main__":
    import_data()