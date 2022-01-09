import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def create_web_driver(url):
    # 不打开浏览器的情况下，爬取数据
    options=webdriver.ChromeOptions()
    # 无头模式
    #options.add_argument('--headless')
    # 不加载图片
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
        }
    }
    options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(options=options) # 打开浏览器

    #反屏蔽
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    browser.get(url)
    return browser

def reptilian(browser):
    rankList = []
    nameList=[]
    regionList=[]
    scoreList=[]
    regEx=re.compile("ranking.*")
    pages=34

    for j in range(pages):
        web_data = browser.page_source
        soup=BeautifulSoup(web_data,'lxml')
        # 找到第一个tbody, 再找里面的所有tr，find_all返回元素列表
        table=soup.find("tbody").find_all("tr")
        i=0
        for item in table:
            i=i+1
            # find返回元素
            rank=item.find("div",class_=regEx)
            rankList.append(rank.text.strip())

            name=item.find("div",class_="link-container")
            nameList.append(name.text.strip())

            region=item.select(f"#content-box > div.rk-table-box > table > tbody > tr:nth-child({i}) > td:nth-child(3)")
            regionList.append(region[0].text.strip())
            score=item.select(f"#content-box > div.rk-table-box > table > tbody > tr:nth-child({i}) > td:nth-child(5)")
            scoreList.append(score[0].text.strip())

        Data = pd.DataFrame(columns = ["ranking","name","country","score"])
        Data["ranking"] = rankList
        Data["name"] = nameList
        Data["country"] = regionList
        Data["score"]=scoreList
        # 要导入csv，用此编码，才不会导致中文乱码
        Data.to_csv("world_colleges_dataset.csv", encoding='utf_8_sig')
        # 下一页
        element4 = browser.find_element(By.CSS_SELECTOR, f'#content-box > ul > li.ant-pagination-item.ant-pagination-item-{j+2} > a')
        element4.click()

if __name__ == '__main__':
    browser=create_web_driver('https://www.shanghairanking.cn/rankings/arwu/2021')
    reptilian(browser)
