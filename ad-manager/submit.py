import configparser
import datetime
import logging
import os
import platform
import re
import sys
import time

from selenium.webdriver import ActionChains
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
logging.debug('開始')
# -------------------------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------------------------


def take_display_screenshot(driver):
    now = datetime.date.today()
    ss_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ss')
    if not os.path.exists(ss_dir):
        os.mkdir(ss_dir)
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    driver.save_screenshot(filename=filename)


def take_element_screenshot(element):
    now = datetime.date.today()
    ss_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ss')
    if not os.path.exists(ss_dir):
        os.mkdir(ss_dir)
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'ss/{now:%y%m%d-%h:%m:%ss}.png')
    png = element.screenshot_as_png
    with open(filename, 'wb') as f:
        f.write(png)


def save_error_html(driver):
    now = datetime.date.today()
    with open(f'debug_{now:%y%m%d-%h:%m:%ss}.html', mode="w") as f:
        f.write(driver.page_source)


def click_element_by_id(driver, id):
    retry_count = 0
    max_retry_count = 100
    while retry_count < max_retry_count:
        try:
            driver.find_element_by_id(id).click()
            wait()
            break
        except NoSuchElementException:
            logging.debug(f'not found id={id}. retry_count={retry_count}')
        wait()
        retry_count += 1

    if retry_count >= max_retry_count:
        logging.error(f'retry {retry_count} times. cannot click element. id={id}.')
        take_display_screenshot(driver)
        save_error_html(driver)

def click_div_by_class_name(driver, class_name):
    try:
        driver.find_element_by_xpath(f'//div[@class="{class_name}"]').click()
        wait()
    except NoSuchElementException:
        logging.error(f'not found class_name={class_name}')
        take_display_screenshot(driver)


def click_button_by_class_name(driver, class_name):
    try:
        driver.find_element_by_xpath(f'//button[@class="{class_name}"]').click()
        wait()
    except NoSuchElementException:
        take_display_screenshot(driver)
        save_error_html(driver)
        logging.error(f'not found class_name={class_name}')


def click_by_xpath(driver, xpath):
    retry_count = 0
    max_retry_count = 100
    while retry_count < max_retry_count:
        try:
            driver.find_element_by_xpath(xpath).click()
            wait()
            break
        except NoSuchElementException as e:
            logging.debug(f'Not found xpath={xpath}. retry_count={retry_count}')
        wait()
        retry_count += 1

    if retry_count >= max_retry_count:
        logging.error(f'Retry {retry_count} times. cannot click element. xpath={xpath}.')
        take_display_screenshot(driver)
        save_error_html(driver)


def input_element_by_class_name(driver, class_name, value):
    try:
        driver.find_element_by_xpath(f'//input[@class="{class_name}"]').send_keys(value)
        wait()
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found class_name={class_name}')


def input_element_by_id(driver, id, value):
    try:
        driver.find_element_by_xpath(f'//input[@id="{id}"]').send_keys(value)
        wait()
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found class_name={id}')


def input_element_by_xpath(driver, xpath, value):
    try:
        driver.find_element_by_xpath(xpath).send_keys(value)
        wait()
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found xpath={xpath}')


def clear_input(driver, class_name):
    try:
        while True:
            driver.find_element_by_xpath(f'//input[@class="{class_name}"]').send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(f'//input[@class="{class_name}"]').get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found class_name={class_name}')


def clear_input_by_id(driver, id):
    try:
        while True:
            driver.find_element_by_xpath(f'//input[@id="{id}"]').send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(f'//input[@id="{id}"]').get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found class_name={id}')


def clear_input_by_xpath(driver, xpath):
    try:
        while True:
            driver.find_element_by_xpath(xpath).send_keys(Keys.BACK_SPACE)
            input_text = driver.find_element_by_xpath(xpath).get_attribute('value')
            if input_text == '':
                break
    except NoSuchElementException:
        take_display_screenshot(driver)
        logging.error(f'not found xpath={xpath}')


