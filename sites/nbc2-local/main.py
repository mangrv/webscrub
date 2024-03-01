import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Import the Config class
from config import Config

# Import your custom modules
from database_manager import DatabaseManager
from wordpress_manager import WordPressManager
from scraper import Scraper

# Setup logging at the top so it's configured for the entire script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-cache-dir')
    chrome_options.add_argument('--disable-application-cache')
    return chrome_options

def main():
    # Initialize and configure Chrome options
    chrome_options = setup_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize the scraper
    scraper = Scraper(driver)

    # Define the target URL for scraping
    target_url = "https://www.nbc-2.com/local-news/"
    logging.info(f"Beginning to scrape links from {target_url}")
    found_links = scraper.get_links(target_url)

    # Initialize WordPressManager with the configuration from config.py
    wp_manager = WordPressManager(Config.WORDPRESS_SITE, Config.WORDPRESS_USERNAME, Config.WORDPRESS_PASSWORD, Config.POST_TO_WP)

    # Initialize DatabaseManager and connect to the database
    db_manager = DatabaseManager(Config.DB_HOST, Config.DB_PORT, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    if not db_manager.connect():
        logging.error("Failed to establish database connection.")
        return

    # Iterate through the found links and process them
    for link in found_links:
        logging.info(f"Processing content from {link}")
        post_details = scraper.get_post_content(link)
        if post_details:
            # Check if posting to WordPress is enabled
            if wp_manager.post_to_wp:
                logging.info(f"Publishing to WordPress: {post_details['title']}")
                success, wp_post_link = wp_manager.publish_post(post_details)
                if success:
                    logging.info(f"Published successfully to WordPress. URL: {wp_post_link}")
                    # Update the post publish status in the database
                    db_manager.update_post_publish_status(post_details['canonical_url'], wp_post_link)
                else:
                    logging.error("Failed to publish to WordPress.")
            else:
                logging.info("Posting to WordPress is disabled.")
        else:
            logging.error(f"Failed to scrape content from {link}")

    # Close the database connection
    db_manager.close()
    logging.info("Database connection closed.")

    # Quit the driver
    driver.quit()
    logging.info("Scraping process completed.")

if __name__ == "__main__":
    main()
