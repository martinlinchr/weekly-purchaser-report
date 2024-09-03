import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_website(url, data_selectors):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    scraped_data = {}
    for key, selector in data_selectors.items():
        element = soup.select_one(selector)
        scraped_data[key] = element.text.strip() if element else 'Not found'
    
    return scraped_data

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def run_scraper(websites):
    all_data = []
    for site in websites:
        data = scrape_website(site['url'], site['selectors'])
        data['url'] = site['url']
        all_data.append(data)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.csv"
    save_to_csv(all_data, filename)
    return all_data, filename
