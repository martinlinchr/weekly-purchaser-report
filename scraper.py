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
    
    # Find the table with id 'benchmarkTable'
    table = soup.find('table', {'id': 'benchmarkTable'})
    
    if not table:
        st.warning(f"No table with id 'benchmarkTable' found on {url}")
        return None

    # Extract table headers
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    
    # Extract table rows
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        row = [td.text.strip() for td in tr.find_all('td')]
        if row:
            rows.append(row)
    
    if not rows:
        st.warning(f"No data rows found in table on {url}")
        return None

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)
    return df

# ... rest of the file remains the same
