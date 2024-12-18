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

LIST_FIELDS = "pl_name, image_url"

def fetch_exoplanets(offset=0, per_page=10, search_query=None):
    conn = sqlite3.connect('exoplanets.db')

    exclude_patterns = [
        '%via.placeholder.com%',
        '%Confirmed_exoplanets_by_methods_EPE.svg%',
        '%Example_exoplanet.jpg%'
    ]

    if search_query:
        query = f"""
            SELECT {LIST_FIELDS}
            FROM exoplanets
            WHERE (pl_name LIKE ? OR hostname LIKE ?)
              AND image_url IS NOT NULL
              AND image_url != ''
              AND {" AND ".join(["image_url NOT LIKE ?"] * len(exclude_patterns))}
            LIMIT ? OFFSET ?
        """
        params = [f"%{search_query}%", f"%{search_query}%"] + exclude_patterns + [per_page, offset]
    else:
        query = f"""
            SELECT {LIST_FIELDS}
            FROM exoplanets
            WHERE image_url IS NOT NULL
              AND image_url != ''
              AND {" AND ".join(["image_url NOT LIKE ?"] * len(exclude_patterns))}
            LIMIT ? OFFSET ?
        """
        params = exclude_patterns + [per_page, offset]

    df = pd.read_sql_query(query, conn, params=params)
    df['link'] = df['pl_name'].apply(lambda name: f'/exoplanet/{name}')

    conn.close()
    return df

def get_total_count(search_query=None):
    conn = sqlite3.connect('exoplanets.db')

    exclude_patterns = [
        '%via.placeholder.com%',
        '%Confirmed_exoplanets_by_methods_EPE.svg%',
        '%Example_exoplanet.jpg%'
    ]

    if search_query:
        query = f"""
            SELECT COUNT(*) as count
            FROM exoplanets
            WHERE (pl_name LIKE ? OR hostname LIKE ?)
              AND image_url IS NOT NULL
              AND image_url != ''
              AND {" AND ".join(["image_url NOT LIKE ?"] * len(exclude_patterns))}
        """
        params = [f"%{search_query}%", f"%{search_query}%"] + exclude_patterns
    else:
        query = f"""
            SELECT COUNT(*) as count
            FROM exoplanets
            WHERE image_url IS NOT NULL
              AND image_url != ''
              AND {" AND ".join(["image_url NOT LIKE ?"] * len(exclude_patterns))}
        """
        params = exclude_patterns

    count = pd.read_sql_query(query, conn, params=params).iloc[0]['count']
    conn.close()
    return count

@app.route("/")
def home():
    search_query = request.args.get('search', '')
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', default_per_page=10)
    total = get_total_count(search_query)
    exoplanets = fetch_exoplanets(offset=offset, per_page=per_page, search_query=search_query)
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('index.html', exoplanets=exoplanets, pagination=pagination, search_query=search_query, page = page)

@app.route("/exoplanet/<name>")
def exoplanet_detail(name):
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')

    conn = sqlite3.connect('exoplanets.db')
    query = "SELECT * FROM exoplanets WHERE pl_name = ?"
    df = pd.read_sql_query(query, conn, params=(name,))
    conn.close()

    if df.empty:
        # If no data found, pass None to the template
        return render_template('detail.html', exoplanet=None, page=page, search_query=search_query)
    
    # Convert the first row of df to a dictionary
    exoplanet = df.iloc[0].to_dict()

    return render_template('detail.html', exoplanet=exoplanet, page=page, search_query=search_query)

def open_browser():
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