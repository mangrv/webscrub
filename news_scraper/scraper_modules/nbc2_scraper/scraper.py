import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent

ua = UserAgent()

session = requests.Session()
session.headers.update({
    'User-Agent': ua.random
})

def homepage_localnews_link_extractor(base_url, url, seen_links):
    response = session.get(url + '?t=' + str(time.time()))
    time.sleep(5)

    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all(lambda tag: tag.name == 'div' and tag.get('data-content-url'))

    links = []
    for article in articles:
        link = article.find('a', href=True)['href']
        if not link.startswith('http'):
            link = base_url + link
        data_site = article.get('data-site', 'N/A')
        data_section = article.get('data-section', 'N/A')
        data_subsection = article.get('data-subsection', 'N/A')
        
        title_div = article.find('div', class_='feed-item-title')
        title = article.get('data-content-title', 'N/A')
       
        image = article.find('img')
        image_url = article.get('data-content-image', 'N/A')

        if data_site == 'wbbh' and link not in seen_links:    
            links.append((link, data_site, data_section, data_subsection, image_url, title))
            seen_links.add(link)
    
    return links, seen_links

seen_links = set()

base_url = "https://nbc-2.com"
homepage_links, seen_links = homepage_localnews_link_extractor(base_url, base_url + "/", seen_links)
localnews_links, seen_links = homepage_localnews_link_extractor(base_url, base_url + "/local-news/", seen_links)

for link, site, section, subsection, image_url, title in homepage_links + localnews_links:
    print(f"Link: {link}, Site: {site}, Section: {section}, Subsection: {subsection}, Title: {title}")

for item in homepage_links + localnews_links:
    if isinstance(item, tuple):
        if len(item) == 6:
            link, site, section, subsection, image_url, title = item
            print(f"Link: {link}, Site: {site}, Section: {section}, Subsection: {subsection}, Image URL: {image_url}, Title: {title}")
        elif len(item) == 5:
            link, site, section, subsection, image_url = item
            print(f"Link: {link}, Site: {site}, Section: {section}, Subsection: {subsection}, Image URL: {image_url}")
        else:
            print(f"Skipping item {item} as it's not a tuple with 5 or 6 elements")
    else:
        print(f"Skipping item {item} as it's not a tuple")


def scrape_article_content(url, image_url):
    print(f"Fetching article content from: {url}")
    try:
        response = session.get(url + '?t=' + str(time.time()))
        time.sleep(5)
        soup = BeautifulSoup(response.content, 'html.parser')

        author = soup.find('a', class_='article-byline--details-author-name')
        author = author.get_text() if author else 'N/A'

        publish_date = soup.find('div', class_='article-headline--publish-date border-left')
        publish_date = publish_date.get_text() if publish_date else 'N/A'

        image_meta_tag = soup.find('meta', attrs={'name': 'twitter:image'})
        if image_meta_tag:
            post_media = image_meta_tag['content']
            post_media = post_media.split('?')[0]
        else:
            post_media = 'N/A'

        article_body = soup.find('div', class_='article-content--body-text')
        if article_body:
            for ad in article_body.find_all('div', class_='ad-rectangle'):
                ad.decompose()
            article_body = article_body.prettify()
        else:
            article_body = 'N/A'

        return {
            'author': author,
            'publish_date': publish_date,
            'image_url': post_media,
            'content': article_body,
            'url': url
        }
    except requests.exceptions.TooManyRedirects:
        print(f"Failed to fetch article content from: {url} due to too many redirects")
        return None

    
base_url = "https://nbc-2.com"
seen_links = set()

homepage_links, seen_links = homepage_localnews_link_extractor(base_url, base_url + "/", seen_links)
localnews_links, seen_links = homepage_localnews_link_extractor(base_url, base_url + "/local-news/", seen_links)

for link, site, section, subsection, image_url, title in homepage_links + localnews_links:
    content = scrape_article_content(link, image_url)
    if content is None:
        print(f"Skipping article {link} due to too many redirects")
        continue
    image_url = content['image_url']
    print(f"Link: {link}, Site: {site}, Section: {section}, Subsection: {subsection}, Image URL: {image_url}, Title: {title}")
    print(f"Content: {content}")
