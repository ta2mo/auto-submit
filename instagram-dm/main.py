import configparser
import datetime
import logging
import os
import platform
import sys
import time

from selenium.webdriver.support import expected_conditions

import csv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

# -------------------------------------------------------------------------------------------------
# config
# -------------------------------------------------------------------------------------------------
config = configparser.ConfigParser()
config.read('config.ini')

WAIT_TIME = 3
if 'wait_time' in config:
    WAIT_TIME = config['DEFAULT']['wait_time']

logging.basicConfig(filename='./debug.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logging.debug('start')
logging.debug(f'WAIT_TIME={WAIT_TIME}')

# -------------------------------------------------------------------------------------------------
# csv check
# -------------------------------------------------------------------------------------------------
logging.info('check csv files')
csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'csv')
if not os.path.exists(csv_dir):
    logging.error('指定のディレクトリが存在しません')
    sys.exit(1)

login_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/login_setting.csv')
if not os.path.exists(login_csv_path):
    logging.error('ログイン設定のCSVファイルが存在しません')
    sys.exit(1)

dm_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/dm.csv')
if not os.path.exists(dm_csv_path):
    logging.error('送り先設定のCSVファイルが存在しません')
    sys.exit(1)

login_csv_file = open(login_csv_path, 'r', encoding='utf_8')
login_csv_reader = csv.DictReader(login_csv_file)

dm_csv_file = open(dm_csv_path, 'r', encoding='utf_8')
dm_csv_reader = csv.DictReader(dm_csv_file)

for row in login_csv_reader:
    login_setting = row
    break

logging.info("complete check csv")

# -------------------------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------------------------

options = webdriver.ChromeOptions()

user_data_dir = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/'
profile_directory = '--profile-directory="Profile 1'
if platform.system() == 'Windows':
    logging.info('exec on windows')
    user_data_dir = f'--user-data-dir="{config["DEFAULT"]["windows_profile_dir"]}"'
    profile_directory = f'--profile-directory="{config["DEFAULT"]["profile_directory"]}"'
    options.add_argument(user_data_dir)
    options.add_argument(profile_directory)
    try:
        driver = webdriver.Chrome(options=options, executable_path='.\\driver\\chromedriver-89.exe')
    except Exception as e:
        logging.error(f'get driver failed. {e}')
else:
    logging.info('exec on other os')
    # options.add_argument(user_data_dir)
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logging.error(f'get driver failed. {e}')

driver.get("https://www.instagram.com/accounts/login/")

time.sleep(WAIT_TIME)

driver.find_element_by_name("username").send_keys(login_setting["mailaddress"])
driver.find_element_by_name("password").send_keys(login_setting["password"])
time.sleep(WAIT_TIME)

driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[3]/button").click()
time.sleep(WAIT_TIME)

# ログイン情報を保存しますかポップアップを後で
try:
    notify_element = driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/div/div/button")
    notify_text = notify_element.text
    if notify_text == '後で':
        notify_element.click()
        print('login popup down')
        time.sleep(WAIT_TIME)
except:
    logging.debug("notify popup not found.")

for dm_setting in dm_csv_reader:
    if dm_setting['送信済み']:
        continue

    driver.get("https://www.instagram.com/direct/inbox/")
    time.sleep(WAIT_TIME)

    # 通知ONポップアップを後で
    try:
        notify_element = driver.find_element_by_xpath("/html/body/div[3]/div/div/div/div[3]/button[2]")
        notify_text = notify_element.text
        if notify_text == '後で':
            notify_element.click()
            time.sleep(WAIT_TIME)
    except:
        logging.debug("notify popup not found.")
        # time.sleep(WAIT_TIME)

    driver.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[1]/div[1]/div/div[3]/button").click()
    driver.find_element_by_name("queryBox").send_keys(dm_setting["username"])

    time.sleep(WAIT_TIME)

    # 先頭のユーザーをクリック
    driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[2]/div[1]/div").click()

    # 次へをクリック
    driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]/div/button").click()
    time.sleep(WAIT_TIME)

    # テキスト入力
    text = f"{dm_setting['username']} 様" + dm_setting["文面"].format(name=login_setting["name"], send_to=dm_setting["username"])
    driver.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea").send_keys(text)

    # 送信
    # driver.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[3]/button").click()
