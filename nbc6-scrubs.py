import requests
from bs4 import BeautifulSoup

# URL of the NBC-2 local news section
url = 'https://www.nbc-2.com/local-news/'

print("Fetching URL:", url)
response = requests.get(url)
print("HTTP Response Status:", response.status_code)

# Check if the request was successful
if response.status_code == 200:
    print("Successfully fetched the webpage.")
    web_content = response.content
    
    # Print the first 500 characters of the fetched HTML
    print("First 500 characters of the fetched HTML:")
    print(web_content[:500])
    
    # Parse the HTML content
    soup = BeautifulSoup(web_content, 'html.parser')
    
    # Debug: Print the title of the webpage to confirm correct parsing
    print("Webpage title:", soup.title.string)
    
    # Assuming each article is contained within an <article> tag
    articles = soup.find_all('article')
    print(f"Found {len(articles)} articles.")
    
    for article in articles:
        # Extract the title and summary
        title = article.find('h2').text.strip()
        summary = article.find('p').text.strip()
        # Optionally, extract the URL of the full article if available
        link = article.find('a')['href']

        # Print the extracted information for debugging
        print(f'Title: {title}\nSummary: {summary}\nLink: {link}\n')
else:
    print("Failed to fetch the webpage.")
