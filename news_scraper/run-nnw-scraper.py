import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper_modules.nnw_scraper.scraper import get_articles as nnw_extractor
from data_processor.processor import DataProcessor
from cms_integration.integrator import post_article

# Set up logging
logging.basicConfig(filename='nnw_scraper.log', level=logging.INFO, format='%(asctime)s %(message)s')

def run_nnw_scraper():
    nnw_base_url = "https://www.naplesnews.com"

    nnw_articles = nnw_extractor(nnw_base_url)
    raw_data = []

    for article in nnw_articles:
        content = article
        if content is not None and 'title' in content:  # Check if 'title' key exists
            # If 'posted_date' key doesn't exist, add it with the current timestamp
            if 'posted_date' not in content:
                content['posted_date'] = datetime.now().isoformat()
            logging.info(f"Content: {content}")
            raw_data.append(content)

            # Get the HTML of the article
            response = requests.get(content['link_url'])
            soup = BeautifulSoup(response.text, 'html.parser')
            logging.info(f"Article HTML: {soup.prettify()}")  # Log the full HTML of the article page

    logging.info(f"Raw Data: {raw_data}")

    logging.info("Processing data...")
    processor = DataProcessor(raw_data)
    structured_data = processor.process_data()
    logging.info(f"Structured Data: {structured_data}")
    logging.info("Data processed.")

    logging.info("Posting articles...")
    for data in structured_data:
        logging.info(f"Posting article: {data['title']}")
        response = post_article(data)
        logging.info(f"Response: {response}")
    logging.info("Articles posted.")

if __name__ == "__main__":
    run_nnw_scraper()