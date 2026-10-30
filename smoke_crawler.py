"""Read-only live smoke test; never publishes or rewrites crawl_data."""
import os
import argparse
from selenium import webdriver
from danawa_crawler import DanawaCrawler


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=2)
    parser.add_argument('--category', default=None)
    args = parser.parse_args()
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    if os.environ.get('CHROME_PATH'):
        options.binary_location = os.environ['CHROME_PATH']
    crawler = DanawaCrawler()
    for category in crawler.crawlingCategory:
        if args.category and category['name'] != args.category:
            continue
        with webdriver.Chrome(options=options) as browser:
            browser.command_executor.set_timeout(45)
            browser.set_page_load_timeout(60)
            try:
                crawler.OpenCategory(browser, category['url'])
                rows = crawler.CrawlProductPages(browser, max_pages=args.pages)
                assert rows and all(row[0].isdigit() and int(row[3]) > 0 for row in rows)
                print(f"Smoke OK: {category['name']}, {len(rows)} rows", flush=True)
            except Exception:
                crawler.SaveDiagnostics(browser, 'smoke')
                raise
