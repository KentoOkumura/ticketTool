# -*- coding: utf-8 -*-
#from datetime import datetime
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import time
import sched
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import getpass
import requests
import json
import threading
import re

#options = webdriver.ChromeOptions()
#options.add_argument('--user-data-dir=C:\\Users\\kento\\Desktop\\Python\\profile_data')
#driver = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe', options=options)
#driver = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe')

th_objs    = [] #スレッドの配列
cap_objs   = []
driver     = {} #各スレッドのwebdriverオブジェクト格納用
recaptchas = []
break_cap  = {}
recaptcha_page = None

#ブラウザのサイズと表示位置
# browsers = [
#     { "size-x": "640", "size-y": "360", "pos-x": "0",   "pos-y": "0"},
#     { "size-x": "640", "size-y": "360", "pos-x": "640", "pos-y": "0"},
#     { "size-x": "640", "size-y": "360", "pos-x": "0",   "pos-y": "360"},
#     { "size-x": "640", "size-y": "360", "pos-x": "640", "pos-y": "360"}
# ]

browsers = [
    { "size-x": "240", "size-y": "420", "pos-x": "0",   "pos-y": "300"}
    ]

# browsers = [
#     { "size-x": "240", "size-y": "420", "pos-x": "0",   "pos-y": "0"},
#     { "size-x": "240", "size-y": "420", "pos-x": "320", "pos-y": "0"},
#     { "size-x": "240", "size-y": "420", "pos-x": "640", "pos-y": "0"},
#     { "size-x": "240", "size-y": "420", "pos-x": "960", "pos-y": "0"},
#     { "size-x": "240", "size-y": "420", "pos-x": "0",   "pos-y": "360"},
#     { "size-x": "240", "size-y": "420", "pos-x": "320", "pos-y": "360"},
#     { "size-x": "240", "size-y": "420", "pos-x": "640", "pos-y": "360"},
#     { "size-x": "240", "size-y": "420", "pos-x": "960", "pos-y": "360"}
# ]


start_time = '2019-08-11 12:00:00.000000'

def start_browser(idx, tid):
    
    browser = browsers[idx]
    driver[tid] = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe')

    #位置とサイズ指定
    driver[tid].set_window_size(browser['size-x'], browser['size-y'])
    driver[tid].set_window_position(browser['pos-x'], browser['pos-y'])

    while True:
        if "楽天会員ログイン" in driver[tid].page_source:
            break
        driver[tid].get('https://rt.tstar.jp/orderreview/mypage')
    driver[tid].find_element_by_id('loginInner_u').send_keys('kentookumura6@gmail.com')
    driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
    driver[tid].find_element_by_class_name('loginButton').click()
    
def uncaptcha(idx):

    while True:
        if break_cap[idx] == 1:
            break
        print (idx)
        service_key     = '7faed6a88ee62d38c1e16e8eda0e4a67'         # 2captcha service key API KEY
        google_site_key = '6LdanyoUAAAAAOh3LNep4EtZaKV19dCE92gMCAcl' # reCAPTCHAのdata-sitekey
        while recaptcha_page is None:
            pass
        url             = "http://2captcha.com/in.php?key=" + service_key + "&method=userrecaptcha&googlekey=" + google_site_key + "&recaptcha_page=" + recaptcha_page
        resp            = requests.get(url)
        
        if resp.text[0:2] != 'OK': 
            quit('Service error. Error code:' + resp.text)
        captcha_id = resp.text[3:]    
        fetch_url  = "http://2captcha.com/res.php?key="+ service_key + "&action=get&id=" + captcha_id

        while True:
            time.sleep(0.5)
            resp = requests.get(fetch_url)
            if resp.text[0:2] == 'OK':
                break
            
        print('Google response token: ', resp.text[3:])
        recaptchas.append( {'get_time':datetime.datetime.now(), 'key':resp.text[3:]} )
        print ('recaptchasの長さ',len(recaptchas)) 

        time.sleep(60)
    
