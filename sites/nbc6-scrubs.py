from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import os
import datetime
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Function to connect to the database
def connect_to_db(config):
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Check if an article already exists based on its canonical URL
def check_article_exists(connection, canonical_url):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM articles WHERE canonical_url = %s"
    cursor.execute(query, (canonical_url,))
    (count,) = cursor.fetchone()
    return count > 0

# Insert a new article into the database
def insert_article(db_connection, title, author, publish_date, content, canonical_url):
    cursor = db_connection.cursor()
    query = """
    INSERT INTO articles (title, author, publish_date, content, canonical_url)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (title, author, publish_date, content, canonical_url))
    db_connection.commit()

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")
webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Your existing web scraping functions here
# - get_article_details(driver, url)
# - get_links(driver, url)

if __name__ == "__main__":
    db_connection = connect_to_db(db_config)
    if not db_connection:
        print("Failed to connect to the database. Exiting...")
        exit()

    target_url = 'https://www.example.com/'  # Your target URL
    links = get_links(driver, target_url)

    if links:
        for index, link in enumerate(links):
            title, author_name, publish_date, excerpt, content_html, full_html_content, canonical_url = get_article_details(driver, link)
            if not check_article_exists(db_connection, canonical_url):
                # Only insert if the article doesn't already exist
                insert_article(db_connection, title, author_name, publish_date, content_html, canonical_url)
                print(f"Article inserted: {title}")
            else:
                print(f"Article already exists, skipping: {title}")
    else:
        print("No article links found.")
    
    driver.quit()
    if db_connection.is_connected():
        db_connection.close()
