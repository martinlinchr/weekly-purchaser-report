import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with the data
    table = soup.find('table', {'class': 'table table-striped table-hover table-condensed'})
    
    if not table:
        return None

    # Extract table headers
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Extract table rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        row = [td.text.strip() for td in tr.find_all('td')]
        if row:
            rows.append(row)
    
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
        df = scrape_website(url)
        if df is not None:
            all_data[key] = df
        else:
            print(f"Failed to scrape data for {key}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename) as writer:
        for key, df in all_data.items():
            df.to_excel(writer, sheet_name=key, index=False)
    
    print(f"Data saved to {filename}")
    return all_data, filename

if __name__ == "__main__":
    run_scraper()
