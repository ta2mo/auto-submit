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

# if 'log_level' in config:
#     LOG_LEVEL = config['log_level']
# else:
#     LOG_LEVEL = logging.DEBUG

logging.basicConfig(filename='./debug.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logging.debug('start')
logging.debug(f'WAIT_TIME={WAIT_TIME}')


# logging.debug(f'LOG_LEVEL={LOG_LEVEL}')


# -------------------------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------------------------
def take_display_screenshot(driver):
    now = datetime.date.today()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    driver.save_screenshot(filename=filename)


def take_element_screenshot(element):
    now = datetime.date.today()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    png = element.screenshot_as_png
    with open(filename, 'wb') as f:
        f.write(png)


def click_element_by_id(driver, id):
    try:
        driver.find_element_by_id(id).click()
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found id={id}')
        take_display_screenshot(driver)


def click_div_by_class_name(driver, class_name):
    try:
        driver.find_element_by_xpath(f'//div[@class="{class_name}"]').click()
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found class_name={class_name}')
        take_display_screenshot(driver)


def click_button_by_class_name(driver, class_name):
    try:
        driver.find_element_by_xpath(f'//button[@class="{class_name}"]').click()
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found class_name={class_name}')
        take_display_screenshot(driver)


def input_element_by_class_name(driver, class_name, value):
    try:
        driver.find_element_by_xpath(f'//input[@class="{class_name}"]').send_keys(value)
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found class_name={class_name}')
        take_display_screenshot(driver)


def input_element_by_id(driver, id, value):
    try:
        driver.find_element_by_xpath(f'//input[@id="{id}"]').send_keys(value)
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found class_name={id}')
        take_display_screenshot(driver)


def input_element_by_xpath(driver, xpath, value):
    try:
        driver.find_element_by_xpath(xpath).send_keys(value)
        time.sleep(WAIT_TIME)
    except NoSuchElementException:
        logging.error(f'not found xpath={xpath}')
        take_display_screenshot(driver)


def clear_input(driver, class_name):
    try:
        while True:
            driver.find_element_by_xpath(f'//input[@class="{class_name}"]').send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(f'//input[@class="{class_name}"]').get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        logging.error(f'not found class_name={class_name}')
        take_display_screenshot(driver)


def clear_input_by_id(driver, id):
    try:
        while True:
            driver.find_element_by_xpath(f'//input[@id="{id}"]').send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(f'//input[@id="{id}"]').get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        logging.error(f'not found class_name={id}')
        take_display_screenshot(driver)


def clear_input_by_xpath(driver, xpath):
    try:
        while True:
            driver.find_element_by_xpath(xpath).send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(xpath).get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        logging.error(f'not found xpath={xpath}')
        take_display_screenshot(driver)


# -------------------------------------------------------------------------------------------------
# temp dir check
# -------------------------------------------------------------------------------------------------
logging.debug('temp dir check')
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
    os.environ['TEMP'] = temp_dir
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
    os.environ['TMP'] = tmp_dir
    os.makedirs(tmp_dir, exist_ok=True)

logging.debug('driver settings')
options = webdriver.ChromeOptions()

user_data_dir = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/'
profile_directory = '--profile-directory="Profile 1'
if platform.system() == 'Windows':
    logging.info('exec on windows')
    user_data_dir = f'--user-data-dir={config["DEFAULT"]["windows_profile_dir"]}'
    profile_directory = f'--profile-directory={config["DEFAULT"]["profile_directory"]}'
    options.add_argument(user_data_dir)
    options.add_argument(profile_directory)
    try:
        driver = webdriver.Chrome(options=options, executable_path='.\\driver\\chromedriver-89.exe')
    except Exception as e:
        logging.error(f'get driver failed. {e}')
else:
    logging.info('exec on other os')
    options.add_argument(user_data_dir)
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logging.error(f'get driver failed. {e}')

# -------------------------------------------------------------------------------------------------
# csv check
# -------------------------------------------------------------------------------------------------
logging.info('check csv files')
csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'csv')
if not os.path.exists(csv_dir):
    logging.error('指定のディレクトリが存在しません')
    driver.quit()
    sys.exit(1)

