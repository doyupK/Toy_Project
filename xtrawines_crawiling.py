from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
import certifi
import time
import subprocess

subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"') # 디버거 크롬 구동

ca = certifi.where()
# client = MongoClient('mongodb+srv://test:sparta@sparta.eacl0.mongodb.net/sparta?retryWrites=true&w=majority', tlsCAFile=ca) #이동재
client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca) #DY
db = client.dbsparta


db.xtra_wines.delete_many({})
db.xtra_wines_list.delete_many({})

chrome_options = webdriver.ChromeOptions()
# xtrawine은 셀레니움 사용 시 봇 체크 프로그램으로 인해 페이지 이동 불가 -> 디버그모드로 봇체크 우회
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.xtrawine.com/en')

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "col-sm-push-2.col-sm-10.slider-row")))
soup = BeautifulSoup(driver.page_source, 'html.parser')

wines = soup.select('#RootLayout_PageLayout_UpperPane_Frame2811_Module2811_pnlWlcTop > div.container > div:nth-child(1) > div.col-sm-push-2.col-sm-10.slider-row > div > div > div > div > div')
for wine in wines:

    wine_image = wine.select_one('div > div > a > div.prodItem')['style'].split(": url(")[1:][0]
    wine_name = wine.select_one('div > div > a > div.prodName').text
    wine_region = wine.select_one('div > div > a > div.prodZoneDenom').text.strip()
    xtra_detail = wine.select_one('div > div > a')['href']
    xtra_link = "https://www.xtrawine.com" + xtra_detail

    doc = {
        'site': 'xtra_recommend',
        'image': wine_image,
        'name': wine_name,
        'region': wine_region,
        'link': xtra_link
    }
    db.xtra_wines.insert_one(doc)

# 와인 리스트 페이지 크롤링

SCROLL_PAUSE_TIME = 1

driver.get('https://www.xtrawine.com/en/wines/red-best-sellers/195+2080')
time.sleep(3)

count = 0
page_count = 3
for page in range(5):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = soup.select(
        '#RootLayout_PageLayout_WhiteZoneTopRight_Frame1648_ModuleAreaNoFrame > div.products-list > div')
    for post in posts:
        # 고유 번호(Key)
        count = count + 1
        wine_image = post.select_one('div > div.col-sm-2.col-xs-3 > div > div > a > img')['src']
        wine_name = post.select_one('div > div.col-sm-6.col-xs-9.item-content.clearfix > div.item-title > div > a').text
        wine_maker = post.select_one('div > div.col-sm-6.col-xs-9.item-content.clearfix > div.item-top-title > div > a').text
        xtra_detail = post.select_one('div > div.col-sm-6.col-xs-9.item-content.clearfix > div.item-title > div > a')['href']
        xtra_link = "https://www.xtrawine.com" + xtra_detail
        doc = {
            'site': 'xtra_list',
            'post_num': count,
            'image': wine_image,
            'name': wine_name,
            'producer': wine_maker,
            'link': xtra_link
        }
        db.xtra_wines_list.insert_one(doc)

    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(SCROLL_PAUSE_TIME)
    i = driver.find_element(by=By.XPATH,
                            value='/html/body/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div/div/div/div/div/div[3]/nav/ul/li['+str(page_count)+']/a')
    i.click()
    time.sleep(2)
    page_count = page_count + 1

driver.quit()
