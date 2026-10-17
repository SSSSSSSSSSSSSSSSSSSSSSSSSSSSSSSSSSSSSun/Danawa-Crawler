# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select

from datetime import datetime
from datetime import timedelta
from pytz import timezone

import csv
import os
import os.path
import shutil
import traceback
from math import ceil
from time import sleep

from multiprocessing import Pool
from danawa_parser import parse_product_rows



#PROCESS_COUNT = 6

CRAWLING_DATA_CSV_FILE = 'CrawlingCategory.csv'
DATA_PATH = 'crawl_data'
DATA_REFRESH_PATH = f'{DATA_PATH}/Last_Data'

TIMEZONE = 'Asia/Seoul'

# CHROMEDRIVER_PATH = 'chromedriver_94.exe'
CHROMEDRIVER_PATH = 'chromedriver.exe'
# CHROMEDRIVER_PATH = 'chromedriver-win64/chromedriver.exe'

DATA_DIVIDER = '---'
DATA_REMARK = '//'
DATA_ROW_DIVIDER = ' - '
DATA_PRODUCT_DIVIDER = '|'
DATA_MALL_DIVIDER = '+'

STR_NAME = 'name'
STR_URL = 'url'
STR_CRAWLING_PAGE_SIZE = 'crawlingPageSize'

MAX_RETRIES = 3

def safe_click(browser, locator, timeout=10):
    element = WebDriverWait(browser, timeout).until(EC.element_to_be_clickable(locator))
    try:
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()
    except Exception as e:
        browser.execute_script("arguments[0].click();", element)

