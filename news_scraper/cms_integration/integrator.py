# integrator.py
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

def post_article(data):
    api_url = os.getenv('STRAPI_API_URL')
    bearer_token = os.getenv('STRAPI_BEARER_TOKEN')

    print(f"API URL: {api_url}")
    print(f"Bearer Token: {bearer_token}")

    if api_url is None:
        print('STRAPI_API_URL environment variable is not')
        return

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    print(data.keys())
    print(f"Data Keys: {data.keys()}")

    site_mapping = {"WZVN": "ABC-7", "WBBH": "NBC-2"}

    if 'title' in data and 'slug' in data and 'content' in data and 'image_url' in data and 'author' in data and 'site' in data and 'original_url' in data and 'publish_date' in data and 'article_DateTimeStamp' in data:
        site = site_mapping.get(data['site'].upper(), data['site'])

        api_data = {
            'article_title': data['title'],
            'slug': data['slug'],
            'article_content': data['content'],
            'article_scraped_image_url': data['image_url'],
            'article_author': data['author'].strip(),
            'article_is_featured': data['is_featured'],
            'article_category': site, 
            'article_source_url': data['original_url'],
            'article_posted_date': data['publish_date'].strip(),
            'article_DateTimeStamp': data['article_DateTimeStamp'],
            # 'SEO': data['SEO'],
            # 'keywords': data['keywords'],
            # 'preventIndexing': data['preventIndexing'],
        }

        print(f"API Data: {api_data}")

        response = requests.post(api_url, headers=headers, json={'data': api_data})

        if response.status_code == 201:
            print('Article posted successfully')
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
        else:
            print('Failed to post article', response.status_code, response.text)
    else:
        print('Missing required keys in data')