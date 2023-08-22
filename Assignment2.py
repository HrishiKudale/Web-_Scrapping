import requests
from bs4 import BeautifulSoup
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.3'
}

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"

def scrape_amazon_page(url):
    products = []
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return products

    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.select(".s-result-item")
    for item in items:
        try:
            product_url = "https://www.amazon.in" + item.select_one('a.a-link-normal')['href']
            product_name = item.select_one('span.a-text-normal').text
            product_price = item.select_one('span.a-price-whole').text if item.select_one('span.a-price-whole') else "N/A"
            rating = item.select_one('span.a-icon-alt').text if item.select_one('span.a-icon-alt') else "N/A"
            num_reviews = item.select_one('span.a-size-base').text if item.select_one('span.a-size-base') else "N/A"
            
            products.append([product_url, product_name, product_price, rating, num_reviews])
        except Exception as e:
            print("Error:", e)

    return products

def scrape_product_details(product_url):
    response = requests.get(product_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page {product_url}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    description = soup.select_one('#productDescription p').text.strip() if soup.select_one('#productDescription p') else "N/A"
    asin = soup.select_one('span[data-asin]')['data-asin'] if soup.select_one('span[data-asin]') else "N/A"
    manufacturer = soup.select_one('#bylineInfo').text.strip() if soup.select_one('#bylineInfo') else "N/A"

    return {
        'Description': description,
        'ASIN': asin,
        'Manufacturer': manufacturer
    }

all_products = []

for i in range(1, 21):  # for 20 pages
    url = base_url + str(i)
    products_on_page = scrape_amazon_page(url)
    
    # For each product, get the details
    for product in products_on_page:
        product_details = scrape_product_details(product[0])
        all_products.append(product + [product_details['Description'], product_details['ASIN'], product_details['Manufacturer']])
        if len(all_products) >= 200:  # break after scraping 200 products
            break

    if len(all_products) >= 200:
        break

# Save to CSV
with open('amazon_200_products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Manufacturer'])
    writer.writerows(all_products)
