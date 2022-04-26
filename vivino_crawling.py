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
client = MongoClient('mongodb+srv://test:sparta@sparta.eacl0.mongodb.net/sparta?retryWrites=true&w=majority', tlsCAFile=ca) #이동재
db = client.dbsparta

db.vivino_wines.delete_many({})

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.vivino.com/')

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "toplistsBand")))

for i in range(10):
    try:
        i = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[4]/div/div/div[2]/div/div/div/div[2]/div/span[1]/div')
        i.click()
        time.sleep(0.2)
    except NoSuchElementException:
        break

soup = BeautifulSoup(driver.page_source, 'html.parser')

wines = soup.select('#toplistsBand > div > div > div.wineBand__band--GAdsR > div > div > div > div')
for wine in wines:
    wine_image = wine.select_one('div > a > div.wineCard__topSection--11oVj > div.wineCard__bottleSection--3Bzic > img')['src'][2:]
    wine_name = wine.select_one('div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfo__vintage--2wqwE > div.wineInfoVintage__vintage--VvWlU.wineInfoVintage__truncate--3QAtw').text
    wine_maker = wine.select_one('div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfo__vintage--2wqwE > div:nth-child(1)').text
    wine_region = wine.select_one('div > a > div.wineInfo__wineInfo--Sx0T0 > div.wineInfoLocation__wineInfoLocation--BmkcO > div').text

    doc = {
        '와인 사진': wine_image,
        '와인 이름': wine_name,
        '생산자': wine_maker,
        '생산지역': wine_region,
    }
    db.vivino_wines.insert_one(doc)

driver.quit()

