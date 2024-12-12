from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_args
import pandas as pd
import sqlite3

app = Flask(__name__)

FIELDS = "objectid, pl_name, pl_letter, hostid, hostname, disc_pubdate, disc_year, discoverymethod, disc_locale, disc_facility, disc_instrument, disc_telescope"

def fetch_exoplanets(offset=0, per_page=10, search_query=None):
    conn = sqlite3.connect('exoplanets.db')
    if search_query:
        query = f"SELECT {FIELDS} FROM exoplanets WHERE pl_name LIKE ? OR hostname LIKE ? LIMIT ? OFFSET ?"
        df = pd.read_sql_query(query, conn, params=(f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        query = f"SELECT {FIELDS} FROM exoplanets LIMIT ? OFFSET ?"
        df = pd.read_sql_query(query, conn, params=(per_page, offset))
    conn.close()
    return df

def get_total_count(search_query=None):
    conn = sqlite3.connect('exoplanets.db')
    if search_query:
        query = "SELECT COUNT(*) as count FROM exoplanets WHERE pl_name LIKE ? OR hostname LIKE ?"
        count = pd.read_sql_query(query, conn, params=(f"%{search_query}%", f"%{search_query}%")).iloc[0]['count']
    else:
        query = "SELECT COUNT(*) as count FROM exoplanets"
        count = pd.read_sql_query(query, conn).iloc[0]['count']
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
    conn = sqlite3.connect('exoplanets.db')
    query = f"SELECT {FIELDS} FROM exoplanets WHERE pl_name = ?"
    exoplanet = pd.read_sql_query(query, conn, params=(name,)).iloc[0]
    conn.close()
    return render_template('detail.html', exoplanet=exoplanet)

if __name__ == "__main__":
    app.run(debug=True)

