from selenium.webdriver.common.by import By
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

db.weinco_wines.delete_many({})
db.weinco_wines_list.delete_many({})

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=2560x1440')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)


# 추천 리스트 크롤링
driver.get('https://www.weinco.at/menu/sale/aktionen/top-aktionen')

soup = BeautifulSoup(driver.page_source, 'html.parser')

wines = soup.select('#produkt-container > div.row > div')
count = 0
for wine in wines:
    count = count + 1
    wine_image = wine.select_one('div > div > div.product-image-wrapper > a > picture > img')['src']
    image_link = "https://www.weinco.at" + wine_image
    wine_name = wine.select_one('div > div > h2 > a').text.strip()
    wine_region = wine.select_one('div > div > div.land > a').text.strip()
    wine_producer = wine.select_one('div > div > div.produzent > a').text
    weinco_detail = wine.select_one('div > div > div.product-image-wrapper > a')['href']
    weinco_link = "https://www.weinco.at" + weinco_detail

    doc = {
        'site': 'weinco_recommend',
        'post_num': count,
        'image': image_link,
        'name': wine_name,
        'region': wine_region,
        'producer': wine_producer,
        'link': weinco_link
    }
    db.weinco_wines.insert_one(doc)

time.sleep(3)

# 와인 리스트 페이지 크롤링

driver.get('https://www.weinco.at/menu/weine/search?search=%7B%22page%22%3A1%2C%22pagesize%22%3A15%2C%22sort%22%3A%22avg_rating%22%2C%22sortdirection%22%3A%22desc%22%2C%22filter%22%3A%7B%22domains%22%3A%5B%22AT%22%5D%2C%22listen%22%3A%5B%22Alle+Weine%22%5D%7D%2C%22filter_fixed%22%3A%7B%22domains%22%3A%7B%22AT%22%3Atrue%7D%2C%22listen%22%3A%7B%22Alle+Weine%22%3Atrue%7D%7D%2C%22view%22%3A%22kachel%22%7D&index=produkte')

time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')

count = 0
page_count = 2
for page in range(1, 6):
    driver.implicitly_wait(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = soup.select('#produkt-container > div.row > div')
    for post in posts:
        # print(post)
        # 고유 번호(Key)
        count = count + 1
        img = post.select_one('div > div.product-image-wrapper > a > picture > img')['src']
        # img는 db에 저장할 때 아래와 같이 저장 해야 됨.
        image = "https://www.weinco.at" + img
        space_name = post.select_one('div > h2 > a').text
        name = space_name.strip()
        weinco_detail = post.select_one('div > div.product-image-wrapper > a')['href']
        weinco_link = "https://www.weinco.at" + weinco_detail
        land = post.select_one('div > div.land > a').text
        producer = post.select_one('div > div.produzent > a').text
        doc = {
            'site': 'weinco_list',
            'post_num': count,
            'image': image,
            'name': name,
            'land': land,
            'producer': producer,
            'link': weinco_link
        }
        db.weinco_wines_list.insert_one(doc)
    driver.execute_script('window.scrollTo(0, -600);')
    time.sleep(1)
    i = driver.find_element(by=By.XPATH,
                            value='/html/body/div[4]/section/div/div/div[2]/div[1]/div[3]/span[1]/a['+str(page_count)+']')
    i.click()
    time.sleep(3)
    if page_count == 2:
        page_count = page_count + 2
    elif page_count == 4:
        page_count = page_count + 1
    elif page_count == 5:
        page_count = page_count + 1
    elif page_count == 6:
        page_count = page_count

driver.quit()
