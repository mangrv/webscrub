from scraper_modules.nbc2_scraper.scraper import homepage_localnews_link_extractor as nbc2_extractor, scrape_article_content as nbc2_content
from data_processor.processor import DataProcessor
from cms_integration.integrator import post_article

def run_nbc2_scraper():
    seen_links = set()
    nbc2_base_url = "https://nbc-2.com"

    nbc2_homepage_links, seen_links = nbc2_extractor(nbc2_base_url, nbc2_base_url + "/", seen_links)
    nbc2_localnews_links, seen_links = nbc2_extractor(nbc2_base_url, nbc2_base_url + "/local-news/", seen_links)

    all_links = nbc2_homepage_links + nbc2_localnews_links
    raw_data = []

    for link, site, section, subsection, image_url, title in all_links:
        content = nbc2_content(link, image_url)
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
    run_nbc2_scraper()