import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

# variables
WAIT_TIME = 3

options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=/Users/nt/Library/Application\ Support/Google/Chrome')
options.add_argument('--profile-directory=Profile\ 1')

driver = webdriver.Chrome(options=options)
actions = ActionChains(driver)

# search_text = '参考記事'
search_text = 'kijisample.com'

while True:
    driver.get('https://www.chatwork.com/')
    # time.sleep(50)
    time.sleep(WAIT_TIME)

    search_input_xpath = '/html/body/div[3]/div[3]/div[3]/headersearch/div/div/div/input'
    search_input_element = driver.find_element_by_xpath(search_input_xpath)
    search_input_element.send_keys(search_text)
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

    time.sleep(WAIT_TIME)

    # TODO メッセージがない場合に終了する
    if False:
        break

    # 一覧から選択
    search_id = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/div[1]').get_attribute("id")
    message_id = search_id.replace('_search', '')
    actions.move_to_element(driver.find_element_by_id(search_id)).perform()
    driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div[3]/div/div[3]/div/div[2]/div[1]/div[3]/ul/li[1]/span').click()

    time.sleep(WAIT_TIME)

    # 先頭の投稿にマウスオーバー
    top_post = driver.find_element_by_id(message_id)
    actions.move_to_element(top_post)
    top_post.click()

    time.sleep(WAIT_TIME)

driver.quit()
