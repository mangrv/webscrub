import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

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
            post_details['content'] = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-content--body-text'))).text
            post_details['excerpt'] = self.driver.find_element(By.CSS_SELECTOR, 'h2.article-headline--subheadline').text if self.driver.find_elements(By.CSS_SELECTOR, 'h2.article-headline--subheadline') else ''
            post_details['publish_date'] = datetime.now().strftime('%Y-%m-%d')
            post_details['post_image'] = self.driver.find_element(By.CSS_SELECTOR, 'div.article-branding img').get_attribute('src') if self.driver.find_elements(By.CSS_SELECTOR, 'div.article-branding img') else None
            post_details['canonical_url'] = self.driver.current_url
            return post_details
        except Exception as e:
            logging.error(f"Failed to scrape content from {url}: {e}")
            return None
