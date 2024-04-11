from scraper_modules.nbc2_scraper.scraper import homepage_localnews_link_extractor as nbc2_extractor, scrape_article_content as nbc2_content
from scraper_modules.abc7_scraper.scraper import homepage_localnews_link_extractor as abc7_extractor, scrape_article_content as abc7_content
from data_processor.processor import DataProcessor
from cms_integration.integrator import post_article


def run_scrapers():
    nbc2_seen_links = set()
    abc7_seen_links = set()
    nbc2_base_url = "https://nbc-2.com"
    abc7_base_url = "https://abc7.com"

    # NBC2
    nbc2_homepage_links, nbc2_seen_links = nbc2_extractor(nbc2_base_url, nbc2_base_url, nbc2_seen_links)
    nbc2_localnews_links, nbc2_seen_links = nbc2_extractor(nbc2_base_url, nbc2_base_url + "/local-news", nbc2_seen_links)

    # ABC7
    abc7_homepage_links, abc7_seen_links = abc7_extractor(abc7_base_url, abc7_base_url, abc7_seen_links)
    abc7_localnews_links, abc7_seen_links = abc7_extractor(abc7_base_url, abc7_base_url + "/local-news", abc7_seen_links)

    all_links = nbc2_homepage_links + nbc2_localnews_links + abc7_homepage_links + abc7_localnews_links
    raw_data = []

    print(f"ABC7 homepage links: {abc7_homepage_links}")
    print(f"ABC7 local news links: {abc7_localnews_links}")

    for link, site, section, subsection, image_url, title in all_links:
        print(f"Site: {site}")
        if site == "nbc2":
            content = nbc2_content(link, image_url)
        else: 
            content = abc7_content(link, image_url)
        print(f"Content: {content}")
        if content is not None:
            content["subsection"] = subsection
            content["site"] = site
            content["title"] = title
            raw_data.append(content)

    processor = DataProcessor(raw_data)
    structured_data = processor.process_data()

    for data in structured_data:
        print(data)
        post_article(data)

if __name__ == "__main__":
    run_scrapers()