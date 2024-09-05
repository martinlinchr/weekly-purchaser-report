import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import plotly.express as px

# Define regions
REGIONS = {
    'EU': ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden'],
    'Europe': ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican City'],
    'Asia': ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'China', 'Cyprus', 'Georgia', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan', 'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'],
    'USA': ['United States'],
    'BRICS': ['Brazil', 'Russia', 'India', 'China', 'South Africa'],
    'North America': ['Canada', 'Mexico', 'United States'],
    'South America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela'],
    'Australia': ['Australia'],
    'World': [],  # This will be handled separately
    'G20': ['Argentina', 'Australia', 'Brazil', 'Canada', 'China', 'France', 'Germany', 'India', 'Indonesia', 'Italy', 'Japan', 'Mexico', 'Russia', 'Saudi Arabia', 'South Africa', 'South Korea', 'Turkey', 'United Kingdom', 'United States', 'European Union'],
    'G7': ['Canada', 'France', 'Germany', 'Italy', 'Japan', 'United Kingdom', 'United States'],
    'Scandinavia': ['Denmark', 'Norway', 'Sweden', 'Finland', 'Iceland']
}

def scrape_global_economy(url, is_ranking=False, country_or_region=None):
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
    
    if is_ranking:
        return scrape_ranking_page(soup, country_or_region)
    else:
        return scrape_commodity_page(soup)

def scrape_ranking_page(soup, country_or_region):
    table = soup.find('table', {'id': 'benchmarkTable'})
    if not table:
        st.warning("Could not find ranking table on the page.")
        return None, None, None, None, None

    df = pd.read_html(str(table))[0]
    
    if country_or_region:
        if country_or_region in REGIONS:
            if country_or_region == 'World':
                # For 'World', we'll use the entire dataset
                pass
            else:
                df = df[df['Countries'].isin(REGIONS[country_or_region])]
        else:
            df = df[df['Countries'].str.contains(country_or_region, case=False, na=False)]
    
    if df.empty:
        st.warning(f"No data found for the selected country/region: {country_or_region}")
        return None, None, None, None, None

    indicator = soup.find('h2', style="margin: 0; display: inline-block; font-size: 13px;")
    indicator = indicator.text.strip() if indicator else "Unknown Indicator"

    if country_or_region in REGIONS:
        latest_value = df['Latest value'].mean()
        reference = df['Reference'].mode()[0] if not df['Reference'].empty else 'N/A'
    else:
        latest_value = df.iloc[0]['Latest value']
        reference = df.iloc[0]['Reference']

    details = {
        'country/region': country_or_region,
        'latest_value': f"{latest_value:.2f}",
        'reference': reference,
    }

    # We don't have graph URLs for ranking pages
    return indicator, details, df, None, None

def scrape_commodity_page(soup):
    # ... (rest of the function remains the same)

def scrape_trading_economics(url):
    # ... (rest of the function remains the same)

def extract_data_from_page(soup):
    # ... (rest of the function remains the same)

def get_data(source, is_ranking=False, country_or_region=None):
    if source == 'Trading Economics Commodities':
        return scrape_trading_economics('https://tradingeconomics.com/commodities')
    else:
        return scrape_global_economy(source, is_ranking, country_or_region)

def create_graph(df, title):
    # ... (rest of the function remains the same)

if __name__ == "__main__":
    st.write("This is a module and should not be run directly.")
