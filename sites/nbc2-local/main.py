import logging
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from config import Config
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

def scheduled_scraper_task():
    chrome_options = setup_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        scraper = Scraper(driver)
        target_url = "https://www.nbc-2.com/local-news/"
        logging.info(f"Beginning to scrape links from {target_url}")
        found_links = scraper.get_links(target_url)
        
        wp_manager = WordPressManager(Config.WORDPRESS_SITE, Config.WORDPRESS_USERNAME, Config.WORDPRESS_PASSWORD, Config.POST_TO_WP)
        db_manager = DatabaseManager(Config.DB_HOST, Config.DB_PORT, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
        
        if not db_manager.connect():
            logging.error("Failed to establish database connection.")
            return
        
        for link in found_links:
            if not db_manager.url_exists(link):
                logging.info(f"Processing new content from {link}")
                post_details = scraper.get_post_content(link)
                if post_details:
                    if db_manager.insert_article(post_details) and wp_manager.post_to_wp:
                        logging.info(f"Publishing to WordPress: {post_details['title']}")
                        success, wp_post_link = wp_manager.publish_post(post_details)
                        if success:
                            logging.info(f"Published successfully to WordPress. URL: {wp_post_link}")
                            db_manager.update_post_publish_status(post_details['canonical_url'], wp_post_link)
                        else:
                            logging.error("Failed to publish to WordPress.")
                else:
                    logging.error(f"Failed to scrape content from {link}")
            else:
                logging.info(f"Skipping already processed content: {link}")
        
        db_manager.close()
    finally:
        driver.quit()
        logging.info("Scraping task completed.")

if __name__ == "__main__":
    # Run the task once immediately upon starting the script
    scheduled_scraper_task()

    # Then start the scheduler to run the task every 45 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_scraper_task, 'interval', minutes=45)
    scheduler.start()
    
    logging.info("Scheduler started, press Ctrl+C to exit.")
    
    try:
        # This is to keep the main thread alive
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Not strictly necessary if shutting down the whole process