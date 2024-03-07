#data_manager.py
import mysql.connector
from mysql.connector import Error
import logging

class DatabaseManager:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            if self.connection.is_connected():
                logging.info("Database connection established.")
                return True
        except Error as e:
            logging.error(f"Failed to connect to database: {e}")
            return False

    def url_exists(self, canonical_url):
        cursor = None
        try:
            cursor = self.connection.cursor()
            query = "SELECT EXISTS(SELECT 1 FROM articles WHERE canonical_url = %s)"
            cursor.execute(query, (canonical_url,))
            return cursor.fetchone()[0]
        except Error as e:
            logging.error(f"Failed to check if URL exists: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def insert_article(self, article_details):
        cursor = None
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO articles (title, author, publish_date, content, excerpt, canonical_url, post_image, source)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                article_details['title'],
                article_details['author'],
                article_details['publish_date'],
                article_details['content'],
                article_details['excerpt'],
                article_details['canonical_url'],
                article_details['post_image'],
                article_details['source']  # This assumes 'source' is a part of article_details
            ))
            self.connection.commit()
            logging.info(f"Article inserted into database: {article_details['title']}")
        except Error as e:
            logging.error(f"Failed to insert article into database: {e}")
        finally:
            if cursor:
                cursor.close()

    def fetch_articles_to_publish(self):
        """Retrieve articles that have not been published to WordPress."""
        cursor = None
        articles_to_publish = []
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM articles WHERE is_published_to_wordpress = 0"
            cursor.execute(query)
            articles_to_publish = cursor.fetchall()
        except Error as e:
            logging.error(f"Failed to retrieve unpublished articles: {e}")
        finally:
            if cursor:
                cursor.close()
        return articles_to_publish

    def mark_article_as_published(self, canonical_url, wp_post_link):
        """Mark the article as published to WordPress in the database."""
        cursor = None
        try:
            cursor = self.connection.cursor()
            query = """UPDATE articles SET is_published_to_wordpress = 1, wordpress_url = %s
                       WHERE canonical_url = %s"""
            cursor.execute(query, (wp_post_link, canonical_url))
            self.connection.commit()
            logging.info(f"Article marked as published: {canonical_url}")
        except Error as e:
            logging.error(f"Failed to mark article as published: {e}")
        finally:
            if cursor:
                cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed.")
