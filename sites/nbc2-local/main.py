#main.py

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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    return chrome_options

def scheduled_scraper_and_publish_task():
    logging.info("Setting up Chrome options")
    chrome_options = setup_chrome_options()
    
    logging.info("Installing ChromeDriver")
    service = Service(ChromeDriverManager().install())
    
    logging.info("Starting Chrome with configured options")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    db_manager = DatabaseManager(Config.DB_HOST, Config.DB_PORT, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    wp_manager = WordPressManager(Config.WORDPRESS_SITE, Config.WORDPRESS_USERNAME, Config.WORDPRESS_PASSWORD, Config.POST_TO_WP)

    try:
        logging.info("Initializing scraper")
        scraper = Scraper(driver)
        
        if not db_manager.connect():
            logging.error("Failed to establish database connection.")
            return
        
        if Config.POST_TO_WP:
            # Process for publishing articles to WordPress
            articles_to_publish = db_manager.fetch_articles_to_publish()
            for article in articles_to_publish:
                success, wp_post_link = wp_manager.publish_post(article)
                if success:
                    db_manager.mark_article_as_published(article['canonical_url'], wp_post_link)
        else:
            # Regular scraping and saving to DB process
            all_links = scraper.get_homepage_article_links() + scraper.get_links("https://www.nbc-2.com/local-news/")
            for url in all_links:
                if "nbc-2.com" not in url:
                    logging.info(f"Skipping non-nbc-2.com domain: {url}")
                    continue
                
                if not db_manager.url_exists(url):
                    article_content = scraper.get_post_content(url)
                    if article_content:
                        article_content['source'] = "NBC2-HomePage" if "/local-news/" not in url else "NBC2-LocalNews-Page"
                        db_manager.insert_article(article_content)
        
        db_manager.close()
    finally:
        driver.quit()
        logging.info("Scraping and/or publishing task completed.")

if __name__ == "__main__":
    logging.info("Script execution started")
    
    # Run the combined scraper and publisher task
    scheduled_scraper_and_publish_task()

    # Optionally, you can use a scheduler to run the task at intervals
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_scraper_and_publish_task, 'interval', minutes=45)
    
    try:
        logging.info("Starting scheduler")
        scheduler.start()
        logging.info("Scheduler started, press Ctrl+C to exit.")
        scheduler._thread.join()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler shutdown initiated")
        scheduler.shutdown()
        logging.info("Scheduler shutdown complete")
