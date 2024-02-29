import os
import requests
import logging
import base64

class WordPressManager:
    def __init__(self, wordpress_site, wordpress_username, wordpress_password, post_to_wp):
        self.wordpress_site = wordpress_site
        self.wordpress_username = wordpress_username
        self.wordpress_password = wordpress_password
        self.post_to_wp = post_to_wp

    def get_basic_auth_header(self):
        credentials = f"{self.wordpress_username}:{self.wordpress_password}"
        token = base64.b64encode(credentials.encode()).decode("utf-8")
        return {"Authorization": f"Basic {token}"}

    def publish_post(self, post_details):
        headers = self.get_basic_auth_header()
        # Set the category and tag IDs
        categories = [47]  # Example category ID
        tags = [223]  # Example tag ID

        post_data = {
            "title": post_details['title'],
            "content": post_details['content'],
            "excerpt": post_details['excerpt'],
            "status": "publish",
            "categories": categories,
            "tags": tags,
            "date_gmt": post_details['publish_date'] + 'T00:00:00',
        }

        if 'post_image' in post_details:
            image_id = self.upload_image_to_wordpress(post_details['post_image'], headers)
            if image_id:
                post_data['featured_media'] = image_id

        response = requests.post(f"{self.wordpress_site}/wp-json/wp/v2/posts", headers=headers, json=post_data)
        if response.status_code == 201:
            wp_post_link = response.json().get('link')
            logging.info(f"Post successfully published to WordPress: {wp_post_link}")
            return True, wp_post_link
        else:
            logging.error(f"Failed to publish post to WordPress: {response.status_code}, {response.text}")
            return False, None

    def upload_image_to_wordpress(self, image_url, headers):
        media_endpoint = f"{self.wordpress_site}/wp-json/wp/v2/media"
        image_data = requests.get(image_url).content
        files = {'file': ('filename.jpg', image_data, 'image/jpeg')}
        response = requests.post(media_endpoint, headers=headers, files=files)
        if response.status_code == 201:
            return response.json()['id']
        logging.error("Failed to upload image to WordPress.")
        return None
