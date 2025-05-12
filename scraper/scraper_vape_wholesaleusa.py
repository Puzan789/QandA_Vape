import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class ProductScraper:
    """
    A class to scrape product information from a  website.
    """
    def __init__(self, base_url, max_pages=20, max_workers=8):
        self.base_url = base_url
        self.max_pages = max_pages
        self.max_workers = max_workers

    def get_all_product_links(self):
        all_links = []
        for page in range(1, self.max_pages + 1):
            url = f"{self.base_url}?p={page}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            products = soup.select('ol.products.list.items.product-items li.product-item a.product-item-link')
            if not products:
                break
            links = [a['href'] for a in products if a.has_attr('href')]
            all_links.extend(links)
        return all_links

    def fetch_product(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.select_one('h1.page-title')
        description = soup.select_one('div.product.attribute.description')
        stock = soup.select_one('div.stock.available')
        price = soup.select_one('span.price')
        image = soup.select_one('img.gallery-placeholder__image')
        more_info = soup.select_one('#additional tbody')
        return {
            "title": title.get_text(strip=True) if title else None,
            "description": description.get_text(strip=True) if description else None,
            "stock": stock.get_text(strip=True) if stock else None,
            "price": price.get_text(strip=True) if price else None,
            "image_url": image['src'] if image and image.has_attr('src') else None,
            "more_information": more_info.get_text(strip=True) if more_info else None,
        }

    def scrape(self, output_csv="products.csv"):
        product_links = self.get_all_product_links()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.fetch_product, product_links))
        cleaned_data = [r for r in results if r is not None]
        df = pd.DataFrame(cleaned_data)
        df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    scraper = ProductScraper("https://vapewholesaleusa.com/disposables", max_pages=5, max_workers=8) 
    scraper.scrape("vapewholesalesusa_data.csv")