class DanawaCrawler:
    def __init__(self):
        self.errorList = list()
        self.crawlingCategory = list()
        with open(CRAWLING_DATA_CSV_FILE, 'r', newline='') as file:
            for crawlingValues in csv.reader(file, skipinitialspace=True):
                if crawlingValues and not crawlingValues[0].startswith(DATA_REMARK):
                    self.crawlingCategory.append({STR_NAME: crawlingValues[0], STR_URL: crawlingValues[1]})


    def StartCrawling(self):
        self.chrome_option = webdriver.ChromeOptions()
        self.chrome_option.page_load_strategy = 'eager'
        self.chrome_option.add_argument('--headless=new')
        self.chrome_option.add_argument('--window-size=1920,1080')
        self.chrome_option.add_argument('--start-maximized')
        self.chrome_option.add_argument('--disable-gpu')
        self.chrome_option.add_argument('lang=ko=KR')
        if os.environ.get('CHROME_PATH'):
            self.chrome_option.binary_location = os.environ['CHROME_PATH']
        with Pool(processes=2) as pool:
            results = pool.map(self.CrawlingCategory, self.crawlingCategory)
        self.errorList = [category[STR_NAME] for category, success
                          in zip(self.crawlingCategory, results) if not success]
        if self.errorList:
            raise RuntimeError('Crawling failed: ' + ', '.join(self.errorList))

          
    
    def CrawlingCategory(self, categoryValue):

        crawlingName = categoryValue[STR_NAME]
        crawlingURL = categoryValue[STR_URL]

        print('Crawling Start : ' + crawlingName)


        retry_count = 0

        while retry_count < MAX_RETRIES:
            browser = None
            row_count = 0
            # data
            crawlingFile = open(f'{crawlingName}.csv', 'w', newline='', encoding='utf8')
            crawlingData_csvWriter = csv.writer(crawlingFile)
            crawlingData_csvWriter.writerow([self.GetCurrentDate().strftime('%Y-%m-%d %H:%M:%S')])
            
            try:
                driver_path = os.environ.get('CHROMEDRIVER_PATH')
                service = Service(driver_path) if driver_path else Service()
                browser = webdriver.Chrome(service=service, options=self.chrome_option)
                browser.command_executor.set_timeout(45)
                browser.set_page_load_timeout(60)
                browser.implicitly_wait(5)
                browser.get(crawlingURL)

                rows = self.CrawlProductPages(browser)
                crawlingData_csvWriter.writerows(rows)
                row_count = len(rows)

                crawlingFile.close()
                print(f'Crawling Finish : {crawlingName} ({row_count} rows)')
                return True
                    
            except Exception as e:
                print('Error - ' + crawlingName + ' ->')
                print(traceback.format_exc())
                self.SaveDiagnostics(browser, crawlingName)

                crawlingFile.close()

                retry_count += 1
                if retry_count < MAX_RETRIES :
                    print('Retry ' + str(retry_count) + ' Start : ' + crawlingName)
                    sleep(5)
                else:
                    print('Fail - ' + crawlingName)
                    break
            finally:
                crawlingFile.close()
                if browser is not None:
                    try:
                        browser.quit()
                    except Exception:
                        print('Could not close browser')

        return False

    def SaveDiagnostics(self, browser, name):
        os.makedirs('diagnostics', exist_ok=True)
        with open(f'diagnostics/{name}.log', 'w', encoding='utf8') as file:
            file.write(traceback.format_exc())
        if browser is None:
            return
        # Save each independently: a screenshot/title failure must not lose HTML.
        for suffix, operation in [
            ('html', lambda: browser.page_source),
            ('url.txt', lambda: browser.current_url),
            ('title.txt', lambda: browser.title),
            ('png', lambda: browser.save_screenshot(f'diagnostics/{name}.png')),
        ]:
            try:
                value = operation()
                if suffix != 'png':
                    with open(f'diagnostics/{name}.{suffix}', 'w', encoding='utf8') as file:
                        file.write(value)
            except Exception as error:
                print(f'Diagnostic {suffix} failed: {error}')

    def CrawlProductPages(self, browser, max_pages=22):
        wait = WebDriverWait(browser, 45)
        title_locator = (By.CSS_SELECTOR, '#productListArea [data-testid="ProductListTitle"] a')
        wait.until(EC.visibility_of_element_located(title_locator))
        pagination = '//*[@data-testid="ProductListPagination"]'
        wait.until(EC.presence_of_element_located((By.XPATH, pagination)))
        # These controls are hydrated by React after the initial HTML loads.
        sort_locator = (By.XPATH, '//button[normalize-space(.)="신상품순"]')
        safe_click(browser, sort_locator, timeout=30)
        select = wait.until(EC.presence_of_element_located((By.XPATH, '//select[option[@value="90"]]')))
        Select(select).select_by_value('90')
        def page_size_applied(driver):
            if driver.find_elements(By.CSS_SELECTOR, '#productListArea .animate-pulse'):
                return False
            navigation = driver.find_elements(By.XPATH, pagination)
            if not navigation:
                return False
            titles = driver.find_elements(*title_locator)
            # React can briefly retain the original 30-item list after the select
            # reads 90. A short list is valid only when there is a single page.
            more = driver.find_elements(By.XPATH, pagination + '//button[not(@disabled) and (normalize-space(.)="2" or @aria-label="다음 페이지 그룹")]')
            return len(titles) >= 90 or not more
        wait.until(page_size_applied)
        all_rows = {}
        previous_signature = None
        for page in range(1, max_pages + 1):
            # A selected page button alone can update before the product request finishes.
            def ready(driver):
                if driver.find_elements(By.CSS_SELECTOR, '#productListArea .animate-pulse'):
                    return False
                rows = parse_product_rows(driver.page_source)
                signature = tuple(row[0] for row in rows)
                return rows if rows and signature != previous_signature else False

            rows = wait.until(ready)
            # Reveal variants hidden behind the "other configurations" control.
            for button in browser.find_elements(By.XPATH, '//*[@id="productListArea"]//button[starts-with(normalize-space(.),"다른 구성")]'):
                if button.is_displayed():
                    browser.execute_script('arguments[0].click();', button)
            rows = parse_product_rows(browser.page_source)
            if not rows:
                raise RuntimeError(f'No priced products on page {page}')
            previous_signature = tuple(row[0] for row in rows)
            all_rows.update((row[0], row) for row in rows)
            print(f'Page {page}: {len(rows)} price rows', flush=True)
            if page == max_pages:
                break  # Preserve the existing 22-page limit.
            wait.until(EC.presence_of_element_located((By.XPATH, pagination)))
            next_page = browser.find_elements(By.XPATH, pagination + f'//button[normalize-space(.)="{page+1}"]')
            if not next_page:
                next_page = browser.find_elements(By.XPATH, pagination + '//button[@aria-label="다음 페이지 그룹" and not(@disabled)]')
            if not next_page:
                break
            next_page[0].click()
            wait.until(EC.presence_of_element_located((By.XPATH, pagination + f'//button[@aria-current="page" and normalize-space(.)="{page+1}"]')))
        return list(all_rows.values())

    def RemoveRankText(self, productText):
        if len(productText) < 2:
            return productText
        
        char1 = productText[0]
        char2 = productText[1]

        if char1.isdigit() and (1 <= int(char1) and int(char1) <= 9):
            if char2 == '위':
                
                if not len(productText) < 3:
                    char3 = productText[2]
                    if char3 == '\n':
                        return productText[3:].strip()

                return productText[2:].strip()
        
        return productText

    def DataSort(self):
        print('Data Sort')

        for crawlingValue in self.crawlingCategory:
            dataName = crawlingValue[STR_NAME]
            crawlingDataPath = f'{dataName}.csv'
            
            if not os.path.exists(crawlingDataPath):
                raise RuntimeError('Missing crawl data: ' + dataName)

            
            crawl_dataList = list()
            dataList = list()
            

            with open(crawlingDataPath, 'r', newline='', encoding='utf8') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    crawl_dataList.append(row)
            
            if len(crawl_dataList) <= 1:
                raise RuntimeError('Refusing empty data: ' + dataName)
            
            dataPath = f'{DATA_PATH}/{dataName}.csv'

            
            firstRow = ['Id', 'Name', 'Type', 'Price', 'Mall']
            firstRow.append(crawl_dataList.pop(0)[0])
            for product in crawl_dataList:
                if not product or not str(product[0]).isdigit():
                    continue
                
                newDataList = ([])
                for i in range(0,len(product)):
                    if i == 0:
                        newDataList.append(int(product[i]))
                    else:
                        newDataList.append(product[i])

                dataList.append(newDataList)
            
            dataList.sort(key= lambda x: x[0])
            if not dataList:
                raise RuntimeError('Refusing empty data: ' + dataName)
            os.makedirs(DATA_PATH, exist_ok=True)
                
            with open(dataPath + '.tmp', 'w', newline='', encoding='utf8') as file:
                csvWriter = csv.writer(file)
                csvWriter.writerow(firstRow)
                for data in dataList:
                    csvWriter.writerow(data)
                file.close()
            os.replace(dataPath + '.tmp', dataPath)
                
            if os.path.isfile(crawlingDataPath):
                os.remove(crawlingDataPath)


    def ResetCsv(self, crawlingDataPath):
        with open(crawlingDataPath, 'w', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerows([])
    
    def GetCurrentDate(self):
        tz = timezone(TIMEZONE)
        return (datetime.now(tz))

    def CreateIssue(self):
        if len(self.errorList) > 0:
            g = Github(os.environ[GITHUB_TOKEN_KEY])
            repo = g.get_repo(GITHUB_REPOSITORY_NAME)
            
            title = f'Crawling Error - ' + self.GetCurrentDate().strftime('%Y-%m-%d')
            body = ''
            for err in self.errorList:
                body += f'- {err}\n'
            labels = [repo.get_label('bug')]
            repo.create_issue(title=title, body=body, labels=labels)


if __name__ == '__main__':
    crawler = DanawaCrawler()
    crawler.StartCrawling()
    crawler.DataSort()
    # crawler.CsvToXlsx()
    # crawler.CsvToGspread()
    # crawler.CsvToGoogleDrive()



    
