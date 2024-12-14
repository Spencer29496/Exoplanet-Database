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
            "prop": "images",
            "format": "json",
            "redirects": 1
        }
        r = requests.get(WIKI_API_ENDPOINT, params=params)
        r.raise_for_status()
        data = r.json()
        
        pages = data.get('query', {}).get('pages', {})
        for pageid, page in pages.items():
            if 'images' in page:
                for image in page['images']:
                    image_title = image['title']
                    if "planet" in image_title.lower() or "exoplanet" in image_title.lower() or "artist's impression" in image_title.lower():
                        return get_image_url(image_title)
        return None

    def get_image_url(image_title):
        params = {
            "action": "query",
            "titles": image_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }
        r = requests.get(WIKI_API_ENDPOINT, params=params)
        r.raise_for_status()
        data = r.json()
        
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            return page['imageinfo'][0]['url'] if 'imageinfo' in page else None
        return None

    # Direct attempt
    direct_image = get_image_from_title(planet_name)
    if direct_image:
        return direct_image

    # Try stripped name
    stripped_name = planet_name.replace(" b", "").strip()
    if stripped_name != planet_name:
        stripped_image = get_image_from_title(stripped_name)
        if stripped_image:
            return stripped_image

    # No image found
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