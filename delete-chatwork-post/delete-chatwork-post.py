import configparser
import json
import logging
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def mouse_over_at_post(driver, message_id):
    retry_count = 0
    result = False
    while retry_count < 10:
        # 読込中マークの確認
        try:
            driver.find_element_by_xpath('//*[@id="_chatContent"]/div[@class="sc-eOnLuU OfsCi"]')
            retry_count += 1
            logging.debug('now loading.')
            time.sleep(5)
            continue
        except NoSuchElementException:
            logging.debug('loading complete.')

        # 先頭の投稿にマウスオーバー
        try:
            top_post = driver.find_element_by_id(message_id)
        except Exception:
            logging.info(f'post not found.message_id={message_id}')
            with open(f'debug{message_id}.html', mode="w") as f:
                f.write(driver.page_source)
            retry_count += 1
            continue

        post_list_actions = ActionChains(driver)
        post_list_actions.move_to_element(top_post)
        try:
            post_list_actions.perform()
        except Exception:
            logging.info(
                f'stale element reference: element is not attached to the page document. message_id={message_id}')
            retry_count += 1
            return False

        try:
            driver.find_element_by_xpath(f'//*[@id="{message_id}"]/div[3]/ul/li[5]/button').click()
        except NoSuchElementException:
            driver.execute_script('window.scroll(0,100);')
            retry_count += 1
            continue
        except Exception:
            logging.info(f"throw Exception.message_id={message_id}")
            with open(f'debug{message_id}.html', mode="w") as f:
                f.write(driver.page_source)
            result = False
            break

        result = True
        break
    return result


def delete_post(driver, search_word):
    loop_count = 0
    retry_count = 0
    while True:
        if retry_count >= 10:
            logging.info(f'over retry 10 count. retry_count={retry_count}, search_word={search_word}')
            with open(f'debug_cannot_retry.html', mode="w") as f:
                f.write(driver.page_source)
            break

        driver.get('https://www.chatwork.com/')
        time.sleep(WAIT_TIME)

        search_input_xpath = '/html/body/div[3]/div[3]/div[3]/headersearch/div/div/div/input'
        try:
            search_input_element = driver.find_element_by_xpath(search_input_xpath)
        except Exception:
            retry_count += 1
            logging.info('search_input_element not found. and retry.')
            time.sleep(5)
            continue

        search_input_element.send_keys(search_word)
        search_input_element.send_keys(Keys.ENTER)

        time.sleep(WAIT_TIME)

        # 検索オプション
        driver.find_element_by_id('_messageSearchOption').click()

        time.sleep(WAIT_TIME)

        driver.find_element_by_id('_messageSearchSpeaker').click()

        # 自分を選択
        driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[55]/ul/li[1]').click()

        # 検索ボタン押下
        driver.find_element_by_id('_messageSearchSend').click()

        time.sleep(7)

        # メッセージがない場合に終了する
        try:
            ele = driver.find_element_by_xpath(
                '/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/div[@class="searchNotFound alert alertWarning"]')
            if ele.text == f'{search_word} に一致する検索結果は見つかりませんでした':
                logging.info(f'{search_word} に一致する検索結果は見つかりませんでした')
                break
            else:
                logging.info(f'検索結果あり. loop_count={loop_count}, search_word={search_word}')
        except Exception:
            logging.info(f'検索結果あり. loop_count={loop_count}')

        # 一覧から選択
        ## 削除されたメッセージでないか確認
        top_post_pre_xpath = '/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/div[1]/div[1]/div[2]/pre/div'
        try:
            if driver.find_element_by_xpath(top_post_pre_xpath).text == 'メッセージは削除されました':
                div_path = 'div[2]'
            else:
                div_path = 'div[1]'
        except NoSuchElementException:
            div_path = 'div[1]'

        try:
            top_post_element = driver.find_element_by_xpath(
                f'/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/{div_path}')
        except Exception:
            logging.info('no post.')
            break

        search_id = top_post_element.get_attribute("id")
        message_id = search_id.replace('_search', '')
        search_list_actions = ActionChains(driver)
        search_list_actions.move_to_element(driver.find_element_by_id(search_id)).perform()
        driver.find_element_by_xpath(
            f'/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/{div_path}/div[3]/ul/li[1]/span').click()

        time.sleep(WAIT_TIME)

        if not mouse_over_at_post(driver, message_id):
            logging.info(f'can not mouse over. message_id={message_id}')
            with open(f'debug_{message_id}.html', mode="w") as f:
                f.write(driver.page_source)
            retry_count += 1
            continue

        time.sleep(WAIT_TIME)

        # ホバーして表示されるメニューの削除ボタンを押す
        try:
            driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[77]/div/div/ul/li[3]/button/span[2]').click()
        except Exception:
            logging.info(f"delete button not found.message_id={message_id}")
            with open(f'debug{message_id}.html', mode="w") as f:
                f.write(driver.page_source)

        time.sleep(WAIT_TIME)

        # モーダルの削除ボタンを押す
        try:
            driver.find_element_by_xpath('/html/body/div[6]/div/div[2]/div[2]').click()
        except NoSuchElementException:
            logging.info(f'with file post. delete file button click.')
            driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[6]/div/div[2]/div[2]').click()
        except Exception:
            logging.info(f"modal delete button not found.message_id={message_id}")
            with open(f'debug{message_id}.html', mode="w") as f:
                f.write(driver.page_source)

        time.sleep(WAIT_TIME)
        retry_count = 0
        loop_count += 1
    logging.info(f'loop end. count={loop_count}')


# -------------------------------------------------------------------------------------------------
# config
# -------------------------------------------------------------------------------------------------
config = configparser.ConfigParser()
config.read('config.ini')

# variables
WAIT_TIME = 3

logging.basicConfig(filename='./debug.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
logging.info('start')

options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=/Users/nt/Library/Application\ Support/Google/Chrome')
options.add_argument('--profile-directory=Profile\ 1')
options.add_argument('--disable-dev-shm-usage')  # invalid session id対策

driver = webdriver.Chrome(options=options)

# 検索文字列
search_words = json.loads(config['DEFAULT']['search_words'])

for search_word in search_words:
    logging.info(f'search_word={search_word} start.')
    delete_post(driver, search_word)
    logging.info(f'search_word={search_word} end.')

driver.quit()
logging.info('end')
