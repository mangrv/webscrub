from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse



# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--disable-application-cache")

# Initialize WebDriver with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to extract and save news links, titles, and post images
def extract_news_links_titles_images(url):
    elements = driver.find_elements(By.CSS_SELECTOR, "div.grid-content.article[data-content-url][data-content-title][data-subsection='local-news']")
    news_items = [] 
    for element in elements:
        link = element.get_attribute('data-content-url')
        title = element.get_attribute('data-content-title')
        post_image = element.find_element(By.CSS_SELECTOR, ".image").get_attribute('style')
        if link and title: 
            full_link = f"https://www.abc-7.com{link}" if not link.startswith('http') else link
            image_url = post_image.split("url(")[-1].split(")")[0]
            news_items.append((title, full_link, image_url))
    return news_items

def extract_article_details(news_items, save_to_strapi=False):
    for index, (title, link, post_image) in enumerate(news_items):
        driver.get(link)
        time.sleep(5)

        # Initialize the clean_html_content variable
        clean_html_content = ""

        # Extract author details
        author_details = driver.find_elements(By.CSS_SELECTOR, ".article-authors .article-byline--details-author-name")
        author_name = author_details[0].text if author_details else "No author name found"

        # Extract excerpt
        excerpt_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-teaser")
        excerpt = excerpt_elements[0].text if excerpt_elements else "No excerpt found"

        # Extract content body, excluding advertisement section
        content_body_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-text")
        content_body = ""
        for el in content_body_elements:
            # Check if the element contains advertisement section, exclude if present
            ad_section = el.find_elements(By.CSS_SELECTOR, ".ad-rectangle")
            if ad_section:
                continue
            content_body += el.get_attribute('innerHTML')
            clean_html_content += el.get_attribute('outerHTML')

            
        # Extract clean HTML content, excluding sections with advertisements
        content_body_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-text, .article-content--body-text-raw")
        for el in content_body_elements:
            # Convert WebElement to a BeautifulSoup object
            soup = BeautifulSoup(el.get_attribute('outerHTML'), 'html.parser')
                
            # Remove any ad sections
            ads = soup.find_all(class_="ad-rectangle")
            for ad in ads:
                ad.decompose()

            # Check if after removing ads, the element still contains meaningful content
            if soup.text.strip():
                clean_html_content += str(soup) + "\n\n"
                
        # Extract publish date
        publish_date_elements = driver.find_elements(By.CSS_SELECTOR, ".article-headline--publish-date")
        publish_date = publish_date_elements[0].text if publish_date_elements else "No publish date found"

        # Compile and append details
        details = {
            "Title": title,
            "Author Name": author_name,
            "Excerpt": excerpt,
            "Content Body": content_body,
            "Clean Content": clean_html_content,
            "Publish Date": publish_date
        }

        # Save content to individual files
        filename = f"{index}_{title.replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Title: {title}\n")
            file.write(f"Author Name: {author_name}\n")
            file.write(f"Excerpt: {excerpt}\n")
            file.write(f"Publish Date: {publish_date}\n")
            file.write(f"URL: {link}\n")
            file.write(f"Post Content:\n\n")
            file.write(content_body)
            file.write(clean_html_content)
            print(f"Content for {title} saved to {filename}")

        if save_to_strapi:
            push_to_strapi(title, author_name, excerpt, content_body, publish_date, link, post_image)

def push_to_strapi(title, author_name, excerpt, content_body, publish_date, link, post_image):
    payload = {
        "title": title,
        "author_name": author_name,
        "excerpt": excerpt,
        "content_body": content_body,
        "publish_date": publish_date,
        "link": link,
        "post_image": post_image
    }
    print("Data pushed to Strapi.")

news_items = extract_news_links_titles_images("https://www.abc-7.com/local-news")
extract_article_details(news_items, save_to_strapi=False)

