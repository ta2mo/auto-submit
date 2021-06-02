import time

from selenium import webdriver

# 新しいタブでgoogleを開くサンプル

driver = webdriver.Chrome()

original_window = driver.current_window_handle

driver.get('http://yahoo.co.jp/')

driver.execute_script("window.open()") #make new tab

time.sleep(3)

for i, window_handle in enumerate(driver.window_handles):
    if window_handle == original_window:
        new_window = driver.window_handles[i + 1]
        driver.switch_to.window(new_window)
        driver.get('http://google.com/')
        break

time.sleep(3)

driver.quit()
