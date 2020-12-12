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
from selenium.webdriver.common.action_chains import ActionChains
import getpass
import requests
import json
import threading
import re
import pickle
import subprocess
from queue import Queue

th_objs    = [] #スレッドの配列
driver     = {} #各スレッドのwebdriverオブジェクト格納用
recaptchas = []
break_cap  = 0
recaptcha_page = None
loopflg = True

#proc    = subprocess.Popen('c:\\Users\\kento\\Desktop\\Python\\Tor Browser\\Browser\\firefox.exe')
options = webdriver.ChromeOptions()
#proxy   = ['140.227.230.89:60088', '140.227.74.14:3128']
proxy   = '140.227.74.14:3128'
#options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
fifo = Queue()
for i in proxy:
    fifo.put(i)

options.add_argument('--proxy-server=http://%s' % proxy)

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


start_time      = '2019-12-28 10:00:00.000000'
#ticket_page     = 'https://ticket.rakuten.co.jp/music/RTCTAEH/?scid=we_twt_free_826aska_20191228'
ticket_page     = 'https://ticket.rakuten.co.jp/music/jpop/visual/rtdgnig/'
purchase_button = '/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[6]/div[3]/div[2]/div[2]/div[2]/div/a'


def start_browser(idx, tid):
    
    browser     = browsers[idx]
    driver[tid] = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe',options=options)

    #位置とサイズ指定
    driver[tid].set_window_size(browser['size-x'], browser['size-y'])
    driver[tid].set_window_position(browser['pos-x'], browser['pos-y'])

    
def init(idx, tid):
    
    cookie_file = 'cookie{}.pkl'.format(idx)
    pickle.dump(driver[tid].get_cookies() , open(cookie_file,"wb"))
    cookies     = pickle.load(open(cookie_file, "rb"))
    
    #クッキー初期化
    for cookie in cookies:
        driver[tid].add_cookie(cookie)
    driver[tid].delete_all_cookies()

    for cookie in cookies:
        print(cookie)

    #クッキー取得
    while True:
        if "楽天会員ログイン" in driver[tid].page_source:
            break
        driver[tid].get('https://rt.tstar.jp/orderreview/mypage')
    driver[tid].find_element_by_id('loginInner_u').send_keys('kentookumura6@gmail.com')
    driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
    driver[tid].find_element_by_class_name('loginButton').click()
    pickle.dump(driver[tid].get_cookies() , open(cookie_file,"wb"))

    driver[tid].get('https://rt.tstar.jp/orderreview/mypage')
    cookies = pickle.load(open(cookie_file, "rb"))
    for cookie in cookies:
        driver[tid].add_cookie(cookie)

        
