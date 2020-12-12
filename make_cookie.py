# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import os
import configparser

# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
# --------------------------------------------------
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

# --------------------------------------------------
# config.iniから値取得
# --------------------------------------------------
userID           = config_ini['DEFAULT']['userID']
password         = config_ini['DEFAULT']['password']

# --------------------------------------------------
# 初期化処理
# --------------------------------------------------
options = webdriver.ChromeOptions()

#ブラウザのサイズと表示位置
browser = { "size-x": "1280", "size-y": "720", "pos-x": "0", "pos-y": "0"}
driver  = None

options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')


def start_browser():
    global driver
    driver = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe',options=options)
    #位置とサイズ指定
    driver.set_window_size(browser['size-x'], browser['size-y'])
    driver.set_window_position(browser['pos-x'], browser['pos-y'])

    
def init(n):

    driver.get('https://rt.tstar.jp/orderreview/mypage')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)

    driver.find_element_by_id('loginInner_u').send_keys(userID)
    driver.find_element_by_id('loginInner_p').send_keys(password)
    driver.find_element_by_class_name('loginButton').click()
    cookie_file = "cookie\cookie{}.pkl".format(n)
    pickle.dump(driver.get_cookies() , open(cookie_file,"wb"))
    
        
def run():
    
    for n in range(10, 40):
        #ブラウザ立ち上げ
        start_browser()
        #クッキー取得
        init(n)

        driver.quit()
    
if __name__ == "__main__":
    run()

