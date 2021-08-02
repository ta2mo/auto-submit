import datetime

from selenium.common.exceptions import NoSuchElementException

import csv
import os
import logging
import platform
import sys

import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# -------------------------------------------------------------------------------------------------
# variables
# -------------------------------------------------------------------------------------------------
WAIT_TIME = 3

ACCOUNT_TYPE_HEADER = '競合 or リポスト元'
ACCOUNT_USERID_HEADER = '競合アカウントのuserID'

logging.basicConfig(filename='./debug.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

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
# functions
# -------------------------------------------------------------------------------------------------

def connect_gspread(jsonf, key):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonf, scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_KEY = key
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    follow_target_worksheet = workbook.worksheet('自動フォロー_自動化用')
    follow_calendar_worksheet = workbook.worksheet('自動フォローカレンダー')
    conflict_account_worksheet = workbook.worksheet('競合アカウント一覧')
    return follow_target_worksheet, follow_calendar_worksheet, conflict_account_worksheet


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
        # options.add_argument(user_data_dir)
        options.add_argument(profile_directory)
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

# spreadsheet
json_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret', 'diet-project.json')
spread_sheet_key = "1XRdnOIn31ZXNfeMe6mDskgGKCXbi7Nmj_bqiX5q-yM4"

follow_target_worksheet, follow_calendar_worksheet, conflict_account_worksheet = connect_gspread(json_file_name, spread_sheet_key)

today = datetime.datetime.today().strftime('%Y/%m/%d')
today_cell = follow_calendar_worksheet.find(today)
try:
    c = follow_calendar_worksheet.cell(today_cell.row, today_cell.col + 2).value
    today_count = int(c)
except ValueError as e:
    logging.debug(f'invalid value error. e={e}')
    today_count = 0


if today_count == 0:
    logging.debug('follow count=0.')
    driver.quit()
    exit(0)

account = follow_calendar_worksheet.row_values(today_cell.row)

user_name = account[1]
driver.get(f'https://www.instagram.com/{user_name}/')
wait()

# ページ削除の場合
try:
    not_found_message = driver.find_element(By.XPATH, '/html/body/div[1]/section/main/div/div/h2').text
    if not_found_message == 'このページはご利用いただけません。':
        logging.debug(f'page not found. userID={user_name}')
        # TODO: ユーザーが存在しなかった場合にスプレッドシートに書く
        exit(1)
except NoSuchElementException as e:
    logging.debug('exist account.')



MAX_FOLLOW_COUNT = 150
MAX_FOLLOW_COUNT = int(account[2])
post_dig_count = 0
col_count = 1
MAX_DIG_COUNT = 100

while post_dig_count < MAX_DIG_COUNT:
    # 投稿をクリック
    latest_post_xpath = f'//*[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[{int(post_dig_count / 3) +1}]/div[{(post_dig_count % 3) + 1}]/a/div[1]/div[2]'
    driver.find_element(By.XPATH, latest_post_xpath).click()
    wait()

    # いいね数をクリック
    try:
        like_count_xpath = '/html/body/div[4]/div[2]/div/article/div[3]/section[2]/div/div[2]/a/span'
        like_count = int(driver.find_element(By.XPATH, like_count_xpath).text)
    except:
        logging.debug(f'no such like count element. xpath={like_count_xpath}')

    try:
        like_count_xpath = '/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div[2]/a/span'
        like_count = int(driver.find_element(By.XPATH, like_count_xpath).text)
    except:
        logging.debug(f'no such like count element. xpath={like_count_xpath}')

    wait()
    if like_count < MAX_FOLLOW_COUNT:
        logging.debug(f'like account = {like_count}.')

        print('>')
        filter_xpath = '/html/body/div[5]/div[3]/button'
        target_element = driver.find_element(By.XPATH, filter_xpath)

        driver.execute_script(f'var elm=arguments[0];elm.click();', target_element)
        post_dig_count += 1
        continue

    break

post_url = driver.current_url

# いいね数をクリック
like_account_xpath = '/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div[2]/a'
driver.find_element(By.XPATH, like_account_xpath).click()
wait()

get_account_count = 0
account_name_list = []

excluce_username_list = conflict_account_worksheet.col_values(4)
while True:
    account_name_xpath = f'/html/body/div[6]/div/div/div[2]/div/div/div[{get_account_count + 1}]/div[2]/div[1]/div/span/a'
    account_name = driver.find_element(By.XPATH, account_name_xpath).text

    account_follow_button = f'/html/body/div[6]/div/div/div[2]/div/div/div[{get_account_count + 1}]/div[3]/button'

    follow_button = driver.find_element(By.XPATH, account_follow_button)
    wait()

    if follow_button.text == 'フォロー中' or user_name in excluce_username_list:
        logging.debug(f'followed account. account_name={account_name}')
        continue

    # フォローボタンまでスクロール
    actions = ActionChains(driver)
    actions.move_to_element(follow_button).perform()

    # フォローボタンをクリック
    follow_button.click()

    account_name_list.append(account_name)
    get_account_count += 1

    if get_account_count > MAX_FOLLOW_COUNT:
        logging.debug('follow complete')
        break

# スプレッドシートに書き込む
for target in account_name_list:
    follow_target_worksheet.append_row([today, target, user_name, post_url])

driver.quit()
