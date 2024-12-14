from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_args
import pandas as pd
import sqlite3
import webbrowser
import threading
import time
import sys
import os

app = Flask(__name__)

# Fields for the list view (excluding image_url and description)
LIST_FIELDS = "objectid, pl_name, pl_letter, hostid, hostname, disc_pubdate, disc_year, discoverymethod, disc_locale, disc_facility, disc_instrument, disc_telescope"

# Fields for the detail view (including image_url and description)
DETAIL_FIELDS = "objectid, pl_name, pl_letter, hostid, hostname, disc_pubdate, disc_year, discoverymethod, disc_locale, disc_facility, disc_instrument, disc_telescope, image_url, description"

def fetch_exoplanets(offset=0, per_page=10, search_query=None):
    conn = sqlite3.connect('exoplanets.db')
    placeholder_pattern = '%via.placeholder.com%'

    if search_query:
        query = f"""
            SELECT {LIST_FIELDS}
            FROM exoplanets
            WHERE (pl_name LIKE ? OR hostname LIKE ?)
              AND image_url IS NOT NULL
              AND image_url != ''
              AND image_url NOT LIKE ?
            LIMIT ? OFFSET ?
        """
        df = pd.read_sql_query(query, conn, params=(f"%{search_query}%", f"%{search_query}%", placeholder_pattern, per_page, offset))
    else:
        query = f"""
            SELECT {LIST_FIELDS}
            FROM exoplanets
            WHERE image_url IS NOT NULL
              AND image_url != ''
              AND image_url NOT LIKE ?
            LIMIT ? OFFSET ?
        """
        df = pd.read_sql_query(query, conn, params=(placeholder_pattern, per_page, offset))
    
    # Add clickable links for planet names
    df['pl_name'] = df['pl_name'].apply(lambda name: f'<a href="/exoplanet/{name}">{name}</a>')

    conn.close()
    return df

def get_total_count(search_query=None):
    conn = sqlite3.connect('exoplanets.db')
    placeholder_pattern = '%via.placeholder.com%'

    if search_query:
        query = """
            SELECT COUNT(*) as count
            FROM exoplanets
            WHERE (pl_name LIKE ? OR hostname LIKE ?)
              AND image_url IS NOT NULL
              AND image_url != ''
              AND image_url NOT LIKE ?
        """
        count = pd.read_sql_query(query, conn, params=(f"%{search_query}%", f"%{search_query}%", placeholder_pattern)).iloc[0]['count']
    else:
        query = """
            SELECT COUNT(*) as count
            FROM exoplanets
            WHERE image_url IS NOT NULL
              AND image_url != ''
              AND image_url NOT LIKE ?
        """
        count = pd.read_sql_query(query, conn, params=(placeholder_pattern,)).iloc[0]['count']
    
    conn.close()
    return count

@app.route("/")
def home():
    search_query = request.args.get('search', '')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', default_per_page=10)
    total = get_total_count(search_query)
    exoplanets = fetch_exoplanets(offset=offset, per_page=per_page, search_query=search_query)
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('index.html', tables=[exoplanets.to_html(classes='data', index=False, escape=False)], pagination=pagination, search_query=search_query)

@app.route("/exoplanet/<name>")
def exoplanet_detail(name):
    page = request.args.get('page', 1)
    search_query = request.args.get('search', '')
    
    conn = sqlite3.connect('exoplanets.db')
    query = f"SELECT {DETAIL_FIELDS} FROM exoplanets WHERE pl_name = ?"
    df = pd.read_sql_query(query, conn, params=(name,))
    conn.close()

    if df.empty:
        return render_template('detail.html', exoplanet=None, page=page, search=search_query)

    exoplanet = df.iloc[0]
    return render_template('detail.html', exoplanet=exoplanet, page=page, search=search_query)


def open_browser():
    """Open the Flask app in the default web browser (Chrome)."""
    time.sleep(1)
    webbrowser.get("C:/Program Files/Google/Chrome/Application/chrome.exe %s").open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    try:
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)