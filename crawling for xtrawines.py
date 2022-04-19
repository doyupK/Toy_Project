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

wine_names = soup.select('.prodName')
wine_regions = soup.select('.prodZoneDenom')

wine_regions_list = []
wine_names_list = []
for i in range(len(wine_names)):
    wine_name = wine_names[i].text
    wine_names_list.append(wine_name)

for i in range(len(wine_regions)):
    wine_region = wine_regions[i].text.strip()
    wine_regions_list.append(wine_region)

for a, b in zip(wine_names_list, wine_regions_list):
    each_wine = {
        '와인 이름': a,
        '생산 지역': b
    }
    db.xtra_wines.insert_one(each_wine)
