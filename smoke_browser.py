"""Verify the browser pair supplied by CI before starting the full crawl."""

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def main():
    chrome_path = os.environ['CHROME_PATH']
    driver_path = os.environ['CHROMEDRIVER_PATH']
    for path in (chrome_path, driver_path):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    print(f'Chrome: {chrome_path}', flush=True)
    print(f'ChromeDriver: {driver_path}', flush=True)
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument('--headless=new')
    with webdriver.Chrome(service=Service(driver_path), options=options) as browser:
        print(f"Browser version: {browser.capabilities['browserVersion']}")
        print(f"Driver version: {browser.capabilities['chrome']['chromedriverVersion']}")
        browser.get('data:text/html,<title>browser-check</title>')
        if browser.title != 'browser-check':
            raise RuntimeError('Browser navigation check failed')


if __name__ == '__main__':
    main()