def save_html(url, page_name):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.grid-content.article[data-content-url][data-content-title][data-subsection='local-news']")))

        
        news_items_info = ''
        # Check if the page is 'Homepage' or 'LocalNewsPage'
        if page_name in ['Homepage', 'LocalNewsPage']:
            news_items = extract_news_links_titles_images(url)
            news_items_info = "\n".join([f"{title}: {link}" for title, link, post_image in news_items]) + "\n\n"

        # Get page source
        html_content = driver.page_source

        # Generate filename based on current date and time
        current_time = datetime.now().strftime("%m%d_%H%M")
        filename = f"{current_time}_{page_name}.txt"

        # Save to a file, news items at the top
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(news_items_info + html_content)
        print(f"HTML content saved to {filename}")

       
        # Extract image URLs from the main page or local news page
        article_divs = driver.find_elements(By.CSS_SELECTOR, "div.bg-image")
        image_urls = []
        for div in article_divs:
            style_attr = div.get_attribute('style')
            if style_attr:
                # Use regex to extract URL from the style attribute
                match = re.search(r"url\((.*?)\)", style_attr)
                if match:
                    image_url = match.group(1)
                    image_urls.append(image_url)


        # Assuming `image_url` contains the URL you've extracted
        original_image_url = "https://kubrick.htvapps.com/htv-prod-media.s3.amazonaws.com/images/thumbnail-123-1-1-6608832061308.jpg?crop=1.00xw:0.752xh;0,0.0897xh&resize=900:*"

        # Parse the URL
        parsed_url = urlparse(original_image_url)

        # Reconstruct the URL without the query part
        clean_image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        print(f"Original Image URL: {original_image_url}")
        print(f"Clean Image URL: {clean_image_url}")

 


        # Extract article details and save to individual files
        for index, (title, link, post_image) in enumerate(news_items):
            driver.get(link)
            time.sleep(10)

            # Get the full raw HTML content here
            full_raw_html = driver.page_source

            # Initialize variable to store clean HTML
            clean_html_content = ""
            
            # Extract clean HTML content, excluding sections with advertisements
            content_body_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-text, .article-content--body-text-raw")
            for el in content_body_elements:
                # Convert WebElement to a BeautifulSoup object
                soup = BeautifulSoup(el.get_attribute('outerHTML'), 'html.parser')
                
                # Remove any ad sections
                ads = soup.find_all(class_="ad-rectangle")
                for ad in ads:
                    ad.decompose()

                # Check if after removing ads, the element still contains meaningful content
                if soup.text.strip():
                    clean_html_content += str(soup) + "\n\n"


            # Extract author details
            author_details = driver.find_elements(By.CSS_SELECTOR, ".article-authors .article-byline--details-author-name")
            author_name = author_details[0].text if author_details else "No author name found"

            # Extract excerpt
            excerpt_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-teaser")
            excerpt = excerpt_elements[0].text if excerpt_elements else "No excerpt found"

            # Extract content body
            content_body_elements = driver.find_elements(By.CSS_SELECTOR, ".article-content--body-text-raw")
            content_body = "\n".join([el.get_attribute('innerHTML') for el in content_body_elements])

            # Extract publish date
            publish_date_elements = driver.find_elements(By.CSS_SELECTOR, ".article-headline--publish-date")
            publish_date = publish_date_elements[0].text if publish_date_elements else "No publish date found"

            # Save article info to individual files
            filename = f"{index}_{title.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"Title: {title}\n")
                file.write(f"Image URL: {clean_image_url}\n")
                file.write(f"Author Name: {author_name}\n")
                file.write(f"Excerpt: {excerpt}\n")
                file.write(f"Publish Date: {publish_date}\n")
                file.write(f"URL: {link}\n")
                file.write(f"Post Content:\n\n") 
                file.write(content_body)

            # Save clean html    
                file.write("\n\n" + "-"*80 + "\n")
                file.write("CLEAN HTML CONTENT BELOW (No Advertisements)\n")
                file.write("-"*80 + "\n\n")
                file.write(clean_html_content)
                print(f"Clean content saved to {filename}")
 

               
            # Save raw html
                file.write("\n\n" + "-"*80 + "\n")
                file.write("RAW HTML CONTENT BELOW\n")
                file.write("-"*80 + "\n\n")
                
                file.write(full_raw_html)

                print(f"Content for {title} saved to {filename}")


    except Exception as e:
        print(f"An error occurred: {e}")


urls = [
    ('https://www.abc-7.com', 'Homepage'),
    ('https://www.abc-7.com/local-news', 'LocalNewsPage')
]


for url, page_name in urls:
    save_html(url, page_name)


driver.quit()
