import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import plotly.express as px

def scrape_global_economy(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch {url}: {str(e)}")
        return None, None, None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the commodity/indicator name
    commodity_element = soup.find('h2', style="margin: 0; display: inline-block; font-size: 13px;")
    commodity = commodity_element.text.strip() if commodity_element else "Unknown Indicator"

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

    # Extract graph image URLs
    graph_imgs = soup.find_all('img', id='graphImage')
    recent_graph_url = None
    historical_graph_url = None
    
    if len(graph_imgs) >= 2:
        recent_graph_url = graph_imgs[0]['src']
        historical_graph_url = graph_imgs[1]['src']
    elif len(graph_imgs) == 1:
        recent_graph_url = graph_imgs[0]['src']

    # Try to extract historical data from the table
    df = extract_data_from_page(soup)

    return commodity, details, df, recent_graph_url, historical_graph_url

def scrape_trading_economics(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch {url}: {str(e)}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table table-hover'})
    
    if table:
        df = pd.read_html(str(table))[0]
        return "Commodities", df
    else:
        st.warning("Could not find commodities table on the page.")
        return None, None

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
    if source == 'Trading Economics Commodities':
        return scrape_trading_economics('https://tradingeconomics.com/commodities')
    else:
        return scrape_global_economy(source)

def create_graph(df, title):
    if df is not None and not df.empty:
        if 'Year' in df.columns and 'Value' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            df = df.dropna()
            
            fig = px.line(df, x='Year', y='Value', title=f'{title} - Historical Data')
            return fig
    return None

if __name__ == "__main__":
    st.write("This is a module and should not be run directly.")
