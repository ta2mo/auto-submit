import datetime
import logging
import os
import platform
import sys
import time
import csv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

# transition wait
WAIT_TIME = 2


def take_display_screenshot(driver):
    now = datetime.date.today()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    driver.save_screenshot(filename=filename)


def take_element_screenshot():
    now = datetime.date.today()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    driver.save_screenshot(filename=filename)


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

logging.basicConfig(filename='./debug.log', level=logging.DEBUG)

options = webdriver.ChromeOptions()

user_data_path = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/Profile 1/'
if platform.system() == 'Windows':
    logging.debug('exec on windows')
    user_data_path = 'C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\Default'
    options.add_argument(user_data_path)
    try:
        driver = webdriver.Chrome(options=options, executable_path='.\\driver\\chromedriver-85.exe')
    except Exception as e:
        logging.debug(f'get driver failed. {e}')
else:
    logging.debug('exec on other os')
    options.add_argument(user_data_path)
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logging.debug(f'get driver failed. {e}')

# 引数
logging.debug('check csv files')
csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'csv/{sys.argv[1]}')
if not os.path.exists(csv_dir):
    print('指定のディレクトリが存在しません')
    driver.quit()
    sys.exit(1)

creative_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/creative.csv')
if not os.path.exists(creative_csv_path):
    print('クリエイティブ設定のCSVファイルが存在しません')
    driver.quit()
    sys.exit(1)

campaign_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/campaign.csv')
if not os.path.exists(campaign_csv_path):
    print('キャンペーン設定のCSVファイルが存在しません')
    driver.quit()
    sys.exit(1)

creative_csv_file = open(creative_csv_path, 'r')
creative_csv_reader = csv.DictReader(creative_csv_file)

campaign_csv_file = open(campaign_csv_path, 'r')
campaign_csv_reader = csv.DictReader(campaign_csv_file)
for row in campaign_csv_reader:
    campaign_settings = row
    break

# 広告マネージャーを開く
logging.debug('open chrome')
driver.get('https://business.facebook.com/adsmanager/manage/')
time.sleep(5)

# 作成ボタン
# driver.find_element_by_link_text('作成').click()
click_div_by_class_name(driver, 'g1fckbup dfy4e4am h3y5hp2p sdgvddc7 b8b10xji okyvhjd0 rpcniqb6 jytk9n0j ojz0a1ch '
                                'avm085bc mtc4pi7f jza0iyw7 njc9t6cs qhe9tvzt spzutpn9 puibpoiz svsqgeze if5qj5rh '
                                'har4n1i8 diwav8v6 nlmdo9b9 h706y6tg qbdq5e12 j90q0chr rbzcxh88 h8e39ki1 rgsc13q7 '
                                'a53abz89 llt6l64p pt6x234n bmtosu2b ndrgvajj s7wjoji2 jztyeye0 d5rc5kzv jdcxz0ji '
                                'frrweqq6 qnavoh4n b1hd98k5 c332bl9r f1dwqt7s rqkdmjxc tb4cuiq2 nmystfjm kojzg8i3 '
                                'm33fj6rl wy1fu5n8 chuaj5k6 hkz453cq dkjikr3h ay1kswi3 lcvupfea jq4kb4ie ft7osd3y')

# 認知アップ選択
click_element_by_id(driver, 'BRAND_AWARENESS')

# 次へ選択
click_button_by_class_name(driver, '_271k _271m _1qjd layerConfirm _7tvm _7tv3 _7tv4')
click_button_by_class_name(driver, '_271k _271m _1qjd _7tvm _7tv3 _7tv4')

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

# 広告セット
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['広告セット名'])

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

# 広告名
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['広告名'])

time.sleep(WAIT_TIME)

# クリエイティブ
driver.find_element_by_xpath(
    '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[3]/div/span[1]/div/button/div/div').click()
time.sleep(WAIT_TIME)

for row in creative_csv_reader:
    file_name = row['ファイル名']
    main_text = row['メインテキスト']

    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div/div[3]/div/div/div/div/div/div[1]/div/div/ul/li[1]/div/div/div[2]'
    ).click()
    time.sleep(WAIT_TIME)

    image_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{csv_dir}/image/{file_name}')
    print(image_file)
    driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/input'
    ).send_keys(image_file)

    time.sleep(10)

    print('upload complete')

    driver \
        .find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[4]/div[1]/div/div/div[1]/div/div/div[1]').click()  # .find_element_by_partial_link_text(

    print('click image')
    time.sleep(WAIT_TIME)

    # 次へ
    driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div').click()

    time.sleep(WAIT_TIME)

    # 完了
    driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div').click()

    # メインテキスト
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[4]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/span').send_keys(
        'メインテキスト')
    print('テキスト入力完了')

    while True:
        try:
            msg = driver.find_element_by_xpath(f'//div[@class="_3b62"]/span').text
        except:
            time.sleep(3)
            continue

        if msg == 'すべての変更が保存されました':
            break

        time.sleep(3)

    print('保存完了')

# --- ---

time.sleep(WAIT_TIME)
time.sleep(500)

# 終了
driver.quit()
