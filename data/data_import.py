import sqlite3
import pandas as pd
import requests
import urllib.parse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

WIKI_SUMMARY_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def fetch_wikipedia_data(planet_name):
    """
    Fetches both the summary description and a thumbnail image for the given planet name.
    """
    title = f"{planet_name} (exoplanet)"
    url = f"{WIKI_SUMMARY_ENDPOINT}{urllib.parse.quote(title)}"

    description, image_url = None, None

    try:
        print(f"Fetching data from Wikipedia for: {title}")
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            description = data.get('extract')
            image_url = data.get('thumbnail', {}).get('source')
    except requests.RequestException as e:
        print(f"Error fetching Wikipedia data for {planet_name}: {e}")

    # Fallback if no specific exoplanet result
    if not description:
        print(f"No specific data for {title}, trying general search for: {planet_name}")
        url = f"{WIKI_SUMMARY_ENDPOINT}{urllib.parse.quote(planet_name)}"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                description = data.get('extract')
                image_url = data.get('thumbnail', {}).get('source')
        except requests.RequestException as e:
            print(f"Error fetching fallback data for {planet_name}: {e}")

    # Final fallback for the image
    if not image_url:
        image_url = f"https://via.placeholder.com/300?text={urllib.parse.quote(planet_name)}+Image+Not+Found"

    return description, image_url

def is_valid_image(image_url):
    """
    Checks if the image URL does not contain words related to constellations or diagrams.
    """
    exclusion_keywords = [
        # Common scientific terms
        "constellation", "diagram", "chart", "map", "illustration", "schematic",
        "graph", "plot", "curve", "velocity", "spectrum", "spectroscopy",
        "radial", "doppler", "wavelength", "lightcurve", "transit", "phase",
        "orbit", "motion", "astrometry", "periodogram", "time-series", "scatter",
        "lineplot", "histogram", "data", "analysis", "detection", "residual",
        "contour", "absorption", "emission", "frequency", "simulation", "model",
        "trajectory", "magnitude", "flux", "intensity", "errorbar", "timescale",
        "power", "distribution", "hist", "logarithm", "cross-section", "radar",
        "grid", "waveform", "noise", "precision", "accuracy", "fit", "measurement",
        "correlation", "calibration", "instrument", "function", "variation", "trend",
        "spectra", "offset", "axis", "scatterplot", "boxplot", "heatmap", "densityplot",
        "barplot", "polarplot", "surfaceplot", "diagrammatic", "visualization",
        "timeline", "fourier", "fft", "kinematics", "dynamics", "signal", "resonance",
        "phaseplot", "bode", "nyquist", "gain", "impulse", "stepresponse",
        
        # Additional visualization and analysis terms
        "wave", "gridlines", "contourplot", "matrix", "transformation", "vector",
        "field", "gradient", "isosurface", "topology", "morphology", "scattergram",
        "trendline", "deviation", "outlier", "confidence", "regression", "fitline",
        
        # Physics and astronomy related terms
        "redshift", "blueshift", "luminosity", "brightness", "magnitude", "lightcurve",
        "stellar", "orbital", "kinetic", "potential", "gravitational", "acceleration",
        "astrophysical", "cosmology", "radiation", "fluxdensity", "parallax",
        
        # Mathematical terms
        "derivative", "integral", "functionplot", "parametric", "polar", "cartesian",
        "complexplane", "vectorfield", "gradientfield", "equationplot", "matrixplot",
        "tensor", "eigenvalue", "eigenvector", "laplacian", "divergence", "curl",
        
        # Generic plot terms
        "x-axis", "y-axis", "z-axis", "legend", "label", "scale", "ticks", "gridline",
        "errorbars", "datapoint", "dataset", "fitcurve", "trendcurve", "overlay",
        
        # File types and image descriptions
        "svg", "diagram.jpg", "graph.png", "plot.jpg", "spectrum.png", "curve.png",
        "velocitygraph", "datagraph", "spectralplot", "motiondiagram", "timediagram",
        "orbitaldiagram", "analysischart"
    ]
    return not any(keyword in image_url.lower() for keyword in exclusion_keywords)

EXCLUDE_TERMS = [
    "spectroscopy", "TrES-3b", "14 Andromedae b", "OGLE-TR-56b", "18 Delphini b", "55 Cancri d", "TOI-1231 b", "Sun-like", "absolute magnitude"
]

def should_exclude_description(description):
    """
    Returns True if the description contains any of the specified exclusion terms.
    """
    if not description:
        return False
    return any(term.lower() in description.lower() for term in EXCLUDE_TERMS)

def import_data(csv_file='src/data/nasa_exoplanet_data.csv'):
    data = pd.read_csv(csv_file)

    # Parallel fetching of descriptions and images from Wikipedia summary
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_wikipedia_data, planet): planet for planet in data['pl_name']}

        results = {}
        for future in as_completed(futures):
            planet = futures[future]
            try:
                desc, img = future.result()
                # Filter criteria:
                # 1. Description must contain "exoplanet" or "extrasolar."
                # 2. Description must not contain any of the exclusion terms.
                # 3. Image URL must not contain keywords related to constellations or diagrams.
                if (desc and 
                    ("exoplanet" in desc.lower() or "extrasolar" in desc.lower()) and
                    not should_exclude_description(desc) and
                    is_valid_image(img)):
                    results[planet] = (desc, img)
                else:
                    results[planet] = (None, None)  # Exclude if criteria are not met
            except Exception as e:
                print(f"Error fetching data for {planet}: {e}")
                results[planet] = (None, None)

    # Filter out rows where description is None (meaning the criteria weren't met)
    data['description'] = data['pl_name'].apply(lambda p: results[p][0])
    data['image_url'] = data['pl_name'].apply(lambda p: results[p][1])
    data = data.dropna(subset=['description'])

    # Connect to SQLite and write DataFrame in a batch
    conn = sqlite3.connect('src/data/exoplanets.db')
    data.to_sql('exoplanets', conn, if_exists='replace', index=False, chunksize=1000)
    conn.close()
    print("Data imported successfully with filtered Wikipedia summaries and thumbnail images.")

if __name__ == "__main__":
    # if not in root directory, throw an error
    if os.path.dirname(__file__) != os.path.abspath('src'):
        raise ValueError("This script must be run from the root directory, not src/")

    # if csv file does not exist, throw an error
    if not os.path.exists('src/data/nasa_exoplanet_data.csv'):
        raise ValueError("CSV file does not exist, did you run the download_data.py script?")

    # if database file does not exist, throw an error
    if not os.path.exists('src/data/exoplanets.db'):
        raise ValueError("Database file does not exist, did you run the database_setup.py script?")

    print("Importing data...")
    import_data()