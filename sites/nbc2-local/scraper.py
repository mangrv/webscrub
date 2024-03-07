#scraper.py

import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
import os
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Scraper:
    def __init__(self, driver):
        self.driver = driver

    def get_links(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'feed-item-title')]")))
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'feed-item-title')]")
            links = [post.get_attribute('href') for post in posts]
            logging.info(f"Found {len(links)} links on the page: {url}")
            return links
        except TimeoutException as e:
            logging.error(f"Timeout while trying to get links from {url}: {e}")
            return []
        except Exception as e:
            logging.error(f"General exception while getting links from {url}: {e}")
            return []

    def get_post_content(self, url):
        self.driver.get(url)
        self.save_html_to_file(url)  # Save HTML before processing for debugging
        post_details = {}
        try:
            title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.article-headline--title'))).text
            content_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-content--body-text')))
            inner_html = content_element.get_attribute('innerHTML')
            soup = BeautifulSoup(inner_html, 'html.parser')

            # Clean up the HTML content
            for ad_block in soup.select('.ad-container, .ad-rectangle, .ad-label'):
                ad_block.decompose()
            for img in soup.find_all('img', {'data-src': True}):
                img['src'] = img['data-src']
                del img['data-src']

            post_details['title'] = title
            post_details['content'] = str(soup)
            post_details['publish_date'] = datetime.now().strftime('%Y-%m-%d')
            post_details['canonical_url'] = self.driver.current_url

            # Optional fields
            excerpt_element = self.driver.find_elements(By.CSS_SELECTOR, 'h2.article-headline--subheadline')
            post_details['excerpt'] = excerpt_element[0].text if excerpt_element else ''

            og_image_meta = self.driver.find_elements(By.XPATH, "//meta[@property='og:image']")
            post_details['post_image'] = og_image_meta[0].get_attribute('content') if og_image_meta else ''

            author_element = self.driver.find_elements(By.CSS_SELECTOR, 'div.article-byline--details-author')
            post_details['author'] = author_element[0].text if author_element else 'Unknown'

            return post_details
        except Exception as e:
            logging.error(f"Failed to scrape content from {url}: {e}")
            return None

    def get_homepage_article_links(self):
        """Extracts article links from the homepage, excluding unwanted content."""
        try:
            self.driver.get("https://www.nbc-2.com/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//script[@type='application/ld+json']")))
            article_urls = []
            for script in self.driver.find_elements(By.XPATH, "//script[@type='application/ld+json']"):
                try:
                    data = json.loads(script.get_attribute('innerHTML'))
                    if data["@type"] == "ItemList":
                        for item in data["itemListElement"]:
                            if not any(x in item['url'] for x in ['sponsored-content', 'top-picks']):
                                article_urls.append(item['url'])
                    logging.info(f"Filtered {len(article_urls)} article links.")
                except json.JSONDecodeError:
                    continue
            return article_urls
        except Exception as e:
            logging.error(f"Error extracting homepage article links: {e}")
            return []

    def save_html_to_file(self, url):
        filename = "html_output_" + url.replace("://", "_").replace("/", "_")[:50] + ".html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.driver.page_source)
        logging.info(f"Saved HTML content of {url} to {filename}")

if __name__ == "__main__":
    # Example usage
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    scraper = Scraper(driver)
    try:
        links = scraper.get_homepage_article_links()
        for link in links:
            content = scraper.get_post_content(link)
            if content:
                print(content)
    finally:
        driver.quit()
