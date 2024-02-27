from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless if you don't need a browser UI
chrome_options.add_argument("--disable-notifications")  # Disable browser notifications

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Function to get post content from a single page
def get_post_content(driver, url):
    driver.get(url)
    time.sleep(3)  # Sleep to allow the page to load.
    try:
        # This selector must be specific to the content of the post
        content_element = driver.find_element(By.CSS_SELECTOR, 'div.article-content')
        content_html = content_element.get_attribute('innerHTML')

        # Print the raw HTML of the post content
        print(content_html)

        # Extracting images
        images = content_element.find_elements(By.TAG_NAME, 'img')
        for img in images:
            print(img.get_attribute('src'))  # Prints out each image URL

        # Extracting links
        links = content_element.find_elements(By.TAG_NAME, 'a')
        for link in links:
            print(link.get_attribute('href'))  # Prints out each hyperlink URL

        # Extracting videos (assuming they are in iframes)
        videos = content_element.find_elements(By.TAG_NAME, 'iframe')
        for video in videos:
            print(video.get_attribute('src'))  # Prints out each video URL

    except Exception as e:
        print(f"An error occurred while trying to get the content of {url}: {e}")

# Function to get links from website
def get_links(driver, url):
    driver.get(url)
    time.sleep(5)  # Sleep for 5 seconds to allow the page to load.
    posts = driver.find_elements(By.CLASS_NAME, 'feed-item-title')
    links = []
    for post in posts:
        href = post.get_attribute('href')
        if href:
            # Ensure the URL is absolute
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