campaign_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/campaign.csv')
if not os.path.exists(campaign_csv_path):
    logging.error('キャンペーン設定のCSVファイルが存在しません')
    driver.quit()
    sys.exit(1)

creative_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/creative.csv')
if not os.path.exists(creative_csv_path):
    logging.error('クリエイティブ設定のCSVファイルが存在しません')
    driver.quit()
    sys.exit(1)

campaign_csv_file = open(campaign_csv_path, 'r', encoding='utf_8')
campaign_csv_reader = csv.DictReader(campaign_csv_file)

creative_csv_file = open(creative_csv_path, 'r', encoding='utf_8')
creative_csv_reader = csv.DictReader(creative_csv_file)

for row in campaign_csv_reader:
    campaign_settings = row
    break

# -------------------------------------------------------------------------------------------------
# 広告マネージャーを開く
# -------------------------------------------------------------------------------------------------
original_window = driver.current_window_handle
driver.execute_script("window.open()")  # make new tab
for i, window_handle in enumerate(driver.window_handles):
    if window_handle == original_window:
        logging.debug(f'switch new tab. original_window driver.title={driver.title}')
        new_window = driver.window_handles[i + 1]  # 隣で新規タブが開かれる想定
        driver.switch_to.window(new_window)
        break

if 'act' in campaign_settings:
    act = campaign_settings['act']
    query_string = f'act={act}'

driver.get(f'https://business.facebook.com/adsmanager/manage/campaigns?{query_string}')
time.sleep(5)

# -------------------------------------------------------------------------------------------------
# キャンペーン
# -------------------------------------------------------------------------------------------------
# 作成ボタン
# click_div_by_class_name(driver, 'g1fckbup dfy4e4am h3y5hp2p sdgvddc7 b8b10xji okyvhjd0 rpcniqb6 jytk9n0j ojz0a1ch '
#                                 'avm085bc mtc4pi7f jza0iyw7 njc9t6cs qhe9tvzt spzutpn9 puibpoiz svsqgeze if5qj5rh '
#                                 'har4n1i8 diwav8v6 nlmdo9b9 h706y6tg qbdq5e12 j90q0chr rbzcxh88 h8e39ki1 rgsc13q7 '
#                                 'a53abz89 llt6l64p pt6x234n bmtosu2b ndrgvajj s7wjoji2 jztyeye0 d5rc5kzv jdcxz0ji '
#                                 'frrweqq6 qnavoh4n b1hd98k5 c332bl9r f1dwqt7s rqkdmjxc tb4cuiq2 nmystfjm kojzg8i3 '
#                                 'm33fj6rl wy1fu5n8 chuaj5k6 hkz453cq dkjikr3h ay1kswi3 lcvupfea jq4kb4ie ft7osd3y')
create_button_xpath = '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/div[3]/div[4]/div/div[3]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div'
driver.find_element_by_xpath(create_button_xpath).click()
time.sleep(WAIT_TIME)

# 認知アップ選択
click_element_by_id(driver, 'CONVERSIONS')
time.sleep(WAIT_TIME)

# 次へ選択
click_button_by_class_name(driver, '_271k _271m _1qjd layerConfirm _7tvm _7tv3 _7tv4')
click_button_by_class_name(driver, '_271k _271m _1qjd _7tvm _7tv3 _7tv4')

time.sleep(WAIT_TIME)

# キャンペーン名入力
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['キャンペーン名'])

while True:
    try:
        msg = driver.find_element_by_xpath(f'//div[@class="_3b62"]/span').text
    except:
        time.sleep(3)
        continue

    if msg == 'すべての変更が保存されました':
        break

    time.sleep(3)

driver.find_element_by_xpath(
    '//div[@style="display: inline-block;"]/div[@style="display: inline-block;"]/button[@class="_271k _271m _1qjd _7tvm _7tv3 _7tv4"]').click()

time.sleep(WAIT_TIME)

