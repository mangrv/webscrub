import unittest
from unittest.mock import patch
from wordpress_manager import WordPressManager

class TestWordPressManager(unittest.TestCase):

    def setUp(self):
        self.wp_manager = WordPressManager("https://example.com", "user", "password", True)

    def test_get_basic_auth_header(self):
        """Test if the authentication header is correctly generated."""
        expected_header = {
            "Authorization": "Basic dXNlcjpwYXNzd29yZA=="
        }
        self.assertEqual(self.wp_manager.get_basic_auth_header(), expected_header)

    @patch('requests.post')
    def test_publish_post_success(self, mock_post):
        """Test publishing a post successfully."""
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'link': 'https://example.com/post/1'}

        post_details = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'excerpt': 'Test excerpt',
            'publish_date': '2024-02-29'
        }

        success, wp_post_link = self.wp_manager.publish_post(post_details)
        self.assertTrue(success)
        self.assertEqual(wp_post_link, 'https://example.com/post/1')

    @patch('requests.post')
    def test_publish_post_failure(self, mock_post):
        """Test handling failure when publishing a post."""
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Server error"

        post_details = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'excerpt': 'Test excerpt',
            'publish_date': '2024-02-29'
        }

        success, wp_post_link = self.wp_manager.publish_post(post_details)
        self.assertFalse(success)
        self.assertIsNone(wp_post_link)

    @patch('requests.get')
    @patch('requests.post')
    def test_upload_image_to_wordpress(self, mock_post, mock_get):
        """Test the image upload functionality."""
        # Simulate fetching image data
        mock_get.return_value.content = b'image data'
        # Simulate successful image upload
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'id': 123}

        image_id = self.wp_manager.upload_image_to_wordpress('https://example.com/image.jpg', self.wp_manager.get_basic_auth_header())
        self.assertEqual(image_id, 123)

if __name__ == '__main__':
    unittest.main()
