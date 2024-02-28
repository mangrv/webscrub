from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless if you don't need a browser UI
chrome_options.add_argument("--disable-notifications")  # Disable browser notifications

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Specify output directory
output_dir = 'sites/output'
os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it does not exist

# Function to get post content from a single page
def get_post_content(driver, url):
    driver.get(url)
    time.sleep(3)  # Sleep to allow the page to load.
    try:
        # Generate a unique filename for each URL
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{output_dir}/content_{timestamp}.txt"

        # Extracting specific details
        post_title = driver.find_element(By.CSS_SELECTOR, 'h1.article-headline--title').text
        post_excerpt = driver.find_element(By.CSS_SELECTOR, 'h2.article-headline--subheadline').text
        post_image = driver.find_element(By.CSS_SELECTOR, 'div.article-branding img').get_attribute('src') if driver.find_elements(By.CSS_SELECTOR, 'div.article-branding img') else 'No image found'
        publish_date = driver.find_element(By.CSS_SELECTOR, 'div.article-headline--publish-date.border-left').text
        author = driver.find_element(By.CSS_SELECTOR, 'div.article-byline--details-author').text
        post_content = driver.find_element(By.CSS_SELECTOR, 'div.article-content--body-text').text

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Post Title: {post_title}\n")
            file.write(f"Post Excerpt: {post_excerpt}\n")
            file.write(f"Post Image URL: {post_image}\n")
            file.write(f"Publish Date: {publish_date}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Post Content: {post_content}\n\n")

            file.write("Full HTML:\n")
            file.write(driver.page_source)

    except Exception as e:
        print(f"An error occurred while trying to get the content of {url}: {e}")

# Function to get links from website
def get_links(driver, url):
    driver.get(url)
    time.sleep(5)  # Sleep for 5 seconds to allow the page to load.
    posts = driver.find_elements(By.XPATH, "//a[contains(@class, 'feed-item-title')]")
    links = []
    for post in posts:
        href = post.get_attribute('href')
        if href:
            link = href if href.startswith('http') else f"https://www.nbc-2.com{href}"
            links.append(link)
    return links

# Main process
if __name__ == "__main__":
    target_url = 'https://www.nbc-2.com/local-news/'
    found_links = get_links(driver, target_url)

    for link in found_links:
        print(f"Extracting content from {link}")
        get_post_content(driver, link)
        print("----------------------------------------------------\n")

    driver.quit()
