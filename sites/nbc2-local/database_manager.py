import os
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

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed.")

    def update_post_publish_status(self, canonical_url, wordpress_url):
        if not self.connection or not self.connection.is_connected():
            logging.error("Database connection is not established.")
            return False

        try:
            cursor = self.connection.cursor()
            query = """UPDATE articles SET is_published_to_wordpress = %s, wordpress_url = %s WHERE canonical_url = %s"""
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
