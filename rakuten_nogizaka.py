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
import pickle

th_objs    = [] #スレッドの配列
driver     = {} #各スレッドのwebdriverオブジェクト格納用
recaptchas = []
break_cap  = 0
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
    pickle.dump(driver[tid].get_cookies() , open("cookies.pkl","wb"))

    
def uncaptcha():

    service_key     = '7faed6a88ee62d38c1e16e8eda0e4a67'         # 2captcha service key API KEY
    google_site_key = '6LdanyoUAAAAAOh3LNep4EtZaKV19dCE92gMCAcl' # reCAPTCHAのdata-sitekey
    
    while recaptcha_page is None:
        pass
    url             = "http://2captcha.com/in.php?key=" + service_key + "&method=userrecaptcha&googlekey=" + google_site_key + "&pageurl=" + recaptcha_page
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

    
def load(idx, tid):
    
    global recaptcha_page
    while True:
        if recaptcha_page is None:
            #driver[tid].get('https://ticket.rakuten.co.jp/music/jpop/idle/rtodaal/')
            driver[tid].get('https://ticket.rakuten.co.jp/music/kpop/RTKTAEI/?scid=we_twt_free_pentagon_kn_20191213')
            driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
            try:
                page1 = driver[tid].find_element_by_xpath('/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a').get_attribute('href').split('/agreement')[0]
            except:
                continue

            page2 = driver[tid].find_element_by_xpath('/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a').get_attribute('href').split('/agreement')[1]
            driver[tid].find_element_by_xpath('/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a').click()
            recaptcha_page = page1 + page2 + '/recaptcha'

        else:
            driver[tid].get(recaptcha_page)
        
        if "楽天会員ログイン" in driver[tid].page_source:
            driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
            driver[tid].find_element_by_class_name('loginButton').click()
        #if (driver[tid].current_url == recaptcha_page and not('アクセスが集中している為' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
        if (driver[tid].current_url == recaptcha_page and ('私はロボットではありません' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
            break

    if driver[tid].current_url == recaptcha_page:
        wait = WebDriverWait(driver[tid], 5)
        wait.until(EC.presence_of_element_located( (By.ID,'g-recaptcha-response') ))
        driver[tid].execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')

        while True:
            while len(recaptchas) == 0:
                pass
            recaptcha = recaptchas[0]
            print(recaptcha['get_time'])            
            time_diff = datetime.datetime.now() - recaptcha['get_time']
            if time_diff.seconds < 110:
                break
            print('取得してから2分経過')
            recaptchas.pop(0) #取得してから2分経ったキーは捨てる
            print ('recaptchasの長さ',len(recaptchas))

        exe_captcha = recaptcha
        recaptchas.pop(0) #使ったキーは捨てる
        driver[tid].find_element_by_id('g-recaptcha-response').send_keys(exe_captcha['key'])
        driver[tid].find_element_by_css_selector("input[type='submit']").click()
        global break_cap
        break_cap = 1
        print('recaptcha 突破')


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

    for i in range(0,len(browsers)):
        th_objs[i].start()

    while True:
        if break_cap == 1:
            break
        cap_objs = threading.Thread(target=uncaptcha)
        cap_objs.start()
        cap_objs.join()
        # while cap_objs.is_alive():
        #     pass
        time.sleep(60)

    time.sleep(1200)
