import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import streamlit as st
import plotly.express as px
import re
import json

def scrape_global_economy(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch {url}: {str(e)}")
        return None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the commodity name
    commodity_element = soup.find('h2', style="margin: 0; display: inline-block; font-size: 13px;")
    commodity = commodity_element.text.strip() if commodity_element else "Unknown Commodity"

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

    # Try to extract historical data from the graph image URL
    df = pd.DataFrame()
    graph_img = soup.find('img', id='graphImage')
    if graph_img:
        graph_url = graph_img['src']
        match = re.search(r'i=(\w+)$', graph_url)
        if match:
            indicator = match.group(1)
            historical_data_url = f"https://www.theglobaleconomy.com/api/graph_data_json3.php?period=0&country=world&indicator={indicator}"
            try:
                historical_data_response = requests.get(historical_data_url)
                historical_data_response.raise_for_status()
                historical_data = historical_data_response.json()
                df = pd.DataFrame(historical_data)
                df.columns = ['Year', 'Value']
            except (requests.RequestException, json.JSONDecodeError) as e:
                st.warning(f"Failed to fetch historical data: {str(e)}")
                # Fallback: Try to extract data from the page content
                df = extract_data_from_page(soup)

    return commodity, details, df

def extract_data_from_page(soup):
    # Look for a table with historical data
    table = soup.find('table', {'id': 'tableHTML'})
    if table:
        df = pd.read_html(str(table))[0]
        df.columns = ['Year', 'Value']
        return df
    else:
        st.warning("Could not find historical data table on the page.")
        return pd.DataFrame()

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
