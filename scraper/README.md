# Vape Product Scraper & Attribute Extractor


## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Scraping Product Data

- **To scrape from vaperanger.com:**
  ```bash
  python scraper_vape_ranger.py
  ```
  This will save the scraped products to `vape_ranger_data.csv`.

- **To scrape from vapewholesaleusa.com:**
  ```bash
  python scraper_vape_wholesalesusa.py
  ```
  This will save the scraped products to `vapewholesalesusa_data.csv`.
## API Key Setup

Before running the extractor, set your GROQ API key as an environment variable by creating a .env file:

```bash
 GROQ_API_KEY=your_groq_api_key_here
```

Replace `your_groq_api_key_here` with your actual API key.
## Extracting Structured Attributes

To extract structured JSON data from the unstructured CSV:

1. Set the CSV file path in `AttributeExtractor.extract`.
2. Run the extractor script:
   ```bash
   python attribute_extractor.py
   ```
   The structured output will be saved in `structured_output.json`.

---

