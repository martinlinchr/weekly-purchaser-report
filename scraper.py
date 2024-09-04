import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import streamlit as st

def scrape_website(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        st.error(f"Failed to fetch {url}: {str(e)}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with the data
    table = soup.find('table', {'class': 'table table-striped table-hover table-condensed'})
    
    if not table:
        st.warning(f"No table found on {url}")
        return None

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Extract table rows
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

def run_scraper():
    urls = {
        'PMI': 'https://www.theglobaleconomy.com/rankings/pmi_composite/',
        'Inflation': 'https://www.theglobaleconomy.com/rankings/Inflation/',
        'Diesel Prices': 'https://www.theglobaleconomy.com/rankings/diesel_prices/'
    }
    
    all_data = {}
    for key, url in urls.items():
        st.info(f"Scraping data for {key}...")
        df = scrape_website(url)
        if df is not None and not df.empty:
            all_data[key] = df
            st.success(f"Successfully scraped data for {key}")
        else:
            st.error(f"Failed to scrape data for {key}")
    
    if not all_data:
        st.error("No data was successfully scraped.")
        return None, None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.xlsx"
    
    # Save to BytesIO object instead of a file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for key, df in all_data.items():
            df.to_excel(writer, sheet_name=key, index=False)
    
    st.success(f"Data prepared for {filename}")
    return all_data, output

if __name__ == "__main__":
    run_scraper()
