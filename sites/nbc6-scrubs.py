from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import os
from dateutil import parser
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")

webdriver_service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

output_dir = 'sites/output'
os.makedirs(output_dir, exist_ok=True)

# Use environment variables for database connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Default port is 3306 if not specified
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Insert post details into database
def insert_post_details(connection, post_details):
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO articles (title, author, publish_date, content, excerpt, canonical_url, post_image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, post_details)
        connection.commit()
    except Error as e:
        print(f"Failed to insert record into MySQL table: {e}")

def get_post_content(driver, url, db_connection):
    driver.get(url)
    # Initialize post_excerpt to a default value in case it's not found
    post_excerpt = 'No excerpt found'
    try:
        post_excerpt = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.article-headline--subheadline'))
        ).text
    except Exception as e:
        print(f"Element not found or other error for excerpt: {e}")

    try:
        post_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.article-headline--title'))
        ).text
        post_image = driver.find_element(By.CSS_SELECTOR, 'div.article-branding img').get_attribute('src') if driver.find_elements(By.CSS_SELECTOR, 'div.article-branding img') else 'No image found'
        publish_date = driver.find_element(By.CSS_SELECTOR, 'div.article-headline--publish-date.border-left').text
        author = driver.find_element(By.CSS_SELECTOR, 'div.article-byline--details-author').text
        post_content = driver.find_element(By.CSS_SELECTOR, 'div.article-content--body-text').text
        canonical_url = driver.find_element(By.CSS_SELECTOR, 'link[rel="canonical"]').get_attribute('href')

        formatted_date = publish_date.replace('Updated: ', '').replace(' EST', '')
        formatted_date = parser.parse(formatted_date).strftime('%Y-%m-%d')

        post_details = (post_title, author, formatted_date, post_content, post_excerpt, canonical_url, post_image)

        insert_post_details(db_connection, post_details)

    except Exception as e:
        print(f"An error occurred while trying to get the content of {url}: {e}")

def get_links(driver, url):
    driver.get(url)
    time.sleep(5)
    posts = driver.find_elements(By.XPATH, "//a[contains(@class, 'feed-item-title')]")
    links = []
    for post in posts:
        href = post.get_attribute('href')
        if href:
            links.append(href)
    return links

if __name__ == "__main__":
    db_connection = connect_to_database()

    if db_connection is not None:
        target_url = 'https://www.nbc-2.com/local-news/'
        found_links = get_links(driver, target_url)

        for link in found_links:
            print(f"Extracting content from {link}")
            get_post_content(driver, link, db_connection)
            print("----------------------------------------------------\n")

        db_connection.close()
    else:
        print("Failed to connect to the database.")

    driver.quit()