# -------------------------------------------------------------------------------------------------
# 広告セット
# -------------------------------------------------------------------------------------------------
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['広告セット名'])

if '予算' in campaign_settings:
    budget_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[' \
                   '2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[5]/div/div/div/div[' \
                   '2]/div/div/div/div[1]/div/div[2]/div/div[1]/div[3]/div/span/input '
    driver.find_element_by_xpath(budget_xpath).click()
    clear_input_by_xpath(driver, budget_xpath)
    input_element_by_xpath(driver, budget_xpath, value=campaign_settings['予算'])

if '開始日時' in campaign_settings:
    logging.info('開始日時')
    clear_input_by_id(driver, 'js_12i')
    input_element_by_id(driver, 'js_12i', value=campaign_settings['開始日時'])

if '年齢下限' in campaign_settings and '年齢上限' in campaign_settings:
    logging.info('年齢入力')
    try:
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div[2]/div/div/span').click()
    except:
        logging.info("年齢選択テキストがありませんでした")
        take_display_screenshot(driver)

    # 年齢下限
    if '年齢下限' in campaign_settings:
        min_age_target_li = int(campaign_settings['年齢下限']) - 12
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div').click()
        driver.find_element_by_xpath(
            f'/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[{min_age_target_li}]/div/div[1]').click()

    # 年齢上限
    if '年齢上限' in campaign_settings:
        min_age_target_li = int(campaign_settings['年齢上限']) - 12
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div[4]').click()
        driver.find_element_by_xpath(
            f'/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[{min_age_target_li}]/div/div[1]').click()

if '性別' in campaign_settings:
    logging.info('性別')
    try:
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div[1]/div[17]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div[2]/div/div/span').click()
    except:
        logging.info("性別選択テキストがありませんでした")
        take_display_screenshot(driver)

    gender = campaign_settings['性別']
    if gender == '男性':
        checkbox = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div/div[3]/div[1]/div/input').click()
    elif gender == '女性':
        checkbox = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div/div[3]/div[1]/div/input').click()
    else:  # すべて
        checkbox = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div[1]/div[17]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div/div[1]/div[1]/div/input').click()

    expected_conditions.element_selection_state_to_be(checkbox, True)

# 配置
placement_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[1]/div/div/div[2]'
driver.find_element_by_xpath(placement_xpath).click()

# デバイス
device_select_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div/div/span'
try:
    driver.find_element_by_xpath(device_select_xpath).click()
except:
    logging.info('デバイス選択テキストがありませんでした')

device_selectbox_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div'
driver.find_element_by_xpath(device_selectbox_xpath).click()

desktop_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[2]/div/div[1]/div/input'
driver.find_element_by_xpath(desktop_input_xpath).click()

placement_title_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[1]/div/div/div[1]/div'
driver.find_element_by_xpath(placement_title_xpath).click()

# プラットフォーム
fb_input_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[3]/div/div/div[2]/ul/table[1]/tbody/tr/td[1]/li/div/div/div/input'
ig_input_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[3]/div/div/div[2]/ul/table[1]/tbody/tr/td[2]/li/div/div/div/input'
an_input_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[3]/div/div/div[2]/ul/table[2]/tbody/tr/td[1]/li/div/div/div/input'
ms_input_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[3]/div/div/div[2]/ul/table[2]/tbody/tr/td[2]/li/div/div/div/input'

stories_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[2]/ul/li/div[1]/div[3]/div/div/div/input'
instream_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[3]/ul/li/div[1]/div[3]/div/div/div/input'
search_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[4]/ul/li/div[1]/div[3]/div/div/div/input'
inpost_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[6]/ul/li/div[1]/div[3]/div/div/div/input'

ig_st_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[2]/ul/div[2]/li/div/div[3]/div/div/div/input'
ig_feed_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[1]/ul/div[2]/li/div/div[3]/div/div/div/input'
ig_find_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[1]/ul/div[6]/li/div/div[3]/div/div/div/input'

fb_st_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[2]/ul/div[1]/li/div/div[3]/div/div/div/input'
ms_st_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[2]/ul/div[3]/li/div/div[3]/div/div/div/input'

if 'FBFD' in campaign_settings and campaign_settings['FBFD']:
    logging.info('FBFD')
    driver.find_element_by_xpath(ig_input_xpath).click()
    time.sleep(WAIT_TIME)
    driver.find_element_by_xpath(an_input_xpath).click()
    time.sleep(WAIT_TIME)
    driver.find_element_by_xpath(ms_input_xpath).click()
    time.sleep(WAIT_TIME)

    marketplace_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[1]/ul/div[3]/li/div/div[3]/div/div/div/input'
    driver.find_element_by_xpath(marketplace_check_xpath).click()

    movie_feed_check_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[7]/div/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div[6]/div/div[1]/ul/div/li[1]/ul/div[4]/li/div/div[3]/div/div/div/input'
    driver.find_element_by_xpath(movie_feed_check_xpath).click()
    time.sleep(WAIT_TIME)

    driver.find_element_by_xpath(stories_check_xpath).click()
    driver.find_element_by_xpath(stories_check_xpath).click()
    driver.find_element_by_xpath(instream_check_xpath).click()
    driver.find_element_by_xpath(search_check_xpath).click()
    driver.find_element_by_xpath(inpost_check_xpath).click()
    time.sleep(WAIT_TIME)

if 'IGFD' in campaign_settings and campaign_settings['IGFD']:
    logging.info('IGFD')
    driver.find_element_by_xpath(placement_xpath).click(fb_input_xpath)
    time.sleep(WAIT_TIME)
    driver.find_element_by_xpath(ig_input_xpath).click(an_input_xpath)
    driver.find_element_by_xpath(an_input_xpath).click(ms_input_xpath)
    time.sleep(WAIT_TIME)

    driver.find_element_by_xpath(ig_st_xpath).click()

if 'ST' in campaign_settings and campaign_settings['ST']:
    logging.info('ST')
    driver.find_element_by_xpath(placement_xpath).click(fb_input_xpath)
    time.sleep(WAIT_TIME)
    driver.find_element_by_xpath(ig_input_xpath).click(an_input_xpath)
    driver.find_element_by_xpath(an_input_xpath).click(ms_input_xpath)
    time.sleep(WAIT_TIME)

    driver.find_element_by_xpath(ig_feed_xpath).click()
    driver.find_element_by_xpath(ig_find_xpath).click()
    time.sleep(WAIT_TIME)

    driver.find_element_by_xpath(fb_st_xpath).click()
    time.sleep(WAIT_TIME)
    driver.find_element_by_xpath(ms_st_xpath).click()
    time.sleep(WAIT_TIME)

# 最適化と配信
if 'Attribution Setting' in row:
    other_option_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[8]/div/div/div/div/div/div[2]/div/div/div/div[3]/span'
    try:
        driver.find_element_by_xpath(other_option_xpath).click()
    except:
        logging.info('その他のオプションがありませんでした')

    select_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[8]/div/div/div/div/div/div[2]/div/div/div/div[4]/div[2]/div/div[2]/div/div/div[2]/div/div/span'
    try:
        driver.find_element_by_xpath(select_xpath).click()
    except:
        logging.info('Attribution Settingの選択がありませんでした')

    selectbox_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[8]/div/div/div/div/div/div[2]/div/div/div/div[4]/div[2]/div[1]/div[1]/div[2]/div/div[2]'
    driver.find_element_by_xpath(selectbox_xpath).click()

    select_value = row['Attribution Setting']
    if select_value == 'クリックから1日間':
        target_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[1]/div/div[1]/div/input'
    elif select_value == 'クリックから7日間':
        target_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[2]/div/div[1]/div/input'
    elif select_value == 'クリックまたは表示から1日間':
        target_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[3]/div/div[1]/div/input'
    elif select_value == 'クリックから7日間または表示から1日間':
        target_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[4]/div/div[1]/div/input'

    driver.find_element_by_xpath(target_input_xpath).click()
    time.sleep(WAIT_TIME)

while True:
    try:
        msg = driver.find_element_by_xpath(f'//div[@class="_3b62"]/span').text
    except:
        time.sleep(3)
        continue

    if msg == 'すべての変更が保存されました':
        break

    time.sleep(3)

save_button_xpath = '//div[@style="display: inline-block;"]/div[@style="display: inline-block;"]/button[@class="_271k _271m _1qjd _7tvm _7tv3 _7tv4"]'
driver.find_element_by_xpath(save_button_xpath).click()
time.sleep(WAIT_TIME)

# 広告名
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['広告名'])

