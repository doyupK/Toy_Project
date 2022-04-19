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

db.vivino_wines.delete_many({})

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.vivino.com/')

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "toplistsBand")))
soup = BeautifulSoup(driver.page_source, 'html.parser')

wine_makers_names = soup.select('.wineInfoVintage__truncate--3QAtw') #list type
wine_regions = soup.select('.wineInfoLocation__regionAndCountry--1nEJz') #list type

wine_makers_names_list = []

wine_makers_list = []
wine_names_list = []
wine_regions_list = []
for i in range(len(wine_makers_names)):
    wine_maker_name = wine_makers_names[i].text
    wine_makers_names_list.append(wine_maker_name)

for i in wine_makers_names_list:
    if wine_makers_names_list.index(i) % 2 == 0:
        wine_makers_list.append(i)
    else:
        wine_names_list.append(i)

for i in range(len(wine_regions)):
    wine_region = wine_regions[i].text
    wine_regions_list.append(wine_region)

for a, b, c in zip(wine_makers_list, wine_names_list, wine_regions_list):
    each_wine = {
        '생산자': a,
        '와인 이름': b,
        '생산 지역': c
    }
    db.vivino_wines.insert_one(each_wine)

driver.quit()

