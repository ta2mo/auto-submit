import datetime
import os
import time
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/Profile 1/')

driver = webdriver.Chrome(options=options)

driver.get('https://business.facebook.com/adsmanager/manage/')
time.sleep(5)

now = datetime.date.today()
FILENAME = FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%Y%m%d-%H:%M:%S}.png')
driver.save_screenshot(filename=FILENAME)


time.sleep(5)
driver.quit()