time.sleep(WAIT_TIME)

# -------------------------------------------------------------------------------------------------
# クリエイティブ
# -------------------------------------------------------------------------------------------------
driver.find_element_by_xpath(
    '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[3]/div/span[1]/div/button/div/div').click()
time.sleep(WAIT_TIME)

for i, row in enumerate(creative_csv_reader):
    if i != 0:
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div[2]/div[2]').click()
        time.sleep(10)
        quick_copy_xpath = '/html/body/div[1]/div/div/div/div[2]/div/div/div/div/ul/li[2]/div/div'
        driver.find_element_by_xpath(quick_copy_xpath).click()
        time.sleep(WAIT_TIME)

    file_name = row['ファイル名']
    main_text = row['メインテキスト']

    if i == 0:
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div/div[3]/div/div/div/div/div/div[1]/div/div/ul/li[1]/div/div/div[2]'
        ).click()
        time.sleep(WAIT_TIME)

        image_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'image/{file_name}')
        driver.find_element_by_xpath(
            '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/input'
        ).send_keys(image_file)

        time.sleep(10)
    else:
        media_button_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/ul/div/div/div'
        driver.find_element_by_xpath(media_button_xpath).click()
        time.sleep(WAIT_TIME)

        media_edit_button_xpath = '/html/body/div[6]/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/div/div/div/div/div/div'
        driver.find_element_by_xpath(media_edit_button_xpath).click()
        time.sleep(10)

    logging.info(f'upload complete {file_name}')

    driver \
        .find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[4]/div[1]/div/div/div[1]/div/div/div[1]').click()

    logging.info('click image')
    time.sleep(WAIT_TIME)

    # 次へ
    driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div').click()

    time.sleep(WAIT_TIME)

    # 完了
    driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div').click()

    time.sleep(WAIT_TIME)

    # メインテキスト
    if i != 0:
        main_text_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/span/span'
        while True:
            driver.find_element_by_xpath(main_text_xpath).send_keys(Keys.DELETE)
            try:
                input_text = driver.find_element_by_xpath(main_text_xpath).text
            except:
                break

            if input_text == '':
                break

    main_text_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/span/br'
    main_text_element = driver.find_element_by_xpath(main_text_xpath)
    main_text_value = row['メインテキスト']
    main_text_element.send_keys(main_text_value)

    # 最終手段
    # driver.execute_script(f'var ele=arguments[0];ele.innerHTML = "{main_text_value}";', main_text_element)
    logging.info('テキスト入力完了')

    # 見出し
    if '見出し' in row:
        title_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/textarea'
        title_value = row['見出し']
        title_element = driver.find_element_by_xpath(title_xpath).send_keys(title_value)

    # 説明
    if '説明' in row:
        description_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[1]/textarea'
        description_value = row['説明']
        description_element = driver.find_element_by_xpath(description_xpath).send_keys(description_value)

    # ウェブサイトのURL
    if 'ウェブサイトのURL' in row:
        url_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[5]/div/div/div[1]/div[2]/div/div/div/div[2]/div/div/div/div[1]/textarea'
        url_value = row['ウェブサイトのURL']
        url_element = driver.find_element_by_xpath(url_xpath).send_keys(url_value)

    while True:
        try:
            msg = driver.find_element_by_xpath(f'//div[@class="_3b62"]/span').text
        except:
            time.sleep(3)
            continue

        if msg == 'すべての変更が保存されました':
            break

        time.sleep(3)

    logging.info('保存完了')

time.sleep(WAIT_TIME)

logging.debug('end')

# 終了
# driver.quit()
