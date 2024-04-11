from scraper_modules.abc7_scraper.scraper import homepage_localnews_link_extractor as abc7_extractor, scrape_article_content as abc7_content
from data_processor.processor import DataProcessor
from cms_integration.integrator import post_article

def run_abc7_scraper():
    seen_links = set()
    abc7_base_url = "https://abc-7.com"

    abc7_homepage_links, seen_links = abc7_extractor(abc7_base_url, abc7_base_url + "/", seen_links)
    abc7_localnews_links, seen_links = abc7_extractor(abc7_base_url, abc7_base_url + "/local-news/", seen_links)

    all_links = abc7_homepage_links + abc7_localnews_links
    raw_data = []

    for link, site, section, subsection, image_url, title in all_links:
        content = abc7_content(link, image_url)
        if content is not None: 
            content["subsection"] = subsection
            content["site"] = site
            content["title"] = title
            print(f"Content: {content}")
            raw_data.append(content)
    print(f"Raw Data: {raw_data}")

    print("Processing data...")
    processor = DataProcessor(raw_data)
    structured_data = processor.process_data()
    print(f"Structured Data: {structured_data}")
    print("Data processed.")

    print("Posting articles...")
    for data in structured_data:
        print(f"Posting article: {data['title']}")
        post_article(data)
    print("Articles posted.")

if __name__ == "__main__":
    run_abc7_scraper()