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

    def update_is_published_flag(self, canonical_url):
        try:
            cursor = self.connection.cursor()
            query = "UPDATE articles SET is_published_to_wordpress = 1 WHERE canonical_url = %s"
            cursor.execute(query, (canonical_url,))
            self.connection.commit()
            logging.info(f"Updated is_published_to_wordpress flag for {canonical_url}")
        except Error as e:
            logging.error(f"Error while updating is_published_to_wordpress flag: {e}")

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

    def upload_image_to_wordpress(self, image_url):
        if not image_url:
            return None
        media_endpoint = f"{self.wordpress_site}/wp-json/wp/v2/media"
        headers = self.get_basic_auth_header()
        headers.update({
            "Content-Disposition": f"attachment; filename={os.path.basename(image_url)}",
            "Content-Type": "image/jpeg"
        })
        image_data = requests.get(image_url).content
        response = requests.post(media_endpoint, headers=headers, data=image_data)
        if response.status_code == 201:
            return response.json()['id']
        logging.error(f"Failed to upload image to WordPress: {response.status_code}, {response.text}")
        return None

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

        if 'post_image' in post_details and post_details['post_image']:
            image_id = self.upload_image_to_wordpress(post_details['post_image'])
            if image_id:
                post_data["featured_media"] = image_id  # Set the uploaded image as the featured media

        publish_endpoint = f"{self.wordpress_site}/wp-json/wp/v2/posts"
        response = requests.post(publish_endpoint, headers=headers, json=post_data)
        if response.status_code == 201:
            post_response = response.json()
            wp_post_link = post_response.get('link', 'No link available')  # Extract the link to the published post
            logging.info(f"Post successfully published to WordPress. Title: {post_details['title']}, Link: {wp_post_link}")
            # Log the category and tag assignment for verification
            logging.info(f"Assigned to Category 'Local News' (ID: 47), Tag 'NBC2 News' (ID: 223)")
            return True, wp_post_link  # Return success and the link to the published post
        else:
            logging.error(f"Failed to publish post to WordPress: {response.status_code}, {response.text}")
            return False, None  # Indicate failure and return no link


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
                if wp_manager.publish_post(post_details):
                    db_manager.update_is_published_flag(post_details['canonical_url'])
                else:
                    logging.error(f"Failed to publish post to WordPress: {post_details['title']}")
            else:
                logging.error(f"Failed to scrape or publish content from {link}")

    driver.quit()

if __name__ == "__main__":
    main()
