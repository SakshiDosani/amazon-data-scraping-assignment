import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_product_listings(url):
    # Send a GET request to the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the product listings on the page
    listings = soup.find_all('div', {'data-component-type': 's-search-result'})

    # Iterate over the listings and extract the required information
    data = []
    for listing in listings:
        product_url = listing.find('a', {'class': 'a-link-normal'}).get('href')
        product_name = listing.find('span', {'class': 'a-size-medium'}).text.strip()
        product_price = listing.find('span', {'class': 'a-price-whole'}).text.strip()
        rating = listing.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
        num_reviews = listing.find('span', {'class': 'a-size-base'}).text.strip().replace(',', '')
        
               # Scrape additional product details
        product_details = scrape_product_details('https://www.amazon.in' + product_url)
        if product_details:
            description, asin, product_description, manufacturer = product_details
            data.append([product_url, product_name, product_price, rating, num_reviews,
                         description, asin, product_description, manufacturer])
        
        # Add a delay to prevent overwhelming the server
        time.sleep(1)

    return data

def scrape_product_details(url):
    # Send a GET request to the product URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
       # Scrape the required product details
    description_elem = soup.find('span', {'id': 'productTitle'})
    description = description_elem.text.strip() if description_elem else "N/A"

    asin_elem = soup.find('th', string='ASIN')
    asin = asin_elem.find_next_sibling('td').text.strip() if asin_elem else "N/A"

    product_description_elem = soup.find('div', {'id': 'productDescription'})
    product_description = product_description_elem.text.strip() if product_description_elem else "N/A"

    manufacturer_elem = soup.find('a', {'id': 'bylineInfo'})
    manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else "N/A"
    
    return [description, asin, product_description, manufacturer]

def main():
    base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
    num_pages = 20  # Number of pages to scrape
    data = []

    # Scrape each page of the product listings
    for page in range(1, num_pages + 1):
        url = base_url + str(page)
        page_data = scrape_product_listings(url)
        data.extend(page_data)

    # Save the scraped data to a CSV file
    with open('product_listings.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
                         'Description', 'ASIN', 'Product Description', 'Manufacturer'])
        writer.writerows(data)

if __name__ == '__main__':
    main()