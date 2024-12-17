from scraper_modules.fox4_scraper.scraper import homepage_localnews_link_extractor as fox4_extractor, scrape_article_content as fox4_content
from data_processor.processor import DataProcessor
from cms_integration.integrator import post_article
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize UserAgent
try:
    ua = UserAgent()
    session = requests.Session()
    session.headers.update({'User-Agent': ua.random})
except Exception as e:
    logging.error(f"Failed to initialize UserAgent: {str(e)}. Using fallback User-Agent.")
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

# Function to format the publish date from ISO 8601 to the required format
def format_publish_date(date_str):
    try:
        # Parse the ISO 8601 format
        parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Format it into the desired format: '%I:%M %p %b %d, %Y'
        return parsed_date.strftime('%I:%M %p %b %d, %Y')
    except ValueError as e:
        logging.error(f"Error: Date string '{date_str}' does not match ISO format.")
        return "Unknown Publish Date"

# Function to extract homepage and local news links
def homepage_localnews_link_extractor(base_url, url, seen_links):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch page {url}: {str(e)}")
        return [], seen_links

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for article in soup.find_all('a', class_=['huge-item', 'small-item']):
        link = article['href']
        if not link.startswith('http'):
            link = base_url + link

        if link in seen_links:
            logging.info(f"Skipping duplicate link: {link}")
            continue
        seen_links.add(link)

        title = article.find('div', class_='ShowcasePromo-title').text.strip() if article.find('div', class_='ShowcasePromo-title') else "No title"
        if title == "No title":
            logging.warning(f"No title found for article: {link}")

        image_url = None
        image_div = article.find('div', class_='ShowcaseImageOverlay')
        if image_div and 'style' in image_div.attrs:
            image_style = image_div['style']
            start = image_style.find("url('") + 5
            end = image_style.find("')", start)
            image_url = image_style[start:end]

        section = "Local News"  # Static section value for now
        articles.append((link, "Fox4Now", section, section, image_url, title))

    return articles, seen_links

# Function to scrape article content
def scrape_article_content(url, image_url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch article {url}: {str(e)}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    article_body_div = soup.find('div', class_='RichTextArticleBody-body')
    if article_body_div:
        paragraphs = article_body_div.find_all('p')
        article_body = ' '.join([p.get_text() for p in paragraphs]).strip()
        article_body_html = str(article_body_div)
    else:
        logging.warning(f"No content found for article: {url}")
        article_body = "No content"
        article_body_html = "No content"

    author = soup.find('div', class_='Page-body ArticlePage-byline')
    author = author.get_text(strip=True) if author else "Unknown Author"

    # Extract the publish date and format it
    publish_date_element = soup.find('span', class_='published-date')
    if publish_date_element:
        publish_date = publish_date_element.get('data-timestamp', None)
        formatted_publish_date = format_publish_date(publish_date)
    else:
        formatted_publish_date = "Unknown Publish Date"

    return {
        "content": article_body,
        "content_html": article_body_html,
        "author": author.strip(),
        "publish_date": formatted_publish_date,  # Use the formatted date
        "image_url": image_url,
        "url": url
    }

# Main function to run the scraper
def run_fox4_scraper():
    seen_links = set()
    fox4_base_url = "https://www.fox4now.com"

    # Extract homepage and local news links
    logging.info("Extracting links from homepage and local news sections...")
    fox4_homepage_links, seen_links = fox4_extractor(fox4_base_url, fox4_base_url + "/", seen_links)
    fox4_localnews_links, seen_links = fox4_extractor(fox4_base_url, fox4_base_url + "/local-news/", seen_links)

    all_links = fox4_homepage_links + fox4_localnews_links
    raw_data = []

    for link, site, section, subsection, image_url, title in all_links:
        # Scrape article content
        content = fox4_content(link, image_url)
        if content is not None:
            content["subsection"] = subsection
            content["site"] = site
            content["title"] = title
            logging.info(f"Scraped content: {content['title']}")
            raw_data.append(content)

    logging.info(f"Total articles scraped: {len(raw_data)}")

    # Process data using DataProcessor
    logging.info("Processing data...")
    processor = DataProcessor(raw_data)
    structured_data = processor.process_data()
    logging.info(f"Data processed. Structured data count: {len(structured_data)}")

    # Post articles to Strapi
    logging.info("Posting articles...")
    for data in structured_data:
        try:
            logging.info(f"Posting article: {data['title']}")
            post_article(data)
        except Exception as e:
            logging.error(f"Failed to post article {data['title']} due to {str(e)}")
    logging.info("Articles posted successfully.")

if __name__ == "__main__":
    run_fox4_scraper()
