import sqlite3
import pandas as pd
import requests
import urllib.parse

def fetch_wikimedia_image_url(planet_name):
    WIKI_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"

    def get_image_from_title(title):
        params = {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": 600,
            "format": "json",
            "redirects": 1
        }
        r = requests.get(WIKI_API_ENDPOINT, params=params)
        r.raise_for_status()
        data = r.json()

        pages = data.get('query', {}).get('pages', {})
        for pageid, page in pages.items():
            if pageid == "-1":
                continue
            if 'thumbnail' in page:
                return page['thumbnail']['source']
        return None

    # 1. Direct attempt
    direct_image = get_image_from_title(planet_name)
    if direct_image:
        return direct_image

    # 2. Try stripped name (remove trailing " b" or similar)
    stripped_name = planet_name.replace(" b", "").strip()
    if stripped_name != planet_name:
        stripped_image = get_image_from_title(stripped_name)
        if stripped_image:
            return stripped_image

    # 3. Search if direct fails
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": planet_name,
        "format": "json",
        "srlimit": 1
    }
    sr = requests.get(WIKI_API_ENDPOINT, params=search_params)
    sr.raise_for_status()
    search_data = sr.json()

    search_results = search_data.get('query', {}).get('search', [])
    if search_results:
        best_match_title = search_results[0]['title']
        search_image = get_image_from_title(best_match_title)
        if search_image:
            return search_image

    # 4. No image found
    return f"https://via.placeholder.com/300?text={urllib.parse.quote(planet_name)}+Image+Not+Found"


def import_data(csv_file='nasa_exoplanet_data.csv'):
    # Read CSV into DataFrame
    data = pd.read_csv(csv_file)

    # Fetch image URLs from Wikimedia
    data['image_url'] = data['pl_name'].apply(fetch_wikimedia_image_url)

    # Connect to SQLite and write DataFrame
    conn = sqlite3.connect('exoplanets.db')
    data.to_sql('exoplanets', conn, if_exists='replace', index=False)
    conn.close()
    print("Data imported successfully with Wikimedia image URLs.")


if __name__ == "__main__":
    import_data()
