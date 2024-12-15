import sqlite3
import pandas as pd
import requests
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

WIKI_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"

def fetch_wikimedia_image_url(planet_name):
    def get_image_from_title(title):
        params = {
            "action": "query",
            "titles": title,
            "prop": "images",
            "format": "json",
            "redirects": 1
        }
        try:
            print(f"Fetching image for: {title}")
            r = requests.get(WIKI_API_ENDPOINT, params=params)
            r.raise_for_status()
            data = r.json()
            print(f"Response: {data}")

            pages = data.get('query', {}).get('pages', {})
            for page in pages.values():
                if 'images' in page:
                    for image in page['images']:
                        image_title = image['title'].lower()
                        print(f"Found image title: {image_title}")
                        if (title.lower() in image_title or
                            "diagram" in image_title or
                            "artwork" in image_title or
                            "versus" in image_title or
                            "artist" in image_title):
                            return get_image_url(image['title'])
        except requests.RequestException as e:
            print(f"Error fetching image for {title}: {e}")
        return None

    def get_image_url(image_title):
        params = {
            "action": "query",
            "titles": image_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }
        try:
            r = requests.get(WIKI_API_ENDPOINT, params=params)
            r.raise_for_status()
            data = r.json()

            pages = data.get('query', {}).get('pages', {})
            for page in pages.values():
                url = page['imageinfo'][0]['url'] if 'imageinfo' in page else None
                if url and url.startswith('http://'):
                    url = url.replace('http://', 'https://')
                return url
        except requests.RequestException as e:
            print(f"Error fetching image URL for {image_title}: {e}")
        return None

    image_url = get_image_from_title(planet_name)
    if image_url:
        return image_url

    print(f"No valid image found for {planet_name}, using placeholder.")
    return f"https://via.placeholder.com/300?text={urllib.parse.quote(planet_name)}+Image+Not+Found"

def fetch_wikipedia_summary(planet_name):
    title = planet_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"

    try:
        print(f"Fetching summary for: {planet_name}")
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if 'extract' in data:
                return data['extract']
    except requests.RequestException as e:
        print(f"Error fetching summary for {planet_name}: {e}")
    return None

def import_data(csv_file='nasa_exoplanet_data.csv'):
    data = pd.read_csv(csv_file)

    # Parallel fetching of image URLs and descriptions
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for fetching images
        image_futures = {executor.submit(fetch_wikimedia_image_url, planet): planet for planet in data['pl_name']}
        # Submit tasks for fetching descriptions
        summary_futures = {executor.submit(fetch_wikipedia_summary, planet): planet for planet in data['pl_name']}

        # Collect image results
        image_results = {}
        for future in as_completed(image_futures):
            planet = image_futures[future]
            try:
                image_results[planet] = future.result()
            except Exception as e:
                print(f"Error fetching image for {planet}: {e}")
                image_results[planet] = f"https://via.placeholder.com/300?text={urllib.parse.quote(planet)}+Image+Not+Found"

        # Collect summary results
        summary_results = {}
        for future in as_completed(summary_futures):
            planet = summary_futures[future]
            try:
                summary_results[planet] = future.result()
            except Exception as e:
                print(f"Error fetching summary for {planet}: {e}")
                summary_results[planet] = None

    # Assign the results to the DataFrame
    data['image_url'] = data['pl_name'].map(image_results)
    data['description'] = data['pl_name'].map(summary_results)

    # Connect to SQLite and write DataFrame in a batch
    conn = sqlite3.connect('exoplanets.db')
    data.to_sql('exoplanets', conn, if_exists='replace', index=False, chunksize=1000)
    conn.close()
    print("Data imported successfully with Wikimedia image URLs and Wikipedia descriptions.")

if __name__ == "__main__":
    import_data()