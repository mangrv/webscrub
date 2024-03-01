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
        """Establish a connection to the database."""
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
        """Check if the given URL already exists in the database."""
        if not self.connection or not self.connection.is_connected():
            logging.error("Database connection is not established.")
            return False

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
        """Insert a new article into the database."""
        if not self.connection or not self.connection.is_connected():
            logging.error("Database connection is not established.")
            return False

        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO articles (title, author, publish_date, content, excerpt, canonical_url, post_image, is_published_to_wordpress, wordpress_url)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                article_details['title'],
                article_details.get('author', ''),
                article_details.get('publish_date', None),
                article_details['content'],
                article_details.get('excerpt', ''),
                article_details['canonical_url'],
                article_details.get('post_image', ''),
                0,
                ''
            ))
            self.connection.commit()
            logging.info(f"Article inserted into database: {article_details['title']}")
            return True
        except Error as e:
            logging.error(f"Failed to insert article into database: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update_post_publish_status(self, canonical_url, wordpress_url):
        """Update the post publish status and WordPress URL for an article."""
        if not self.connection or not self.connection.is_connected():
            logging.error("Database connection is not established.")
            return False

        try:
            cursor = self.connection.cursor()
            query = "UPDATE articles SET is_published_to_wordpress = %s, wordpress_url = %s WHERE canonical_url = %s"
            cursor.execute(query, (1, wordpress_url, canonical_url))
            self.connection.commit()
            logging.info(f"Post publish status and WordPress URL updated for {canonical_url}")
            return True
        except Error as e:
            logging.error(f"Failed to update post publish status: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed.")
