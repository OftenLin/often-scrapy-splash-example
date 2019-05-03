 # -*- coding: utf-8 -*-
from scrapy import Spider as Spider
from scrapy import Request as Request
from selenium import webdriver
import time
import csv
import os

from items import FscFinanicalDictionaryItem


CHROME_DRIVER_PATH = '<your chromedriver path>'
class ToScrapeSpiderXPath(Spider):
    name = 'fsc_financial_project'
    start_urls = ['https://www.fsc.gov.tw/ch/home.jsp?id=178&parentpath=0,6&mcustomize=bilingual_list.jsp']
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection':'keep-alive',
        'Cookie':'HttpOnly; cookiesession1=59F531CCSYUK9GPQDATIRXKLPN9UB47B; HttpOnly',
        'Upgrade-Insecure-Requests':'1',
    }
    

    def parse(self, response):
        for url in self.start_urls:
            yield Request(url, headers=self.headers, callback=self.test)

    def test(self, response):
        all_items = []
        total_page = int(response.xpath(".//span[@class='page']/text()").get().split('/')[1].strip())
        for row in response.xpath('.//div[@class="whitebackground7"]'):
            item = FscFinanicalDictionaryItem()
            item['order_num'] = row.xpath('.//div[@class="bicode_con"]/text()').extract_first()
            item['category'] = row.xpath('.//div[@class="bitype_con"]/text()').extract_first()
            item['chinese'] = row.xpath('.//div[@class="bich_name_con"]/text()').extract_first()
            item['english'] = row.xpath('.//div[@class="bien_name_con"]/text()').extract_first()
            item['source'] = row.xpath('.//div[@class="bisource_con"]/text()').extract_first()
            all_items.append(item)


        driver = webdriver.Chrome(CHROME_DRIVER_PATH)
        driver.get(response.url)
        time.sleep(1)
        for page in range(2, total_page+1):
            driver.execute_script('list(%s)' % page)
            time.sleep(0.5)
            for row in driver.find_elements_by_xpath('.//div[@class="whitebackground7"]'):
                item = FscFinanicalDictionaryItem()
                item['order_num'] = row.find_element_by_xpath('.//div[@class="bicode_con"]').text
                item['category'] = row.find_element_by_xpath('.//div[@class="bitype_con"]').text
                item['chinese'] = row.find_element_by_xpath('.//div[@class="bich_name_con"]').text
                item['english'] = row.find_element_by_xpath('.//div[@class="bien_name_con"]').text
                item['source'] = row.find_element_by_xpath('.//div[@class="bisource_con"]').text
                all_items.append(item)

        with open('fsc_financial_dictionary.csv', 'w', encoding='big5') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            csv_header_list = ['編號', '分類', '中文詞彙', '英文詞彙', '資料來源']
            writer.writerow(csv_header_list)
            
            for item in all_items:
                item = {k: str(v) for (k, v) in item.items()}
                writer.writerow([item['order_num'], item['category'], 
                item['chinese'].replace('倂', '併') if '倂' in item['chinese'] else item['chinese'],
                item['english'],
                item['source']])
           
