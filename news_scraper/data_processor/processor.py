# data_processor/processor.py
import re
from datetime import datetime

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def clean_and_convert_date(self, date_string):
        cleaned_string = date_string.strip().replace('Updated: ', '')
        date_object = datetime.strptime(cleaned_string, '%I:%M %p %Z %b %d, %Y')
        return date_object

    def process_data(self):
        print(f"Raw Data: {self.raw_data}")
        structured_data = [self.transform_article(article, index) for index, article in enumerate(self.raw_data)]
        print(f"Structured Data: {structured_data}")
        return structured_data
    
    def create_slug(self, title):
        title = title.lower()
        title = re.sub(r'[^\x00-\x7F]+', '', title)
        title = re.sub(r'[!@#$%^&*()=+[\]{};:\'",.<>?/\\]', '', title)
        title = title.replace(' ', '-')
        title = re.sub(r'[^\w\s-]', '', title)
        stop_words = ['and', 'or', 'but', 'the', 'a', 'in']
        title = '-'.join(word for word in title.split('-') if word not in stop_words)
        return title

    def transform_article(self, article, index):
        publish_date = self.clean_and_convert_date(article["publish_date"])
        formatted_publish_date = publish_date.isoformat()

        return {
            "title": self.clean_text(article["title"]),
            "content": self.clean_text(article["content"]),
            "author": self.clean_text(article["author"]),
            "publish_date": formatted_publish_date,
            "image_url": self.clean_text(article["image_url"]),
            "original_url": article["url"],
            "slug": self.create_slug(article["title"]),
            "subsection": article["subsection"], 
            "site": article["site"],
            "is_featured": index == 0
        }

    def clean_text(self, text):
        cleaned_text = text.strip()
        cleaned_text = cleaned_text.replace('<!-- blocks/ad.twig -->', '')
        return cleaned_text