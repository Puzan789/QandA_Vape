import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class ProductScrapers:
    """
    A class to scrape product information from a website.
    """
    def __init__(self, base_url, max_pages=20, max_workers=8):
        self.base_url = base_url
        self.max_pages = max_pages
        self.max_workers = max_workers

    def get_all_product_links(self):
        all_links = []
        for page in range(1, self.max_pages + 1):
            url = f"{self.base_url}?page={page}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            links = [a['href'] for a in soup.select('[data-product] a[href]')]
            if not links:
                break
            all_links.extend(links)
        return all_links

    def fetch_product(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.select_one('title')
        desc = " ".join(li.get_text(strip=True) for li in soup.select("div.rte li"))
        image = soup.select_one('figure.productView-image a')
        return {
            "title": title.get_text(strip=True) if title else None,
            "description": desc if desc else None,
            "image_url": image['href'] if image else None,
        }

    def scrape(self, output_csv="products1.csv"):
        product_links = self.get_all_product_links()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.fetch_product, product_links))
        cleaned_data = [r for r in results if r is not None]
        df = pd.DataFrame(cleaned_data)
        df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    op = ProductScrapers("https://vaperanger.com/disposable-vapes/", max_pages=10)
    op.scrape("vaperanger_data.csv")