def set_adset(driver, campaign_settings):
    clear_input(driver, '_58al')
    input_element_by_class_name(driver, '_58al', value=campaign_settings['広告セット名'])

    if '予算' in campaign_settings:
        budget_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div[2]/div[2]/div[' \
                       '3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[5]/div/div/div/div/div[' \
                       '2]/div/div/div/div[1]/div/div/div[2]/div/div/div/div[1]/div[3]/div/span/input '
        click_by_xpath(driver, budget_xpath)
        clear_input_by_xpath(driver, budget_xpath)
        input_element_by_xpath(driver, budget_xpath, value=campaign_settings['予算'])

    if '開始日時' in campaign_settings:
        logging.info('開始日時')
        clear_input_by_id(driver, 'js_12i')
        input_element_by_id(driver, 'js_12i', value=campaign_settings['開始日時'])

    if '年齢下限' in campaign_settings and '年齢上限' in campaign_settings:
        logging.info('年齢入力')
        try:
            age_select_xpath = '//*[@id="campaignTargetingSection"]/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div[2]'
            click_by_xpath(driver, age_select_xpath)
        except:
            logging.info("年齢選択テキストがありませんでした")
            take_display_screenshot(driver)

        # 年齢下限
        if '年齢下限' in campaign_settings:
            min_age_target_li = int(campaign_settings['年齢下限']) - 12
            min_age_target_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div'
            click_by_xpath(driver, min_age_target_xpath)
            min_age_li_xpath = f'/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[{min_age_target_li}]/div/div[1]'
            click_by_xpath(driver, min_age_li_xpath)

        # 年齢上限
        if '年齢上限' in campaign_settings:
            max_age_target_li = int(campaign_settings['年齢上限']) - 12
            max_age_target_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div[4]/div'
            click_by_xpath(driver, max_age_target_xpath)
            max_age_li_xpath = f'/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[{max_age_target_li}]/div/div[1]'
            click_by_xpath(driver, max_age_li_xpath)

    if '性別' in campaign_settings:
        logging.info('性別')
        try:
            driver.find_element_by_xpath(
                '//*[@id="campaignTargetingSection"]/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div[2]/div/div').click()
        except:
            logging.info("性別選択テキストがありませんでした")
            take_display_screenshot(driver)

        gender = campaign_settings['性別']
        if gender == '男性':
            checkbox = driver.find_element_by_xpath(
                '//*[@id="GENDER"]/div/div/div/div/div[2]/div[1]/div/input').click()
        elif gender == '女性':
            checkbox = driver.find_element_by_xpath(
                '//*[@id="GENDER"]/div/div/div/div/div[3]/div[1]/div/input').click()
        else:  # すべて
            checkbox = driver.find_element_by_xpath(
                '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div[1]/div[17]/div/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div/div[1]/div[1]/div/input').click()

        expected_conditions.element_selection_state_to_be(checkbox, True)

    # 配置
    placement_xpath = '//*[@id="campaignPlacementSection"]/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/div[1]/div'
    click_by_xpath(driver, placement_xpath)

    # デバイス
    device_select_xpath = '//*[@id="campaignPlacementSection"]/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div/div/span'
    try:
        driver.find_element_by_xpath(device_select_xpath).click()
    except:
        logging.info('デバイス選択テキストがありませんでした')

    device_selectbox_xpath = '//*[@id="campaignPlacementSection"]/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div'
    click_by_xpath(driver, device_selectbox_xpath)

    desktop_input_xpath = '/html/body/div[1]/div/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/ul/li[2]/div/div[1]'
    click_by_xpath(driver, desktop_input_xpath)

    placement_title_xpath = '//*[@id="placement-feed"]/div'
    click_by_xpath(driver, placement_title_xpath)
    wait()

    # プラットフォーム
    # Facebook
    fb_input_xpath = '//*[@id="placement-facebook/feed"]/div/input'
    # Instagram
    ig_input_xpath = '//*[@id="placement-instagram"]/div/div/input'
    # Audience Network
    an_input_xpath = '//*[@id="placement-audience_network"]/div/div/input'
    # メッセンジャー
    ms_input_xpath = '//*[@id="placement-messenger"]/div/div/input'

    stories_check_xpath = '//*[@id="placement-story"]/div/input'
    instream_check_xpath = '//*[@id="placement-stream"]/div/input'
    search_check_xpath = '//*[@id="placement-search"]/div/input'
    inpost_check_xpath = '//*[@id="placement-context"]/div/input'
    app_and_site_check_xpath = '//*[@id="placement-external"]/div/input'

    ig_st_xpath = '//*[@id="placement-instagram/story"]/div/input'
    ig_feed_xpath = '//*[@id="placement-instagram/stream"]/div/input'
    ig_find_xpath = '//*[@id="placement-instagram/explore"]/div/input'

    fb_st_xpath = '//*[@id="placement-facebook/stories"]/div/input'
    ms_st_xpath = '//*[@id="placement-messenger/story"]/div/input'

    fb_feed_xpath = '//*[@id="placement-facebook/feed"]/div/input'
    fb_news_feed_xpath = '//*[@id="placement-facebook/feed"]/div/input'

    if is_FBFD(campaign_settings):
        logging.info('FBFD')

        click_by_xpath(driver, ig_input_xpath)
        wait()
        click_by_xpath(driver, ig_input_xpath)
        wait()
        click_by_xpath(driver, an_input_xpath)
        wait()
        click_by_xpath(driver, ms_input_xpath)
        wait()
        click_by_xpath(driver, ms_input_xpath)
        wait()

        click_by_xpath(driver, fb_feed_xpath)
        wait()
        click_by_xpath(driver, fb_st_xpath)
        wait()
        click_by_xpath(driver, instream_check_xpath)
        wait()
        click_by_xpath(driver, search_check_xpath)
        wait()
        click_by_xpath(driver, inpost_check_xpath)
        wait()

    if is_IGFD(campaign_settings):
        logging.info('IGFD')
        click_by_xpath(driver, an_input_xpath)
        wait()
        click_by_xpath(driver, ms_input_xpath)
        wait()
        click_by_xpath(driver, ms_input_xpath)
        wait()
        click_by_xpath(driver, fb_input_xpath)
        wait()

        click_by_xpath(driver, ig_feed_xpath)
        wait()
        click_by_xpath(driver, ig_st_xpath)
        wait()

        click_by_xpath(driver, fb_news_feed_xpath)
        wait()
        click_by_xpath(driver, fb_st_xpath)
        wait()
        click_by_xpath(driver, inpost_check_xpath)
        wait()
        click_by_xpath(driver, search_check_xpath)
        wait()
        click_by_xpath(driver, instream_check_xpath)
        wait()

    if is_ST(campaign_settings):
        logging.info('ST')
        click_by_xpath(driver, instream_check_xpath)
        wait()
        click_by_xpath(driver, search_check_xpath)
        wait()
        click_by_xpath(driver, inpost_check_xpath)
        wait()
        click_by_xpath(driver, app_and_site_check_xpath)
        wait()


def wait_until_save(driver, xpath):
    while True:
        try:
            msg = driver.find_element_by_xpath(xpath).text
        except:
            wait()
            continue

        if msg == 'すべての変更が保存されました':
            break
        wait()


def is_FBFD(campaign_settings):
    return 'FBFD' in campaign_settings and campaign_settings['FBFD']


def is_IGFD(campaign_settings):
    return 'IGFD' in campaign_settings and campaign_settings['IGFD']


def is_ST(campaign_settings):
    return 'ST' in campaign_settings and campaign_settings['ST']


def wait():
    time.sleep(WAIT_TIME)


def long_wait():
    time.sleep(WAIT_TIME * 2)


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

user_data_dir = '--user-data-dir=/Users/nt/Library/Application Support/Google/Chrome/Profile 1/'
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
long_wait()

# -------------------------------------------------------------------------------------------------
# キャンペーン
# -------------------------------------------------------------------------------------------------
# 作成ボタン
create_button_xpath = '//*[@id="pe_toolbar"]/div/div/div/div[1]/div/span/div/div/div[2]'
click_by_xpath(driver, create_button_xpath)
wait()

# 認知アップ選択
click_element_by_id(driver, 'CONVERSIONS')
wait()

# 次へ選択
click_button_by_class_name(driver, '_271k _271m _1qjd layerConfirm _7tvm _7tv3 _7tv4')
click_button_by_class_name(driver, '_271k _271m _1qjd _7tvm _7tv3 _7tv4')

wait()

# キャンペーン名入力
clear_input(driver, '_58al')
input_element_by_class_name(driver, '_58al', value=campaign_settings['キャンペーン名'])

wait_until_save(driver, '//div[@class="_3b62"]/span')

button_xpath = '//div[@style="display: inline-block;"]/div[@style="display: inline-block;"]/button[@class="_271k _271m _1qjd _7tvm _7tv3 _7tv4"]'
click_by_xpath(driver, button_xpath)

wait()

# -------------------------------------------------------------------------------------------------
# 広告セット
# -------------------------------------------------------------------------------------------------
set_adset(driver, campaign_settings)

wait_until_save(driver, '//div[@class="_3b62"]/span')

save_button_xpath = '//div[@style="display: inline-block;"]/div[@style="display: inline-block;"]/button[@class="_271k _271m _1qjd _7tvm _7tv3 _7tv4"]'
click_by_xpath(driver, save_button_xpath)

wait()

for i, row in enumerate(creative_csv_reader):
    # -------------------------------------------------------------------------------------------------
    # 広告セットを複製
    # -------------------------------------------------------------------------------------------------
    if i > 0:
        logging.info("広告セットを複製")
        three_point_icon_xpath = '//*[@id="campaign_structure_tree_root"]/div/div[1]/div/div/div[2]/div/div/div/div[2]/div[1]'
        click_by_xpath(driver, three_point_icon_xpath)
        wait()

        quick_copy_xpath = '//*[@id="globalContainer"]/div[3]/div/div/div/div/ul/li[2]'
        click_by_xpath(driver, quick_copy_xpath)
        wait()

    # -------------------------------------------------------------------------------------------------
    # クリエイティブ
    # -------------------------------------------------------------------------------------------------
    # 広告を選択
    adset_count = 0
    while i != 0:
        try:
            adset_xpath = f'/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div/div[{adset_count + 2}]/div/div/div/div[1]/div/div/span'
            text = driver.find_element_by_xpath(adset_xpath).text
            hoge = re.match(r'^.*\s-\sコピー$', text)
            if re.match(r'^.*\s-\sコピー$', text):
                target_ad_xpath = f'/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div/div[{adset_count + 3}]/div/div/div/div[1]'

                if i > 0:
                    # コピーした広告セットをクリック
                    click_by_xpath(driver, adset_xpath)

                    # click_by_xpath(driver, adset_xpath)
                    # time.sleep(15)

                    # 広告セット名の ' - コピー'を削除する
                    adset_name_xpath = '//*[@id="campaignNameSection"]/div/div/div/div/div/div/div/div[2]/div/span/label/input'
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    driver.find_element_by_xpath(adset_name_xpath).send_keys(Keys.BACK_SPACE)
                    wait()

                    click_by_xpath(driver, target_ad_xpath)
                    long_wait()

                    break

            adset_count += 2
        except NoSuchElementException:
            logging.info('NoSuchElementException, at ad select.')
            break

    # シングル画像または動画を選択
    select_image_button = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[1]/div/ul/div[1]/div/div[1]/div/div[2]/div[1]/div/div/div/div[2]/div/div[1]/div/button'
    click_by_xpath(driver, select_image_button)
    wait()

    # 広告名を入力
    ad_name_input_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div/span/label/input'
    clear_input_by_xpath(driver, ad_name_input_xpath)
    input_element_by_xpath(driver, ad_name_input_xpath, value=row['広告名'])
    wait()

    if i == 0:
        # メディアを追加をクリック
        click_by_xpath(driver, '//*[@id="ads_pe_container"]/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[3]/div/span[1]/div/button')
        wait()

        # 画像を追加をクリック
        click_by_xpath(driver, '/html/body/div[1]/div/div/div/div[3]/div/div/div/div/div/div[1]/div/div/ul/li[1]/div')
        wait()
    else:
        # 編集ボタンをクリック
        edit_button_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/ul/div/div/div[1]'
        click_by_xpath(driver, edit_button_xpath)
        wait()

        # メディアを変更ボタンをクリック
        edit_media_button_xpath = '/html/body/div[6]/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/div/div/div'
        click_by_xpath(driver, edit_media_button_xpath)
        wait()

    file_name = row['ファイル名']
    main_text = row['メインテキスト']

    image_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'image/{file_name}')
    image_input_xpath = '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/input'
    driver.find_element_by_xpath(
        image_input_xpath
    ).send_keys(image_file)
    wait()

    logging.info(f'upload complete {file_name}')

    # アップロードした画像ファイルをクリック
    count = 1
    while True:
        image_name_xpath = f'/html/body/div[6]/div[2]/div/div/div/div/div/div/div[1]/div/div/div/div[2]/div[4]/div[1]/div/div/div[{count}]/div/div/div[2]/div'

        text = driver.find_element_by_xpath(image_name_xpath).text
        if text == file_name:
            click_by_xpath(driver, image_name_xpath)
            wait()
            break

        count += 1

    # 次へ
    next_button = '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div'
    click_by_xpath(driver, next_button)
    wait()

    # 次へ
    next_confirm_button = '/html/body/div[6]/div[2]/div/div/div/div/div/div/div[2]/span[2]/div/div[2]/div/div'
    click_by_xpath(driver, next_confirm_button)
    wait()

    # 見出し
    if '見出し' in row:
        title_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/textarea'
        clear_input_by_xpath(driver, title_xpath)
        title_value = row['見出し']
        title_element = driver.find_element_by_xpath(title_xpath).send_keys(title_value)

    # 説明
    if '説明' in row and is_FBFD(campaign_settings):
        description_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[1]/textarea'
        clear_input_by_xpath(driver, description_xpath)
        description_value = row['説明']
        description_element = driver.find_element_by_xpath(description_xpath).send_keys(description_value)

    if i == 0:
        # ウェブサイトのURL
        if 'ウェブサイトのURL' in row:
            url_xpath = '//*[@id="ads_pe_container"]/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[4]/div/div/div/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div/div/div[1]/textarea'
            clear_input_by_xpath(driver, url_xpath)
            url_value = row['ウェブサイトのURL']
            url_element = driver.find_element_by_xpath(url_xpath).send_keys(url_value)

    # メインテキスト
    if i != 0:
        main_text_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/span'
        while True:
            driver.find_element_by_xpath(main_text_xpath).send_keys(Keys.DELETE)
            try:
                input_text = driver.find_element_by_xpath(main_text_xpath).text.strip("\"")
            except:
                break

            if input_text == '':
                break

    main_text_xpath = '/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/span/br'
    main_text_element = driver.find_element_by_xpath(main_text_xpath)
    main_text_value = row['メインテキスト']
    main_text_element.send_keys(main_text_value.strip().strip("\""))


    while True:
        try:
            msg = driver.find_element_by_xpath(f'//div[@class="_3b62"]/span').text
        except:
            wait()
            continue

        if msg == 'すべての変更が保存されました':
            break

        wait()

    logging.info('保存完了')


wait()

print('終了します')
logging.debug('終了')

# 終了
# driver.quit()
