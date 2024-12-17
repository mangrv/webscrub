# data_processor/processor.py
import re
from datetime import datetime

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def clean_and_convert_date(self, date_string):
        cleaned_string = date_string.strip().replace('Updated: ', '')
        cleaned_string = re.sub(r'\n|\t', '', cleaned_string)  # Remove newline and tab characters
        cleaned_string = re.sub(r' [A-Z]{3} ', ' ', cleaned_string)  # Remove timezone
        try:
            date_object = datetime.strptime(cleaned_string, '%I:%M %p %b %d, %Y')
        except ValueError:
            print(f"Error: Date string '{cleaned_string}' does not match format '%I:%M %p %b %d, %Y'")
            print(f"Original date string was: '{date_string}'")
            date_object = None  # or some default value
        return date_object  # Return the date as a datetime object

    def format_date_for_strapi(self, date_object):
        return date_object.isoformat()

    def process_data(self):
        print(f"Raw Data: {self.raw_data}")
        structured_data = []
        skipped_articles = 0
        for index, article in enumerate(self.raw_data):
            if "publish_date" in article and article["publish_date"]:
                structured_data.append(self.transform_article(article, index))
            else:
                print(f"Skipping article with no publish date: {article}")
                skipped_articles += 1
        print(f"Structured Data: {structured_data}")
        print(f"Number of articles skipped due to no publish date: {skipped_articles}")
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
        if publish_date is None:
            publish_date = datetime.now()
        formatted_publish_date = publish_date.isoformat()
        article_DateTimeStamp = self.format_date_for_strapi(publish_date)

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
            "is_featured": index == 0,
            "article_DateTimeStamp": article_DateTimeStamp
        }

    def clean_text(self, text):
        cleaned_text = text.strip()
        cleaned_text = cleaned_text.replace('<!-- blocks/ad.twig -->', '')
        return cleaned_text