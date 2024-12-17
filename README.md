WebScrub Project
================

Description
-----------

The WebScrub Project is designed to aggregate local news articles by scraping websites that do not offer an RSS feed. This project currently focuses on NBC-2 local news but can be extended to include other sources. It utilizes Python with libraries such as Requests, BeautifulSoup4, and Selenium for web scraping, alongside MySQL for database operations.

Installation
------------

### Prerequisites

*   Python 3.x
*   pip (Python package manager)
*   MySQL Server (for database storage)

### Libraries Installation

Run the following command to install the necessary Python libraries:

pip install requests beautifulsoup4 selenium mysql-connector-python

---OR---
pip3 install -r requirements.txt


#### Note:

If you plan to use Selenium, you will also need to download a WebDriver for the browser you intend to use (e.g., ChromeDriver for Google Chrome, geckodriver for Firefox). Please refer to the Selenium documentation for instructions on installing and setting up WebDriver.

### MySQL Database Setup

Ensure MySQL Server is installed and running. Create a database and user for the WebScrub Project with the necessary permissions:

CREATE DATABASE webscrub;
CREATE USER 'webscrub\_user'@'localhost' IDENTIFIED BY 'your\_password';
GRANT ALL PRIVILEGES ON webscrub.\* TO 'webscrub\_user'@'localhost';
FLUSH PRIVILEGES;
    

### Clone the Repository

To get started with the WebScrub project, clone the repository to your local machine:

git clone https://github.com/mangrv/webscrub.git
cd webscrub

Configuration
-------------

Before running the script, ensure you have configured the necessary parameters inside the script. This includes setting up the target URL, configuring the WebDriver path for Selenium, database connection details, and any other site-specific configurations.

Running the Script
------------------

To run the script, navigate to the project directory and execute the following command:

python main.py

Replace \`main.py\` with the script you wish to run. The script will fetch the latest news articles from NBC2 and display or store them according to the script's functionality.

Docker
------------
docker build -t swfl-webscrub .
docker run -d --name swfl-webscrub swfl-webscrub

check the Dockerfile

Scheduled Service
------------
sudo nano /etc/systemd/system/swfl-webscrub.service

```
[Unit]
Description=SWFL Webscrub Service
After=network.target

[Service]
User=ji
WorkingDirectory=/mnt/user/websites/swfl.io/scripts/webscrub/news_scraper/scheduler
ExecStart=/mnt/user/websites/swfl.io/scripts/webscrub/news_scraper/myenv/bin/python /mnt/user/websites/swfl.io/scripts/webscrub/news_scraper/scheduler/scheduler.py
Restart=always
Environment="PATH=/mnt/user/websites/swfl.io/scripts/webscrub/news_scraper/myenv/bin"

[Install]
WantedBy=multi-user.target
```

Reload systemd and restart the service:
```
sudo systemctl daemon-reload
sudo systemctl restart swfl-webscrub.service
sudo systemctl status swfl-webscrub.service
```





Contributing
------------

Contributions to the WebScrub project are welcome. Please feel free to fork the repository, make changes, and submit pull requests.

Credits
-------

Credits to the following dependencies and their respective teams for making the WebScrub project possible:

*   Requests: HTTP library for Python, allows sending HTTP/1.1 requests
*   BeautifulSoup4: Library for parsing HTML and XML documents
*   Selenium: Tool for automating web browsers
*   MySQL Connector/Python: Self-contained Python driver for communicating with MySQL servers

License
-------

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).