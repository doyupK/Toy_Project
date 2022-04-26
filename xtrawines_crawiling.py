from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@sparta.eacl0.mongodb.net/sparta?retryWrites=true&w=majority', tlsCAFile=ca) #이동재
db = client.dbsparta

db.xtra_wines.delete_many({})

chrome_options = webdriver.ChromeOptions()
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
    wine_image = wine.select_one('div > div > a > div.prodItem').attrs['style'].split(": url(")[1:][0]
    wine_name = wine.select_one('div > div > a > div.prodName').text
    wine_region = wine.select_one('div > div > a > div.prodZoneDenom').text.strip()

    doc = {
        '와인 사진': wine_image,
        '와인 이름': wine_name,
        '생산지역': wine_region,
    }
    db.xtra_wines.insert_one(doc)















