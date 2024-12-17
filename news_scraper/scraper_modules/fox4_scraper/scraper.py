import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Initialize UserAgent
ua = UserAgent()

# Create a session and set a random User-Agent
session = requests.Session()
session.headers.update({
    'User-Agent': ua.random
})

def homepage_localnews_link_extractor(base_url, url, seen_links):
    response = session.get(url)
    if response.status_code != 200:
        return [], seen_links

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    # Extract all relevant articles from the homepage
    for article in soup.find_all('a', class_=['huge-item', 'small-item']):
        link = article['href']
        if not link.startswith('http'):
            link = base_url + link
        
        # Avoid processing duplicate links
        if link in seen_links:
            continue
        seen_links.add(link)

        # Extract article title, section, image, etc.
        title = article.find('div', class_='ShowcasePromo-title').text.strip() if article.find('div', class_='ShowcasePromo-title') else "No title"
        image_url = None
        image_div = article.find('div', class_='ShowcaseImageOverlay')
        if image_div and 'style' in image_div.attrs:
            image_style = image_div['style']
            start = image_style.find("url('") + 5
            end = image_style.find("')", start)
            image_url = image_style[start:end]
        
        section = "Local News"  # Modify this logic based on actual structure

        articles.append((link, "Fox4Now", section, section, image_url, title))

    return articles, seen_links

def scrape_article_content(url, image_url):
    response = session.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract article body text
    article_body_div = soup.find('div', class_='RichTextArticleBody-body')
    if article_body_div:
        paragraphs = article_body_div.find_all('p')
        article_body = ' '.join([p.get_text() for p in paragraphs]).strip()
        
        # Extract full HTML for the article content
        article_body_html = str(article_body_div)
    else:
        article_body = "No content"
        article_body_html = "No content"

    # Extract the author (if present)
    author = soup.find('div', class_='Page-body ArticlePage-byline')
    author = author.get_text(strip=True) if author else "Unknown Author"

    # Extract the publish date
    publish_date_element = soup.find('span', class_='published-date')
    if publish_date_element:
        publish_date = publish_date_element.get('data-timestamp', None)
    else:
        publish_date = "Unknown Publish Date"

    # Build the content dictionary with both text and HTML
    return {
        "content": article_body,
        "content_html": article_body_html,  # This is the full HTML of the article body
        "author": author.strip(),
        "publish_date": publish_date,
        "image_url": image_url,
        "url": url
    }
