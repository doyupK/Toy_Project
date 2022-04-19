from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import re
from selenium.common.exceptions import TimeoutException
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.vivino.com/')


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "toplistsBand")))
soup = BeautifulSoup(driver.page_source, 'html.parser')

wine_makers_names_list = []
wine_makers_list = []
wine_names_list = []
wine_regions_list = []

wine_makers_names = soup.select('.wineInfoVintage__truncate--3QAtw') #list type
wine_regions = soup.select('.wineInfoLocation__regionAndCountry--1nEJz') #list type

for i in range(len(wine_makers_names)):
    wine_maker_name = wine_makers_names[i].text
    wine_makers_names_list.append(wine_maker_name)

for i in range(len(wine_regions)):
    wine_region = wine_regions[i].text
    wine_regions_list.append(wine_region)

for i in wine_makers_names_list:
    if wine_makers_names_list.index(i) % 2 == 0:
        wine_makers_list.append(i)
    else:
        wine_names_list.append(i)

print(wine_names_list)

driver.quit()