from unittest.mock import MagicMock, patch, PropertyMock
import unittest
from scraper import Scraper

class TestScraper(unittest.TestCase):
    @patch('selenium.webdriver.Chrome')
    def setUp(self, MockWebDriver):
        self.mock_driver = MockWebDriver()
        self.scraper = Scraper(self.mock_driver)

    @patch('selenium.webdriver.support.ui.WebDriverWait')
def test_get_post_content_success(self, MockWebDriverWait):
    mock_wait = MockWebDriverWait.return_value
    mock_wait.until.return_value = None  # Assume until doesn't need to return a specific value

    # Simplify mocking to focus on critical elements
    mocked_element = MagicMock()
    type(mocked_element).text = PropertyMock(side_effect=['Test Title', 'Test Content', 'Test Excerpt'])
    self.mock_driver.find_element.return_value = mocked_element
    self.mock_driver.find_elements.return_value = [mocked_element]  # Assume it finds image element

    post_details = self.scraper.get_post_content('http://example.com/post')

    self.assertIsNotNone(post_details, "post_details should not be None")
    self.assertEqual(post_details['title'], 'Test Title', "Title does not match")
    # Further assertions...


        # Mock the find_element method to return an element with a text attribute
        mocked_element_title = MagicMock()
        type(mocked_element_title).text = PropertyMock(return_value='Test Title')
        mocked_element_img = MagicMock(get_attribute=MagicMock(return_value='http://example.com/image.jpg'))
        
        # Mock find_element and find_elements to return the mocked elements
        self.mock_driver.find_element.side_effect = [mocked_element_title, mocked_element_img]
        self.mock_driver.find_elements.side_effect = lambda *args, **kwargs: [] if 'h2.article-headline--subheadline' in args[0] else [mocked_element_img]

        post_details = self.scraper.get_post_content('http://example.com/post')

        # Assertions to verify the returned content matches expectations
        self.assertIsNotNone(post_details)
        self.assertEqual(post_details['title'], 'Test Title')
        self.assertEqual(post_details['content'], 'Test Title')
        self.assertEqual(post_details['excerpt'], '')
        self.assertEqual(post_details['post_image'], 'http://example.com/image.jpg')
        self.assertTrue('publish_date' in post_details)
        self.assertTrue('canonical_url' in post_details)

if __name__ == '__main__':
    unittest.main()
