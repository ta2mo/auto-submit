import logging
import os
import platform
import sys
import time
import datetime

import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# -------------------------------------------------------------------------------------------------
# config
# -------------------------------------------------------------------------------------------------
WAIT_TIME = 3

logging.basicConfig(filename='./debug.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logging.debug('start')
logging.debug(f'WAIT_TIME={WAIT_TIME}')

# -------------------------------------------------------------------------------------------------
# temp dir check
# -------------------------------------------------------------------------------------------------
try:
    temp_dir = os.environ['TEMP']
    if os.path.exists(temp_dir):
        logging.debug(f"temp_dir exists. path={temp_dir}")
    else:
        logging.debug(f"temp_dir not exists. path={temp_dir}")
        os.mkdir(temp_dir)
except:
    logging.debug('TEMPは設定されていません')
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.environ['TEMP'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

try:
    tmp_dir = os.environ['TMP']
    if os.path.exists(tmp_dir):
        logging.debug(f"tmp_dir exists. path={tmp_dir}")
    else:
        logging.debug(f"tmp_dir not exists. path={tmp_dir}")
        os.makedirs(tmp_dir, exist_ok=True)
except:
    logging.debug('環境変数TMPは設定されていません')
    tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    os.environ['TMP'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

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

# ヘッダー
HEADER_SEND_RESULT = "送信済み"
HEADER_USERNAME = 'username（半角英数と_のみのやつ）'
HEADER_NAME = '名前（メッセージ内の宛名の置き換え）'
HEADER_MESSAGE = 'メッセージテンプレート'

HEADER_NO = "No"
HEADER_INSTAGRAM_URL = "インスタURL"

# -------------------------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------------------------

options = webdriver.ChromeOptions()

user_data_dir = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/'
profile_directory = '--profile-directory="Profile 1'
if platform.system() == 'Windows':
    logging.info('exec on windows')
    try:
        driver = webdriver.Chrome(options=options, executable_path='.\\driver\\chromedriver-89.exe')
    except Exception as e:
        logging.error(f'get driver failed. {e}')
else:
    logging.info('exec on other os')
    try:
        driver = webdriver.Chrome(options=options, executable_path='./driver/chromedriver-89')
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

result_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/result.csv')
result_csv_file = open(result_csv_path, 'w', encoding='utf_8')
result_csv_writer = csv.DictWriter(result_csv_file,
                                   [HEADER_NO, HEADER_NAME, HEADER_INSTAGRAM_URL, HEADER_USERNAME, HEADER_MESSAGE,
                                    HEADER_SEND_RESULT], quotechar='"',
                                   quoting=csv.QUOTE_ALL)

result_list = []
skip_all = False

for dm_setting in dm_csv_reader:
    if dm_setting[HEADER_SEND_RESULT] or skip_all:
        result_list.append(dm_setting)
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

    try:
        driver.find_element_by_xpath(
            "/html/body/div[1]/section/div/div[2]/div/div/div[1]/div[1]/div/div[3]/button").click()
        driver.find_element_by_name("queryBox").send_keys(dm_setting[HEADER_USERNAME])

        time.sleep(WAIT_TIME)

        # 先頭のユーザーをクリック
        driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[2]/div[1]/div").click()

        # 次へをクリック
        driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]/div/button").click()
        time.sleep(WAIT_TIME)

        # テキスト入力
        text = dm_setting["メッセージテンプレート"].format(name=dm_setting[HEADER_NAME])
        text_list = text.split('\n')
        input_ele = driver.find_element_by_xpath(
            "/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea")
        for t in text_list:
            driver.execute_script(f'var elm=arguments[0];elm.value += "{t}";elm.dispatchEvent(new Event("change"));',
                                  input_ele)
            input_ele.send_keys(Keys.SHIFT, Keys.ENTER)

        time.sleep(WAIT_TIME)

        # 送信
        driver.find_element_by_xpath(
            "/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[3]/button").click()

        # スクリーンショット
        now = datetime.date.today()
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
        driver.save_screenshot(filename=filename)
    except Exception as e:
        print(f'Exception={e}')
        result_list.append(dm_setting)
        continue

    dm_setting.update({HEADER_SEND_RESULT: "済"})
    result_list.append(dm_setting)

result_csv_writer.writeheader()
result_csv_writer.writerows(result_list)
