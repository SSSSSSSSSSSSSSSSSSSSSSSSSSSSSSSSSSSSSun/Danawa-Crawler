# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from datetime import datetime
from datetime import timedelta
from pytz import timezone


# 구글 스프레드시트 저장
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread

# {DATA_PATH}/data.xlsx 파일로 저장
# import openpyxl

# googledrive 저장
# import googledrive

# from github import Github

import csv
import os
import os.path
import shutil
import traceback
from math import ceil
from time import sleep

from multiprocessing import Pool



PROCESS_COUNT = 6

# GITHUB_TOKEN_KEY = 'MY_GITHUB_TOKEN'
# GITHUB_REPOSITORY_NAME = 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler'

SHEET_KEYFILE = 'danawa-428617-f6496870d619.json'
SHEET_NAME = 'DanawaData'

CRAWLING_DATA_CSV_FILE = 'CrawlingCategory.csv'
DATA_PATH = 'crawl_data'
DATA_REFRESH_PATH = f'{DATA_PATH}/Last_Data'

TIMEZONE = 'Asia/Seoul'

# CHROMEDRIVER_PATH = 'chromedriver_94.exe'
# CHROMEDRIVER_PATH = 'chromedriver'
CHROMEDRIVER_PATH = 'chromedriver/chromedriver-win64/chromedriver.exe'

DATA_DIVIDER = '---'
DATA_REMARK = '//'
DATA_ROW_DIVIDER = ' - '
DATA_PRODUCT_DIVIDER = '|'
DATA_MALL_DIVIDER = '+'

STR_NAME = 'name'
STR_URL = 'url'
STR_CRAWLING_PAGE_SIZE = 'crawlingPageSize'


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
        self.chrome_option.add_argument('--headless')
        self.chrome_option.add_argument('--window-size=1920,1080')
        self.chrome_option.add_argument('--start-maximized')
        self.chrome_option.add_argument('--disable-gpu')
        self.chrome_option.add_argument('lang=ko=KR')
        if __name__ == '__main__':
            pool = Pool()
            pool.map(self.CrawlingCategory, self.crawlingCategory)
            pool.close()
            pool.join()

          
    
    def CrawlingCategory(self, categoryValue):

        crawlingName = categoryValue[STR_NAME]
        crawlingURL = categoryValue[STR_URL]

        print('Crawling Start : ' + crawlingName)

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


        except Exception as e:
            print('Error - ' + crawlingName + ' ->')
            print(traceback.format_exc())
            self.errorList.append(crawlingName)

        crawlingFile.close()

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
        
    def CsvToXlsx(self):
        print('.csv to .xlsx')

        xlsxDataPath = f'{DATA_PATH}/data.xlsx'
        wb = openpyxl.load_workbook(xlsxDataPath)

        for crawlingValue in self.crawlingCategory:
            dataName = crawlingValue[STR_NAME]
            csvDataPath = f'{DATA_PATH}/{dataName}.csv'
            

            if not os.path.exists(csvDataPath):
                continue
            if not os.path.exists(xlsxDataPath):
                print(xlsxDataPath + ' pass')
                wb = openpyxl.Workbook()
                wb.save(xlsxDataPath)
                wb.close()
            

            # 데이터 초기화를 위해 시트 삭제
            if dataName in wb.sheetnames:
                wb.remove(wb[dataName])

            wb.create_sheet(title=dataName)
            ws = wb[dataName]

            with open(csvDataPath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for r_idx, row in enumerate(reader, 1):
                    for c_idx, value in enumerate(row, 1):
                        ws.cell(row=r_idx, column=c_idx, value=value)

            wb.save(xlsxDataPath)
            
        wb.close()

    def CsvToGspread(self):
        print('.csv to gspread')

        try:
            # 인증 설정
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(SHEET_KEYFILE, scope)
            client = gspread.authorize(creds)

            spreadsheet = client.open(SHEET_NAME)

            sheetList = spreadsheet.worksheets()


        except Exception as e:
            return

        for crawlingValue in self.crawlingCategory:

            dataName = crawlingValue[STR_NAME]
            csvDataPath = f'{DATA_PATH}/{dataName}.csv'
        
            if not os.path.exists(csvDataPath):
                continue

            # 시트 존재 확인
            if any(sheet.title == dataName for sheet in spreadsheet.worksheets()):
                spreadsheet.worksheet(dataName).clear()
            else:
                spreadsheet.add_worksheet(title=dataName, rows='1', cols='1')

            worksheet = spreadsheet.worksheet(dataName)

            with open(csvDataPath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # for r_idx, row in enumerate(reader, 1):
                #     for c_idx, value in enumerate(row, 1):
                #         worksheet.update_acell(r_idx, c_idx, value)

                for row in reader:
                    while True:
                        try:
                            worksheet.append_row(row)
                            break;
                        except gspread.exceptions.APIError as e:
                            if "quota exceeded" in str(e).lower():
                                print("API 제한 초과. 대기 중...")
                                sleep(10)  # 10초 대기
                            else:
                                raise e

    def CsvToGoogleDrive(self):
        print('.csv to googledrive')
        service = googledrive.connectDrive()
        for crawlingValue in self.crawlingCategory:
            dataName = f"{crawlingValue[STR_NAME]}.csv"
            googledrive.uploadFile(service, dataName)


if __name__ == '__main__':
    crawler = DanawaCrawler()
    crawler.StartCrawling()
    crawler.DataSort()
    crawler.CreateIssue()
    # crawler.CsvToXlsx()
    # crawler.CsvToGspread()
    # crawler.CsvToGoogleDrive()



    
