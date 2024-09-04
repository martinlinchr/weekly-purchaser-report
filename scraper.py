import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import streamlit as st
import plotly.express as px

def scrape_imf(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', {'id': 'mapJsonPayload'})
    if script_tag:
        data = eval(script_tag.string)
        df = pd.DataFrame(data['values']).T
        df.columns = ['Country'] + list(data['periods'])
        return df
    return None

def scrape_trading_economics(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table-hover'})
    if table:
        df = pd.read_html(str(table))[0]
        return df
    return None

def scrape_custom_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = pd.read_html(response.text)
    if tables:
        return tables[0]  # Return the first table found
    return None

def get_data(source, country=None):
    urls = {
        'Inflation': 'https://www.imf.org/external/datamapper/PCPIPCH@WEO/OEMDC/ADVEC/WEOWORLD',
        'Food Inflation': 'https://tradingeconomics.com/country-list/food-inflation',
        'Commodities': 'https://tradingeconomics.com/commodities'
    }
    
    if source == 'Inflation':
        df = scrape_imf(urls[source])
    elif source in ['Food Inflation', 'Commodities']:
        df = scrape_trading_economics(urls[source])
    else:
        df = scrape_custom_url(source)
    
    if df is not None and country:
        df = df[df['Country'].str.contains(country, case=False, na=False)]
    
    return df

def create_graph(df, country):
    if 'Country' in df.columns:
        df = df[df['Country'].str.contains(country, case=False, na=False)]
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 1:
        fig = px.line(df, x=df.columns[0], y=numeric_columns[1:], title=f'Data for {country}')
    else:
        st.warning("Not enough numeric data to create a graph.")
        fig = None
    
    return fig

if __name__ == "__main__":
    st.write("This is a module and should not be run directly.")
