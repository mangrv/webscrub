WebScrub Project
================

Description
-----------

The WebScrub Project is designed to aggregate local news articles by scraping websites that do not offer an RSS feed. This project currently focuses on NBC-2 local news but can be extended to include other sources. It uses Python with libraries such as Requests, BeautifulSoup4, and Selenium for web scraping.

Installation
------------

### Prerequisites

*   Python 3.x
*   pip (Python package manager)

### Libraries Installation

Run the following command to install the necessary libraries:

    pip install requests beautifulsoup4 selenium

**Note:** If you plan to use Selenium, you will also need to download a WebDriver for the browser you intend to use (e.g., ChromeDriver for Google Chrome, geckodriver for Firefox). Please refer to the Selenium documentation for instructions on installing and setting up WebDriver.

### Clone the Repository

To get started with the WebScrub project, clone the repository to your local machine:

    git clone https://github.com/mangrv/webscrub.git
    cd webscrub

Configuration
-------------

Before running the script, ensure you have configured the necessary parameters inside the script. This may include setting up the target URL, configuring the WebDriver path for Selenium, and any other site-specific configurations.

Running the Script
------------------

To run the script, navigate to the project directory and execute the following command:

    python3 nbc6-scrubs.py

Replace `nbc6-scrubs.py` with the script you wish to run. The script will fetch the latest news articles from the configured sources and display or store them according to the script's functionality.

Contributing
------------

Contributions to the WebScrub project are welcome. Please feel free to fork the repository, make changes, and submit pull requests.

Credits
-------

This project was created by the WebScrub team. We thank all contributors for their valuable inputs and feedback.

License
-------

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).