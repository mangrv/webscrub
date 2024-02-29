import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil import parser
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import requests
import logging
import base64
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup Chrome options
def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    return chrome_options

class DatabaseManager:
    def __init__(self):
        self.db_host = os.getenv("DB_HOST")
        self.db_port = int(os.getenv("DB_PORT", 3306))
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.connection = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
        if self.connection.is_connected():
            logging.info("Database connection established.")
            return self
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed.")

    def update_post_publish_status(self, canonical_url, wordpress_url):
        try:
            cursor = self.connection.cursor()
            query = """UPDATE articles SET is_published_to_wordpress = %s, wordpress_url = %s WHERE canonical_url = %s"""
            cursor.execute(query, (1, wordpress_url, canonical_url))
            self.connection.commit()
            logging.info(f"Post publish status and WordPress URL updated for {canonical_url}")
        except Error as e:
            logging.error(f"Failed to update post publish status: {e}")
        finally:
            cursor.close()

class WordPressManager:
    def __init__(self):
        self.wordpress_site = os.getenv("WORDPRESS_SITE")
        self.wordpress_username = os.getenv("WORDPRESS_USERNAME")
        self.wordpress_password = os.getenv("WORDPRESS_PASSWORD")
        self.post_to_wp = os.getenv("POST_TO_WP", "FALSE").lower() == "true"

    def get_basic_auth_header(self):
        credentials = f"{self.wordpress_username}:{self.wordpress_password}"
        token = base64.b64encode(credentials.encode()).decode("utf-8")
        return {"Authorization": f"Basic {token}"}
    
    def publish_post(self, post_details):
        headers = self.get_basic_auth_header()
        # Set the category and tag IDs
        categories = [47]  # Category ID for 'Local News'
        tags = [223]  # Tag ID for 'NBC2 News'

        post_data = {
            "title": post_details['title'],
            "content": post_details['content'],
            "excerpt": post_details['excerpt'],
            "status": "publish",
            "categories": categories,  # Assign the post to the 'Local News' category
            "tags": tags,  # Tag the post with 'NBC2 News'
            "date_gmt": post_details['publish_date'] + 'T00:00:00',  # Ensure the date format is correct
        }

        if 'post_image' in post_details:
            image_id = self.upload_image_to_wordpress(post_details['post_image'], headers)
            if image_id:
                post_data['featured_media'] = image_id

        response = requests.post(f"{self.wordpress_site}/wp-json/wp/v2/posts", headers=headers, json=post_data)
        if response.status_code == 201:
            wp_post_link = response.json().get('link')
            logging.info(f"Post successfully published to WordPress: {wp_post_link}")
            return True, wp_post_link
        else:
            logging.error(f"Failed to publish post to WordPress: {response.status_code}, {response.text}")
            return False, None

    def upload_image_to_wordpress(self, image_url, headers):
        media_endpoint = f"{self.wordpress_site}/wp-json/wp/v2/media"
        image_data = requests.get(image_url).content
        files = {'file': ('filename.jpg', image_data, 'image/jpeg')}
        response = requests.post(media_endpoint, headers=headers, files=files)
        if response.status_code == 201:
            return response.json()['id']
        logging.error("Failed to upload image to WordPress.")
        return None

class Scraper:
    def __init__(self, driver):
        self.driver = driver

    def get_links(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'feed-item-title')]")))
        posts = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'feed-item-title')]")
        return [post.get_attribute('href') for post in posts]

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

def main():
    chrome_options = setup_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    scraper = Scraper(driver)
    wp_manager = WordPressManager()

    target_url = "https://www.nbc-2.com/local-news/"
    found_links = scraper.get_links(target_url)

    with DatabaseManager() as db_manager:
        if not db_manager:
            logging.error("Failed to establish database connection.")
            return
        for link in found_links:
            post_details = scraper.get_post_content(link)
            if post_details and wp_manager.post_to_wp:
                success, wp_post_link = wp_manager.publish_post(post_details)
                if success:
                    db_manager.update_post_publish_status(post_details['canonical_url'], wp_post_link)
                    logging.info(f"Successfully published '{post_details['title']}' to WordPress and updated the database.")
                else:
                    logging.error(f"Failed to publish '{post_details['title']}' to WordPress.")
            else:
                logging.error(f"Failed to scrape or publish content from {link}")

    driver.quit()

if __name__ == "__main__":
    main()