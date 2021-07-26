import datetime
import logging
import os
import platform

import gspread
import sys
import time

from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver import Keys

import csv

from selenium import webdriver

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

login_csv_file = open(login_csv_path, 'r', encoding='utf-8-sig') # BOM付きファイル対応
login_csv_reader = csv.DictReader(login_csv_file)

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


def connect_gspread(jsonf, key):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonf, scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_KEY = key
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    dm_setting_worksheet = workbook.worksheet('許可DM_自動化用')
    account_list_worksheet = workbook.worksheet('アカウント一覧')
    return dm_setting_worksheet, account_list_worksheet

def wait():
    time.sleep(WAIT_TIME)

# -------------------------------------------------------------------------------------------------
# execute
# -------------------------------------------------------------------------------------------------
options = webdriver.ChromeOptions()

user_data_dir = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/'
profile_directory = '--profile-directory="Profile 1'
if platform.system() == 'Windows':
    logging.info('exec on windows')
    try:
        driver = webdriver.Chrome(options=options, executable_path='.\\driver\\chromedriver.exe')
    except Exception as e:
        logging.error(f'get driver failed. {e}')
else:
    logging.info('exec on other os')
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logging.error(f'get driver failed. {e}')

driver.get("https://www.instagram.com/accounts/login/")

wait()

driver.find_element_by_name("username").send_keys(login_setting["mailaddress"])
driver.find_element_by_name("password").send_keys(login_setting["password"])
time.sleep(WAIT_TIME)

driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click()
wait()

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


# spreadsheet
json_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret', 'diet-project.json')
spread_sheet_key = "1XRdnOIn31ZXNfeMe6mDskgGKCXbi7Nmj_bqiX5q-yM4"

dm_setting_worksheet, account_list_worksheet = connect_gspread(json_file_name, spread_sheet_key)
rows = dm_setting_worksheet.get_all_records(empty2zero=False, head=1, default_blank='')

for dm_setting in rows:
    if not dm_setting[HEADER_USERNAME]:
        break

    if dm_setting[HEADER_SEND_RESULT] or not dm_setting[HEADER_MESSAGE]:
        continue

    driver.get("https://www.instagram.com/direct/inbox/")
    wait()

    # 通知ONポップアップを後で
    try:
        notify_element = driver.find_element_by_xpath("/html/body/div[3]/div/div/div/div[3]/button[2]")
        notify_text = notify_element.text
        if notify_text == '後で':
            notify_element.click()
            wait()
    except:
        logging.debug("notify popup not found.")
        # wait()

    try:
        driver.find_element_by_xpath(
            "/html/body/div[1]/section/div/div[2]/div/div/div[1]/div[1]/div/div[3]/button").click()
        driver.find_element_by_name("queryBox").send_keys(dm_setting[HEADER_USERNAME])

        wait()

        # 先頭のユーザーをクリック
        driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[2]/div[1]/div").click()

        # 次へをクリック
        driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]/div/button").click()
        wait()

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

        # テスト用モードは送信と送信済みの記載をしない
        if login_setting["test_mode"] == "ON":
            logging.debug("test mode. not send.")
            continue

        # 送信
        send_button_xpath = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[3]/button'
        driver.find_element_by_xpath(send_button_xpath).click()

        cell = dm_setting_worksheet.find(str(dm_setting[HEADER_NO]))
        account_list_worksheet.update_cell(cell.row, 6, '自動送信')
    except Exception as e:
        print(f'Exception={e}')
        continue

    dm_setting.update({HEADER_SEND_RESULT: "済"})