def load(idx, tid):

    while True:
    #driver[tid].find_element_by_class_name('cart-button').click()
        
        driver[tid].get('https://ticket.rakuten.co.jp/music/jpop/rtdgegs/')
        #driver[tid].get('https://ticket.rakuten.co.jp/music/jpop/idle/rtodaal/')            
        driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        try:
            page_id = driver[tid].find_element_by_xpath('/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a').get_attribute('href').split('agreement/')[1]
        except:
            continue
        
        driver[tid].find_element_by_xpath('/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a').click()
        global recaptcha_page
        recaptcha_page = 'https://rt.tstar.jp/cart/performances/{}/recaptcha'
        recaptcha_page = recaptcha_page.format(page_id)
        
        if "楽天会員ログイン" in driver[tid].page_source:
            driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
            driver[tid].find_element_by_class_name('loginButton').click()
        if driver[tid].current_url == recaptcha_page or "開催日" in driver[tid].page_source:
            break
    

    if driver[tid].current_url == recaptcha_page:
        wait = WebDriverWait(driver[tid], 5)
        wait.until(EC.presence_of_element_located( (By.ID,'g-recaptcha-response') ))
        driver[tid].execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
        #driver[tid].find_element_by_id('g-recaptcha-response').send_keys(recaptcha[tid])

        while len(recaptchas) == 0:
            pass
        recaptcha = recaptchas[0]
        print(recaptcha['get_time'])
        while True:
            time_diff = datetime.datetime.now() - recaptcha['get_time']
            if time_diff.seconds < 110:
                break
            print('取得してから2分経過')
            recaptchas.pop(0) #取得してから2分経ったキーは捨てる
            print ('recaptchasの長さ',len(recaptchas))
            recaptcha = recaptchas[0]

        exe_captcha = recaptcha
        recaptchas.pop(0) #使ったキーは捨てる
        driver[tid].find_element_by_id('g-recaptcha-response').send_keys(exe_captcha['key'])
        driver[tid].find_element_by_css_selector("input[type='submit']").click()
        break_cap[idx] = 1
        print (break_cap)


    #driver.execute_script('var element=document.getElementById("selectProductTemplate"); element.style.display="";')
    # driver[tid].find_element_by_css_selector("#seatTypeList > li").click()
    # seat_element= driver[tid].find_element_by_css_selector("#selectProductTemplate > div.productListContainer > ul.productList.payment-seat-products > li > span.productQuantity > select")
    # seat_select_element = Select(seat_element)
    # driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # wait = WebDriverWait(driver[tid], 5)
    # wait.until(EC.element_to_be_clickable( (By.CSS_SELECTOR,"#selectProductTemplate > div.productListContainer > ul.productList.payment-seat-products > li > span.productQuantity > select")))
    # seat_select_element.select_by_value('2')
    
    #wait.until(EC.element_to_be_clickable( (By.CSS_SELECTOR,"#selectProductTemplate > div.productListContainer > ul.buttonSet > li:nth-child(2) > a")))
    #driver.find_element_by_css_selector("#selectProductTemplate > div.productListContainer > ul.buttonSet > li:nth-child(2) > a").click()


def run(idx, start_time):

    tid = threading.get_ident()
    #ブラウザ立ち上げ
    start_browser(idx, tid)

    #チケットページアクセス
    scheduler = sched.scheduler(time.time, time.sleep)
    run_at    = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(seconds = 0.02)*idx #6 digit
    run_at    = int(time.mktime(run_at.utctimetuple()))
    scheduler.enterabs(run_at, 1, load, (idx, tid,))
    scheduler.run()

    
if __name__ == "__main__":

    for idx in range(0,len(browsers)):
        th_objs.append(threading.Thread(target=run, args=(idx, start_time)))
        #cap_objs.append(threading.Thread(target=uncaptcha, args=(idx,)))
        break_cap[idx] = 0

    for i in range(0,len(browsers)):
        th_objs[i].start()
        #cap_objs[i].start()

    time.sleep(1200)


    
# time.sleep(20)
# seat_element = driver.find_element_by_name('product-3008102')
# seat_select_element = Select(seat_element)
# seat_select_element.select_by_value('2')
#time.sleep(5)
#driver.quit()


    # while '404' in cur_url or "アクセスが集中している為" in driver[tid].page_source or "販売期間にアクセスして" in driver[tid].page_source:
    #     driver[tid].get('https://rt.tstar.jp/cart/performances/21667')
    #     cur_url = driver[tid].current_url
