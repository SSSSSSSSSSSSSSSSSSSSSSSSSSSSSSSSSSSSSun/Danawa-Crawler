# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

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

class DanawaCrawler:
    def __init__(self):
        self.errorList = list()
        self.crawlingCategory = list()
        with open(CRAWLING_DATA_CSV_FILE, 'r', newline='') as file:
            for crawlingValues in csv.reader(file, skipinitialspace=True):
                if not crawlingValues[0].startswith(DATA_REMARK):
                    self.crawlingCategory.append({STR_NAME: crawlingValues[0], STR_URL: crawlingValues[1]})


    def StartCrawling(self):
        self.chrome_option = webdriver.ChromeOptions()
        # self.chrome_option.add_argument('--headless')
        self.chrome_option.add_argument('--window-size=1920,1080')
        self.chrome_option.add_argument('--start-maximized')
        self.chrome_option.add_argument('--disable-gpu')
        self.chrome_option.add_argument('lang=ko=KR')
        self.chrome_option.binary_location = "C:/hostedtoolcache/windows/setup-chrome/chromium/131.0.6778.264/x64/chrome.exe"
        if __name__ == '__main__':
            pool = Pool()
            pool.map(self.CrawlingCategory, self.crawlingCategory)
            pool.close()
            pool.join()

          
    
    def CrawlingCategory(self, categoryValue):

        crawlingName = categoryValue[STR_NAME]
        crawlingURL = categoryValue[STR_URL]

        print('Crawling Start : ' + crawlingName)


        retry_count = 0

        while retry_count < MAX_RETRIES:
            # data
            crawlingFile = open(f'{crawlingName}.csv', 'w', newline='', encoding='utf8')
            crawlingData_csvWriter = csv.writer(crawlingFile)
            crawlingData_csvWriter.writerow([self.GetCurrentDate().strftime('%Y-%m-%d %H:%M:%S')])
            
            try:
                browser = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=self.chrome_option)
                browser.implicitly_wait(5)
                browser.get(crawlingURL)

                browser.find_element(By.XPATH,'//option[@value="90"]').click()
                wait = WebDriverWait(browser, 5)
                wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'product_list_cover')))
                                                            
                crawlingSize = browser.find_element(By.CLASS_NAME,'list_num').text.strip()
                crawlingSize = crawlingSize.replace(",","").lstrip('(').rstrip(')')
                crawlingSize = ceil(int(crawlingSize)/90)

                if crawlingSize > 22:
                    crawlingSize = 22
                
                for i in range(0, crawlingSize):

                    print("Start - " + crawlingName + " " + str(i+1) + "/" + str(crawlingSize) + " Page Start")

                    if i == 0:
                        browser.find_element(By.XPATH,'//li[@data-sort-method="NEW"]').click()
                    elif i > 0:
                        if i % 10 == 0:
                            browser.find_element(By.XPATH,'//a[@class="edge_nav nav_next"]').click()
                        else:
                            browser.find_element(By.XPATH,'//a[@class="num "][%d]'%(i%10)).click()
                    wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'product_list_cover')))
                    
                    # Get Product List
                    productListDiv = browser.find_element(By.XPATH,'//div[@class="main_prodlist main_prodlist_list"]')
                    products = productListDiv.find_elements(By.XPATH,'//ul[@class="product_list"]/li')

                    for product in products:
                        if not product.get_attribute('id'):
                            continue

                        # ad
                        if 'prod_ad_item' in product.get_attribute('class').split(' '):
                            continue
                        if product.get_attribute('id').strip().startswith('ad'):
                            continue




                        productName = product.find_element(By.XPATH,'./div/div[2]/p/a').text.strip()
                        productPrices = product.find_elements(By.XPATH,'./div/div[3]/ul/li')
                        productPriceStr = ''

                        for productPrice in productPrices:

                            # Check Hide
                            if 'display: none' in productPrice.get_attribute('style'):
                                # product.find_element(By.XPATH,'./div/div[3]/p/a').click()
                                browser.execute_script("arguments[0].style.display = 'block';", productPrice)

                            # Default
                            productType = productPrice.find_element(By.XPATH,'./div/p').text.strip()

                            # Remove rank text
                            # 1위, 2위 ...
                            productType = self.RemoveRankText(productType)

                            # like Ram/HDD/SSD
                            # HDD : '6TB\n25원/1GB' -> 
                            productTypeList = list()
                            if '\n' in productType:
                                productTypeList = productType.split('\n')
                            else:
                                productTypeList = [productType, ""]
                            
                            mall = productPrice.find_element(By.XPATH,'./p[1]').text.strip()   
                            price = productPrice.find_element(By.XPATH,'./p[2]/a/strong').text.replace(",","").strip()

                            productId = productPrice.get_attribute('id')[18:]

                            crawlingData_csvWriter.writerow([productId, productName, productTypeList[0], price, mall, productTypeList[1]])

                crawlingFile.close()
                break;
                    
            except Exception as e:
                print('Error - ' + crawlingName + ' ->')
                print(traceback.format_exc())
                self.errorList.append(crawlingName)

                crawlingFile.close()

                if retry_count < MAX_RETRIES :
                    retry_count += 1
                    print('Retry ' + str(retry_count) + ' Start : ' + crawlingName)
                    sleep(5)
                else:
                    print('Fail - ' + crawlingName)
                    break

        print('Crawling Finish : ' + crawlingName)

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
                continue

            
            crawl_dataList = list()
            dataList = list()
            

            with open(crawlingDataPath, 'r', newline='', encoding='utf8') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    crawl_dataList.append(row)
            
            if len(crawl_dataList) == 0:
                continue
            
            dataPath = f'{DATA_PATH}/{dataName}.csv'

            if not os.path.exists(dataPath):
                file = open(dataPath, 'w', encoding='utf8')
                file.close()

            self.ResetCsv(dataPath)
            
            firstRow = ['Id', 'Name', 'Type', 'Price', 'Mall']
            firstRow.append(crawl_dataList.pop(0)[0])
            for product in crawl_dataList:
                if not str(product[0]).isdigit():
                    continue
                
                newDataList = ([])
                for i in range(0,len(product)):
                    if i == 0:
                        newDataList.append(int(product[i]))
                    else:
                        newDataList.append(product[i])

                dataList.append(newDataList)
            
            dataList.sort(key= lambda x: x[0])
                
            with open(dataPath, 'w', newline='', encoding='utf8') as file:
                csvWriter = csv.writer(file)
                csvWriter.writerow(firstRow)
                for data in dataList:
                    csvWriter.writerow(data)
                file.close()
                
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
    crawler.CreateIssue()
    # crawler.CsvToXlsx()
    # crawler.CsvToGspread()
    # crawler.CsvToGoogleDrive()



    
