from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
from urllib.request import urlopen
import requests
import pprint
import re

 
 
options = Options()
#options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
 
browser = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=options)
 
browser.get("https://github.com/topics/android")
 

 
for page in range(1, 3):  # 執行1~2頁

    page_next = browser.find_element_by_xpath('//button[@class="ajax-pagination-btn btn btn-outline color-border-default f6 mt-0 width-full"]')
    page_next.click()  # 點擊下一頁按鈕
 
    time.sleep(5)  # 暫停10秒
    
soup = BeautifulSoup(browser.page_source, "html.parser")
 
# 取得所有class為pull-left infoContent的<li>標籤
elements = soup.find_all("a", {"class": "text-bold wb-break-word"})
urls = []
#print(f"==========第{str(page)}頁==========")
for element in elements:
    # 取得<li>標籤下的<h3>標籤，再取得<h3>標籤下的<a>標籤文字，並且去掉空白
    title = element.get('href')
    urls.append("https://github.com%s"%title)
    #print("https://github.com%s"%title)

print(urls)
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    #print title
    titleTemp = soup.find('title').get_text()
    title = titleTemp.replace('\n','')
    #print("Title: ",title)
    
    #print stars
    starsTemp = soup.find(class_= "social-count js-social-count").get_text()
    stars = starsTemp.replace('\n','')
    #print("stars:", stars)
    
    
    #print language(primary)
    langTemp = soup.find(class_="d-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3")
    if langTemp:
        lang = langTemp.get_text().replace('\n','')
    else:
        lang = "N/A"
    #print("Primary language:", lang)

    # 開啟輸出的 CSV 檔案
    with open('beautifulsoup.csv', 'a+', newline='',encoding='utf-8-sig') as csvfile:
    # 建立 CSV 檔寫入器
        writer = csv.writer(csvfile)
        writer.writerow([title, stars, lang])
