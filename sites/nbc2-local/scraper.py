import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, driver):
        self.driver = driver

    def get_links(self, url):
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'feed-item-title')]")))
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'feed-item-title')]")
            links = [post.get_attribute('href') for post in posts]
            logging.info(f"Found {len(links)} links on the page.")
            return links
        except Exception as e:
            logging.error(f"Failed to get links from {url}: {e}")
            return None

    def get_post_content(self, url):
        self.driver.get(url)
        post_details = {}
        try:
            post_details['title'] = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.article-headline--title'))).text
            content_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-content--body-text')))
            
            # Get the inner HTML of the content element
            inner_html = content_element.get_attribute('innerHTML')
            soup = BeautifulSoup(inner_html, 'html.parser')
            
            # Remove advertisement blocks
            for ad_block in soup.select('.ad-container, .ad-rectangle, .ad-label'):
                ad_block.decompose()
            
            # Handle lazy-loaded images if necessary
            for img in soup.find_all('img', {'data-src': True}):
                img['src'] = img['data-src']
                del img['data-src']
            
            post_details['content'] = str(soup)
            post_details['excerpt'] = self.driver.find_element(By.CSS_SELECTOR, 'h2.article-headline--subheadline').text if self.driver.find_elements(By.CSS_SELECTOR, 'h2.article-headline--subheadline') else ''
            post_details['publish_date'] = datetime.now().strftime('%Y-%m-%d')
            
            og_image_meta = self.driver.find_elements(By.XPATH, "//meta[@property='og:image']")
            post_details['post_image'] = og_image_meta[0].get_attribute('content') if og_image_meta else None
            
            post_details['canonical_url'] = self.driver.current_url
            post_details['author'] = self.driver.find_element(By.CSS_SELECTOR, 'div.article-byline--details-author').text
            
            self.save_html_to_file(url)
            
            return post_details
        except Exception as e:
            logging.error(f"Failed to scrape content from {url}: {e}")
            return None

    def save_html_to_file(self, url):
        # Ensuring filename is valid and does not include prohibited characters
        safe_url = url.split('//')[-1].replace('/', '_').replace(':', '_')
        filename = f"html_output_{safe_url}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.driver.page_source)
        logging.info(f"Saved HTML to {filename}")
