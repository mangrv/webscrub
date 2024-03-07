# config.py
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Define a class to access environment variables
class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    WORDPRESS_SITE = os.getenv("WORDPRESS_SITE")
    WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
    WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")
    POST_TO_WP = os.getenv("POST_TO_WP", "FALSE").lower() == "true"
    # Add more configurations as needed
