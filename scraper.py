import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import streamlit as st
import plotly.express as px
import re

def scrape_global_economy(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch {url}: {str(e)}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the commodity name
    commodity = soup.find('h2', style="margin: 0; display: inline-block; font-size: 13px;").text.strip()

    # Extract other details
    details = {}
    rows = soup.find_all('tr')
    for row in rows:
        th = row.find('th')
        td = row.find('th', style="font-weight:normal")
        if th and td:
            key = th.text.strip().replace('\xa0', '').lower()
            value = td.text.strip()
            details[key] = value

    # Extract historical data from the graph image URL
    graph_img = soup.find('img', id='graphImage')
    if graph_img:
        graph_url = graph_img['src']
        match = re.search(r'i=(\w+)$', graph_url)
        if match:
            indicator = match.group(1)
            historical_data_url = f"https://www.theglobaleconomy.com/api/graph_data_json3.php?period=0&country=world&indicator={indicator}"
            historical_data = requests.get(historical_data_url).json()
            df = pd.DataFrame(historical_data)
            df.columns = ['Year', 'Value']
        else:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    return commodity, details, df

def get_data(source):
    urls = {
        'Brent Oil Prices': 'https://www.theglobaleconomy.com/world/brent_oil_prices/',
        'Gold Prices': 'https://www.theglobaleconomy.com/world/gold_prices/',
    }
    
    if source in urls:
        return scrape_global_economy(urls[source])
    else:
        st.error(f"Unsupported data source: {source}")
        return None, None, None

def create_graph(df, title):
    if df is not None and not df.empty:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna()
        
        fig = px.line(df, x='Year', y='Value', title=f'{title} - Historical Data')
        return fig
    return None

if __name__ == "__main__":
    st.write("This is a module and should not be run directly.")
