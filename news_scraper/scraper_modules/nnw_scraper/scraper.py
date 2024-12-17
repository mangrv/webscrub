import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin
import json
import re
from datetime import datetime

ua = UserAgent()

session = requests.Session()
session.headers.update({
    'User-Agent': ua.random
})

def get_articles(url):
    try:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        main_content = soup.find('main', class_='gnt_cw')

        articles = []

        processed_urls = set()

        for a_tag in main_content.find_all('a', href=True):
            link_url = urljoin(url, a_tag['href'])
            article_name = a_tag.get_text(strip=True)

            if not link_url.startswith("https://www.naplesnews.com/") or not re.search(r'/\d{4}/\d{2}/\d{2}/', link_url):
                continue

            if link_url in processed_urls:
                continue

            processed_urls.add(link_url)

            img_tag = a_tag.find('img', recursive=True)

            if img_tag:
                if 'data-g-r' in img_tag.attrs and img_tag['data-g-r'] == 'lazy':
                    img_src_url = urljoin(url, img_tag['data-src']) if 'data-src' in img_tag.attrs else None
                else:
                    img_src_url = urljoin(url, img_tag['src']) if 'src' in img_tag.attrs else None
            else:
                img_src_url = None

            div_tag = a_tag.find('div', class_='gnt_sbt')
            posted_time = div_tag.get('data-c-dt') if div_tag else "No time provided"

            article_details = get_article_details(link_url)

            articles.append({
                'link_url': link_url,
                'img_src_url': img_src_url,
                'article_name': article_name,
                'posted_time': posted_time,
                'publish_date': article_details['publish_date'],
                'media_url': article_details['media_url'],
                'content_html': article_details['content_html'],
                'author': article_details['author'],
                'full_html': article_details['full_html']
            })

        return articles

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

def get_article_details(article_url):
    response = session.get(article_url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.text, 'html.parser')

    full_html = response.text

    # Extract JSON-LD data from the raw HTML
    json_ld_match = re.findall(r'({".*?})', full_html)
    captions = []
    for match in json_ld_match:
        try:
            json_ld_data = json.loads(match)
            if json_ld_data.get("@type") == "ImageObject":
                captions.append(json_ld_data.get('caption'))
        except json.JSONDecodeError:
            print(f"Failed to decode JSON data: {match}")

    # Extract publish date from the article page or its meta information
    publish_date_tag = soup.find('div', {'class': 'gnt_sbt'})
    publish_date = publish_date_tag.get('data-c-dt') if publish_date_tag else None

    # Extract date_published from the article page or its meta information
    date_published_tag = soup.find('div', {'class': 'publish-date'})
    date_published = date_published_tag.get('data-published') if date_published_tag else None

    # Extract date_created from the article page or its meta information
    date_created_tag = soup.find('div', {'class': 'creation-date'})
    date_created = date_created_tag.get('data-created') if date_created_tag else None

    if publish_date:
        # Convert the date string to a datetime object (customize the format as needed)
        publish_date = datetime.strptime(publish_date, '%I:%M %p %b %d').strftime('%Y-%m-%d %H:%M:%S')

    # Extract the author
    author_tag = soup.find('span', class_='gnt_ar_by_l')
    author = author_tag.get_text(strip=True) if author_tag else "No author provided"

    # Extract the main image or video
    media_tag = soup.find('img') or soup.find('video')
    if media_tag and 'src' in media_tag.attrs:
        media_url = urljoin(article_url, media_tag['src'])
    else:
        media_url = None

    # Extract the full content
    content_tag = soup.find('div', class_='gnt_ar_b')
    content_html = str(content_tag) if content_tag else "No content provided"

    # Extract the title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "No title provided"

    return {
        'publish_date': publish_date,
        'author': author,
        'media_url': media_url,
        'content_html': content_html,
        'title': title, 
        'full_html': full_html,
        'date_published': date_published,
        'date_created': date_created,
        'captions': captions
    }

# URL of the Naples News homepage
url = "https://www.naplesnews.com/"

# Fetch the articles
articles = get_articles(url)

# Print each article on a new line
if articles is not None:
    for article in articles:
        print(article['full_html'])