from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
import certifi
import time

ca = certifi.where()
# client = MongoClient('mongodb+srv://test:sparta@sparta.eacl0.mongodb.net/sparta?retryWrites=true&w=majority', tlsCAFile=ca) #이동재
client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)  # DY
db = client.dbsparta

db.vivino_wines.delete_many({})
db.vivino_wines_list.delete_many({})

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')

chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")

driver = webdriver.Chrome(options=chrome_options)
# 추천 리스트 크롤링
driver.get('https://www.vivino.com/')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "toplistsBand")))

for i in range(10):
    try:
        i = driver.find_element(by=By.XPATH,
                                value='/html/body/div[2]/div[4]/div/div/div[2]/div/div/div/div[2]/div/span[1]/div')
        i.click()
        time.sleep(0.2)
    except NoSuchElementException:
        break

soup = BeautifulSoup(driver.page_source, 'html.parser')

wines = soup.select('#toplistsBand > div > div > div.wineBand__band--GAdsR > div > div > div > div')
count = 0
for wine in wines:
    # 고유번호(Key) 생성
    count = count + 1
    image = wine.select_one('div > a > div > div.wineCard__bottleSection--3Bzic > img')['src'][2:]
    wine_image = "https://" + image
    wine_name = wine.select_one(
        'div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfo__vintage--2wqwE > div.wineInfoVintage__vintage--VvWlU.wineInfoVintage__truncate--3QAtw').text
    wine_maker = wine.select_one(
        'div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfo__vintage--2wqwE > div:nth-child(1)').text
    wine_region = wine.select_one(
        'div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoLocation__wineInfoLocation--BmkcO > div').text
    wine_link = wine.select_one(
        'div > a')['href']

    doc = {
        'site': 'vivino_recommend',
        'post_num': count,
        'image': wine_image,
        'name': wine_name,
        'producer': wine_maker,
        'region': wine_region,
        'link': 'https://vivino.com' + wine_link
    }
    db.vivino_wines.insert_one(doc)

# 와인 리스트 페이지 크롤링

SCROLL_PAUSE_TIME = 1

driver.get(
    'https://www.vivino.com/explore?e=eJzLLbI11rNQy83MszU0AAK13MQKWxMwK7nS1jtILRlIhKsV2BqqpafZliUWZaaWJOao5Rel2KrlJ1XaqpWXRMcCJcGUEQCDaRfR/')
#
driver.implicitly_wait(5)
# 초기 창 높이 값
last_height = driver.execute_script("return document.body.scrollHeight")
#
y = 0
while 1:

    # 스크롤
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, window.scrollY + 1000);")
    time.sleep(SCROLL_PAUSE_TIME)

    # 스크롤 전의 창 높이와 스크롤 후 창의 높이 비교
    new_height = driver.execute_script("return document.body.scrollHeight")
    time.sleep(SCROLL_PAUSE_TIME)
    if new_height == last_height:
        break

    last_height = new_height

soup = BeautifulSoup(driver.page_source, 'html.parser')

posts = soup.select(
    '#explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__results--3wqLw > div > div')
count = 0
for post in posts:
    # 고유 번호(Key)
    count = count + 1
    image = post.select_one('div > a > div > div > img')['src'][2:]
    wine_image = "https://" + image
    wine_name = post.select_one(
        'div > a > div > div.wineCard__infoColumn--3NKrN > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfoVintage__large--OaWjm.wineInfo__vintage--2wqwE > div.wineInfoVintage__vintage--VvWlU.wineInfoVintage__truncate--3QAtw').text
    wine_maker = post.select_one(
        'div > a > div > div.wineCard__infoColumn--3NKrN > div > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfoVintage__large--OaWjm.wineInfo__vintage--2wqwE > div').text
    wine_region = post.select_one(
        'div > a > div > div.wineCard__infoColumn--3NKrN > div > div.wineInfoLocation__wineInfoLocation--BmkcO > div').text
    wine_link = post.select_one(
        'div > a')['href']

    doc = {
        'site': 'vivino_list',
        'post_num': count,
        'image': wine_image,
        'name': wine_name,
        'producer': wine_maker,
        'region': wine_region,
        'link': 'https://vivino.com' + wine_link
    }
    db.vivino_wines_list.insert_one(doc)

driver.quit()
