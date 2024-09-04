import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
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
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with id 'tableHTML'
    table = soup.find('table', {'id': 'tableHTML'})
    
    if not table:
        st.warning(f"No table with id 'tableHTML' found on {url}")
        return None

    # Extract table headers and rows
    headers = [th.text.strip() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        row = [td.text.strip() for td in tr.find_all('td')]
        if row:
            rows.append(row)
    
    if not rows:
        st.warning(f"No data rows found in table on {url}")
        return None

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)
    return df

def get_data(source):
    urls = {
        'Brent Oil Prices': 'https://www.theglobaleconomy.com/world/brent_oil_prices/',
        'Gold Prices': 'https://www.theglobaleconomy.com/world/gold_prices/',
    }
    
    if source in urls:
        df = scrape_global_economy(urls[source])
    else:
        st.error(f"Unsupported data source: {source}")
        return None
    
    return df

def create_graph(df):
    if df is not None and not df.empty:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna()
        
        fig = px.line(df, x='Year', y='Value', title=f'Historical Data')
        return fig
    return None

if __name__ == "__main__":
    st.write("This is a module and should not be run directly.")
