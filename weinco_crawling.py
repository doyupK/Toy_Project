import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.weinco.at/menu/weine/typen/rotweine/search?search=%7B%22page%22%3A1%2C%22pagesize%22%3A%2215%22%2C%22sort%22%3A%22potential%22%2C%22sortdirection%22%3A%22desc%22%2C%22filter%22%3A%7B%22domains%22%3A%5B%22AT%22%5D%2C%22listen%22%3A%5B%22Rotweine%22%5D%7D%2C%22filter_fixed%22%3A%7B%22domains%22%3A%7B%22AT%22%3Atrue%7D%2C%22listen%22%3A%7B%22Rotweine%22%3Atrue%7D%7D%2C%22view%22%3A%22kachel%22%7D&index=produkte',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

# 와인 이름, 이미지 크롤링
wines = soup.select('#produkt-container > div.row > div')
num = 0
for wine in wines:
    num = num + 1
    space_name = wine.select_one('h2 > a').text
    name = space_name.strip()
    img = wine.select_one('div.product-image-wrapper > a > picture > img')['src']
    # img는 db에 저장할 때 아래와 같이 저장 해야 됨.
    image = "https://www.weinco.at" + img

    weinco_detail = wine.select_one('div.product-image-wrapper > a')['href']
    weinco_link = "https://www.weinco.at" + weinco_detail

    price = wine.select_one('div.shipping > span').text
    land = wine.select_one('div.land').text
    region = wine.select_one('div.region').text
    producer = wine.select_one('div.produzent > a').text

    doc = {
        'post_num': num,
        'name': name,
        'land': land,
        'region': region,
        'producer': producer,
        'image': image,
        'price': price,
        'link': weinco_link
    }
    db.wine.insert_one(doc)