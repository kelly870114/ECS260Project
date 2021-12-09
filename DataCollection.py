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
from pydriller import Repository
from pydriller.metrics.process.change_set import ChangeSet 
from datetime import datetime
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.contributors_count import ContributorsCount
from collections import Counter
from pydriller.metrics.process.lines_count import LinesCount
from pydriller.metrics.process.contributors_experience import ContributorsExperience


options = Options()
#options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
 
browser = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=options)
 
domain = "ios"
browser.get("https://github.com/topics/"+domain+"?o=desc&s=updated")
 

for page in range(1, 10):  # 執行1~2頁

    page_next = browser.find_element_by_xpath('//button[@class="ajax-pagination-btn btn btn-outline color-border-default f6 mt-0 width-full"]')
    page_next.click()  # 點擊下一頁按鈕
 
    time.sleep(5)  # 暫停10秒
    
soup = BeautifulSoup(browser.page_source, "html.parser")
 
# 取得所有class為pull-left infoContent的<li>標籤
elements = soup.find_all("a", {"class": "text-bold wb-break-word"})
urls = []
timeurls = []
#print(f"==========第{str(page)}頁==========")
for element in elements:
    # 取得<li>標籤下的<h3>標籤，再取得<h3>標籤下的<a>標籤文字，並且去掉空白
    title = element.get('href')
    timeurls.append("https://api.github.com/repos%s"%title)
    urls.append("https://github.com%s"%title)
    #print("https://github.com%s"%title)

# print(urls)
for i in range(len(urls)):
    response = requests.get(urls[i])
    soup = BeautifulSoup(response.content, "html.parser")
    
    project_path = urls[i]
    all_commits = list(Repository(project_path).traverse_commits())
    first_commit_hash = all_commits[0].hash
    last_commit_hash = all_commits[-1].hash
    
    if len(all_commits) <= 5000:
        # Print scrap timestamp url
        print(timeurls[i])
        
        #  Print Commits Count
        print('Basic---------')
        #print title
        titleTemp = soup.find('title').get_text()
        title1 = titleTemp.replace('\n','')
        print("Title: ",title1)
        
        #print stars
        starsTemp = soup.find(class_= "social-count js-social-count").get_text()
        stars = starsTemp.replace('\n','')
        print("stars:", stars)

        #print language(primary)
        langTemp = soup.find(class_="d-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3")
        if langTemp:
            lang = langTemp.get_text().replace('\n','')
        else:
            lang = "N/A"
        print("Primary language:", lang)
        
        # print doamin
        print("Domain", domain)
        
        # print commits count
        commits_count_total = len(all_commits)
        print("Commits Count: " + str(commits_count_total))

        # 8.1 Change Set
#         metric = ChangeSet(path_to_repo=project_path,
#                         from_commit=first_commit_hash,
#                         to_commit=last_commit_hash)

#         maximum = metric.max()
#         average = metric.avg()
#         print('8.1---------')
#         # chabge_set_max
#         print('Maximum number of files committed together: {}'.format(maximum))
#         # change_set_avg
#         print('Average number of files committed together: {}'.format(average))


        # 8.3 Commits Count
        metric3 = CommitsCount(path_to_repo=project_path,
                           from_commit=first_commit_hash,
                           to_commit=last_commit_hash)
        files = metric3.count()

        print('8.3---------')
        commits_count_max = max(files.values())
        commits_count_avg = sum(files.values())//len(files)
        print('MAX Commits Count per file: {}'.format(commits_count_max))
        print('AVG Commits Count per file: {}'.format(commits_count_avg))
        # print('Files: {}'.format(files))

        # 8.4 Contributors Count
        metric4 = ContributorsCount(path_to_repo=project_path,
                                from_commit=first_commit_hash,
                                to_commit=last_commit_hash)
        count = metric4.count()
        minor = metric4.count_minor()
        X, Y = Counter(count), Counter(minor)
        norm = dict(X-Y)

        # Contributors Counts per Files_Max
        minor_count_max = max(minor.values())
        norm_count_max = max(norm.values())

        # Contributors Counts per Files_Avg
        minor_count_avg = sum(minor.values())//len(minor)
        norm_count_avg = sum(norm.values())//len(norm)

        print('8.4---------')
        # norm_count_max
        print('MAX Normal Contributors Count per file: {}'.format(norm_count_max))
        # minor_count_max
        print('MAX Minor Contributors Count per file: {}'.format(minor_count_max))

        # norm_count_avg
        print('AVG Norm Contributors Count per file: {}'.format(norm_count_avg))
        # minor_count_avg
        print('AVG Minor Contributors Count per file: {}'.format(minor_count_avg))

#         #8.7 Lines count
#         metric = LinesCount(path_to_repo= project_path,
#                                         from_commit= first_commit_hash,
#                                         to_commit= last_commit_hash)

#         added_count = metric.count_added()
#         added_max = metric.max_added()
#         added_avg = metric.avg_added()

#         print('8.7---------')
#         total_lines_add = sum(added_count.values())
#         max_lines_add = sum(added_max.values())
#         avg_lines_add = sum(added_avg.values())
#         print('Total lines added: ', total_lines_add)
#         print('Maximum lines added: ', max_lines_add)
#         print('Average lines added: ', avg_lines_add)

#         removed_count = metric.count_removed()
#         removed_max = metric.max_removed()
#         removed_avg = metric.avg_removed()
        
#         total_lines_rmv = sum(removed_count.values())
#         max_lines_rmv = sum(removed_max.values())
#         avg_lines_rmv = sum(removed_avg.values())

#         print('Total lines removed:', total_lines_rmv)
#         print('Maximum lines removed:', max_lines_rmv)
#         print('Average lines removed:', avg_lines_rmv)

#         #8.5 Contibutors Experiences
#         metric = ContributorsExperience(path_to_repo=project_path,
#                                         from_commit= first_commit_hash,
#                                         to_commit= last_commit_hash)
#         files = metric.count()
#         sum_ = sum(files.values())
#         num_ = len(files.keys())
#         cont_expr = round(sum_/num_,2)//100
#         print('8.5---------')
#         print("Percentage of the lines authored by the highest contributor:", cont_expr)
#         print()
    
        print()
        # 開啟輸出的 CSV 檔案
        with open('beautifulsoup.csv', 'a+', newline='',encoding='utf-8-sig') as csvfile:
        # 建立 CSV 檔寫入器
            writer = csv.writer(csvfile)
            writer.writerow([timeurls[i], title1, stars, lang, domain, commits_count_total, commits_count_max, commits_count_avg, norm_count_max, minor_count_max, norm_count_avg, minor_count_avg])
            
    else:
        continue