def do_exec(idx, tid):
    
    global recaptcha_page
    global loopflg
    #while True:
    for n in range(50):
        if recaptcha_page is None:
            driver[tid].get(ticket_page)
            driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #actions = ActionChains(driver[tid])
            #actions.move_to_element(driver[tid].find_element_by_xpath(purchase_button))
            #actions.perform()
        
            try:
                page1 = driver[tid].find_element_by_xpath(purchase_button).get_attribute('href').split('/agreement')[0]
            except:
                continue
            page2 = driver[tid].find_element_by_xpath(purchase_button).get_attribute('href').split('/agreement')[1]
            driver[tid].find_element_by_xpath(purchase_button).click()
            recaptcha_page = page1 + page2 + '/recaptcha'

        else:
            #driver[tid].get(recaptcha_page)
            driver[tid].execute_script('location.reload(true);')
        
        if "楽天会員ログイン" in driver[tid].page_source:
            driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
            driver[tid].find_element_by_class_name('loginButton').click()
            
        WebDriverWait(driver[tid], 30).until(EC.presence_of_all_elements_located)            
        #if (driver[tid].current_url == recaptcha_page and not('アクセスが集中している為' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
        if (driver[tid].current_url == recaptcha_page and ('不正な申込みを防ぐため、認証を行います。チェックを入れて、次へボタンを押してください' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
            #pass
            loopflg = False
            break

        
def select_ticket(idx, tid):
    driver[tid].execute_script('var element=document.getElementById("selectProductTemplate"); element.style.display="";')
    driver[tid].find_element_by_css_selector("#seatTypeList > li").click()
    seat_element = driver[tid].find_element_by_css_selector("#selectProductTemplate > div.productListContainer > ul.productList.payment-seat-products > li > span.productQuantity > select")
    seat_select_element = Select(seat_element)
    driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
    wait = WebDriverWait(driver[tid], 5)
    wait.until(EC.element_to_be_clickable( (By.CSS_SELECTOR,"#selectProductTemplate > div.productListContainer > ul.productList.payment-seat-products > li > span.productQuantity > select")))
    seat_select_element.select_by_value('2')
    
    wait.until(EC.element_to_be_clickable( (By.CSS_SELECTOR,"#selectProductTemplate > div.productListContainer > ul.buttonSet > li:nth-child(3) > a")))
    driver[tid].find_element_by_css_selector("#selectProductTemplate > div.productListContainer > ul.buttonSet > li:nth-child(3) > a").click()

    try:
        driver[tid].find_element_by_xpath('/html/body/div[9]/div[2]/div[2]/a[2]').click()
    except:
        pass

    
# def settlement(idx, tid):
#     /html/body/div[1]/div[2]/form/div[1]/div/div[1]/div/table/tbody/tr[1]/td[2]/dl/dt
#     /html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/table/tbody/tr[1]/td[2]/dl/dt
#     /html/body/div[1]/div[2]/form/div[1]/div/div[3]/div/table/tbody/tr[1]/td[2]/dl/dt

#     /html/body/div[1]/div[2]/form/div[1]/div/div[1]/div/table/tbody/tr[1]/td[1]/input
#     /html/body/div[1]/div[2]/form/div[1]/div/div[2]/div/table/tbody/tr[1]/td[1]/input
#     /html/body/div[1]/div[2]/form/div[1]/div/div[3]/div/table/tbody/tr[1]/td[1]/input

#     /html/body/div[1]/div[2]/form/p/img
    
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
        time.sleep(3.0)
        resp = requests.get(fetch_url)
        if resp.text[0:2] == 'OK':
            break
            
    print('Google response token: ', resp.text[3:])
    recaptchas.append( {'get_time':datetime.datetime.now(), 'key':resp.text[3:]} )
    print ('recaptchasの長さ',len(recaptchas)) 

    
def load(idx, tid):

    while(loopflg):
        do_exec(idx, tid)
        if not loopflg:
            break
        #クッキー初期化
        init(idx, tid)

    if driver[tid].current_url == recaptcha_page:
        wait = WebDriverWait(driver[tid], 5)
        wait.until(EC.presence_of_element_located( (By.ID,'g-recaptcha-response') ))
        # driver[tid].execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')

        # while True:
        #     while len(recaptchas) == 0:
        #         pass
        #     recaptcha = recaptchas[0]
        #     print(recaptcha['get_time'])            
        #     time_diff = datetime.datetime.now() - recaptcha['get_time']
        #     if time_diff.seconds < 110:
        #         break
        #     print('取得してから2分経過')
        #     recaptchas.pop(0) #取得してから2分経ったキーは捨てる
        #     print ('recaptchasの長さ',len(recaptchas))

        # exe_captcha = recaptcha
        # recaptchas.pop(0) #使ったキーは捨てる
        # driver[tid].find_element_by_id('g-recaptcha-response').send_keys(exe_captcha['key'])
        # driver[tid].find_element_by_css_selector("input[type='submit']").click()
        # global break_cap
        # break_cap = 1
        # print('recaptcha 突破')

        time.sleep(60)
        select_ticket(idx, tid)
        
def run(idx, start_time):
    
    tid = threading.get_ident()
    #ブラウザ立ち上げ
    start_browser(idx, tid)
    #クッキー初期化
    init(idx, tid)

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

    # while True:
    #     if break_cap == 1:
    #         break
    #     cap_objs = threading.Thread(target=uncaptcha)
    #     cap_objs.start()
    #     cap_objs.join()
    #     time.sleep(60)

    time.sleep(1200)
