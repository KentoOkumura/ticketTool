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
from bs4 import BeautifulSoup
import lxml
import os

nbrowser   = 4
do_proxy   = False
start_time = '2020-02-02 12:00:00.000000'

th_objs    = [] #スレッドの配列
driver     = {} #各スレッドのwebdriverオブジェクト格納用
recaptchas = []
break_cap  = 0
recaptcha_page = None
purchase_page  = None
#purchase_page  = 'https://rt.tstar.jp/cart/performances/agreement/141900'
loopflg     = [None]*nbrowser
proxy       = [None]*nbrowser
cookie      = [None]*nbrowser
cookie_file = [None]*nbrowser

headers = {'User-Agent':'Mozilla/5.0'}
options = webdriver.ChromeOptions()
#proxys  = ['160.16.218.54:80', '118.27.31.50:3128', '118.106.145.247:80', '133.86.253.49:80', '61.115.1.182:80', '47.74.38.43:8118', '61.118.35.94:55725', '150.95.131.174:3128', '133.167.108.124:3128', '140.227.230.89:60088', '140.227.74.14:3128', '133.167.93.190:3128', '140.227.31.224:6000', '140.227.202.194:6000', '140.227.211.209:6000', '140.227.52.41:6000']
proxys  = ['192.168.0.2:3128', '36.55.230.146:8888', '140.227.230.89:60088', '140.227.31.224:6000', '140.227.52.41:6000', '118.27.31.50:3128', '150.95.131.174:3128', '118.106.145.247:80', '160.16.101.98:80', '126.72.57.78:51929', '160.16.218.54:80', '103.3.188.101:80', '61.115.1.182:80', '133.86.253.49:80']

#options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

fifo = Queue()
cookie_fifo = Queue()
fifo.put('127.0.0.1:9150')

for x in os.listdir(os.getcwd()):
    if(x[-4:] == '.pkl'):
        cookie_fifo.put(x)
    
ncookies = cookie_fifo.qsize()

#ブラウザのサイズと表示位置
if nbrowser == 1:
    browsers = [
        { "size-x": "1280", "size-y": "720", "pos-x": "0",   "pos-y": "0"}
    ]
elif nbrowser == 2:
    browsers = [
        { "size-x": "640", "size-y": "720", "pos-x": "0",   "pos-y": "0"},
        { "size-x": "640", "size-y": "720", "pos-x": "640", "pos-y": "0"}
    ]
elif nbrowser == 4:
    browsers = [
        { "size-x": "640", "size-y": "360", "pos-x": "0",   "pos-y": "0"},
        { "size-x": "640", "size-y": "360", "pos-x": "640", "pos-y": "0"},
        { "size-x": "640", "size-y": "360", "pos-x": "0",   "pos-y": "360"},
        { "size-x": "640", "size-y": "360", "pos-x": "640", "pos-y": "360"}
    ]
elif nbrowser == 8:
    browsers = [
        { "size-x": "240", "size-y": "420", "pos-x": "0",   "pos-y": "0"},
        { "size-x": "240", "size-y": "420", "pos-x": "320", "pos-y": "0"},
        { "size-x": "240", "size-y": "420", "pos-x": "640", "pos-y": "0"},
        { "size-x": "240", "size-y": "420", "pos-x": "960", "pos-y": "0"},
        { "size-x": "240", "size-y": "420", "pos-x": "0",   "pos-y": "360"},
        { "size-x": "240", "size-y": "420", "pos-x": "320", "pos-y": "360"},
        { "size-x": "240", "size-y": "420", "pos-x": "640", "pos-y": "360"},
        { "size-x": "240", "size-y": "420", "pos-x": "960", "pos-y": "360"}
    ]

ticket_page     = 'https://ticket.rakuten.co.jp/music/jpop/RTZPAHC/'
#ticket_page     = 'https://ticket.rakuten.co.jp/music/classic/rtjmete/?scid=we_twt_free_mujikaeteruna_20200201'
#purchase_button = '/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[5]/div[2]/div[3]/div[3]/div[2]/div[2]/div/a'
purchase_button = '/html/body/div[2]/div[3]/div/main/article/div/div/div/div/div[4]/div[3]/div[3]/div[2]/div[2]/div/a'

options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')


def start_browser(idx, tid):
    global proxy, fifo, options

    if(do_proxy):
        proxy[idx] = fifo.get()
        print(proxy)

        #localhostであればproxy設定しない
        if(proxy[idx] == '127.0.0.1:9150'):
            print('localhost')
            pass
        else:
            options.add_argument('--proxy-server=http://%s' % proxy[idx])
    
    browser     = browsers[idx]
    driver[tid] = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe',options=options)

    #位置とサイズ指定
    driver[tid].set_window_size(browser['size-x'], browser['size-y'])
    driver[tid].set_window_position(browser['pos-x'], browser['pos-y'])

    
def init(idx, tid):

    global cookie, cookie_fifo, cookie_file

    cookie_file[idx] = cookie_fifo.get()
    cookie[idx]      = pickle.load(open(cookie_file[idx], "rb"))
    #cookie[idx]      = pickle.load(open('cookie1.pkl', "rb"))
    print(cookie_file[idx])

    driver[tid].get('http://www.google.com')    
    for i in cookie[idx]:
        driver[tid].add_cookie(i)

    driver[tid].get('https://rt.tstar.jp/cart/performances/agreement/141900')
        
def do_exec(idx, tid):
    
    global recaptcha_page, purchase_page, loopflg
    
    # if purchase_page is not None:
    #     try:
    #         driver[tid].get(purchase_page)
    #     except:
    #         time.sleep(10)
    
    for n in range(1):

        try:
            WebDriverWait(driver[tid], 30).until(EC.presence_of_all_elements_located)
            #time.sleep(10)
            
        except:
            pass

        if "楽天会員ログイン" in driver[tid].page_source:
            driver[tid].find_element_by_id('loginInner_u').clear()
            driver[tid].find_element_by_id('loginInner_p').clear()
            driver[tid].find_element_by_id('loginInner_u').send_keys('kentookumura6@gmail.com')
            driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
            try:
                driver[tid].find_element_by_class_name('loginButton').click()
            except:
                time.sleep(10)        
        
        #if (driver[tid].current_url == recaptcha_page and not('アクセスが集中している為' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
        if (driver[tid].current_url == recaptcha_page and ('不正な申込みを防ぐため、認証を行います。チェックを入れて、次へボタンを押してください' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
            loopflg[idx] = False
            break
        #     #pass
        #     break
        
        if purchase_page is None:
            try:
                driver[tid].get(ticket_page)
            except:
                continue
            driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #actions = ActionChains(driver[tid])
            #actions.move_to_element(driver[tid].find_element_by_xpath(purchase_button))
            #actions.

            try:
                page1 = driver[tid].find_element_by_xpath(purchase_button).get_attribute('href').split('/agreement')[0]
                purchase_page = driver[tid].find_element_by_xpath(purchase_button).get_attribute('href')
            except:
                continue
            page2 = driver[tid].find_element_by_xpath(purchase_button).get_attribute('href').split('/agreement')[1]
            try:
                driver[tid].find_element_by_xpath(purchase_button).click()
            except:
                continue
            recaptcha_page = page1 + page2 + '/recaptcha'

        else:
            #スーパーリロード
            driver[tid].execute_script('location.reload(true);')
            print('super reload')

    purchase_page = None

        
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

def is_bad_proxy(proxy):
    PermissionTime = 10

    temp_options = webdriver.ChromeOptions()
    if(do_proxy):
        temp_options.add_argument('--proxy-server=http://%s' % proxy)
    driver = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe',options=temp_options)
    try:
        print(proxy)
        # webサイトへのタイムアウト時間を設定。もしこの時間内にアクセスできないならexceptに入る
        driver.set_page_load_timeout(PermissionTime)
        # アクセスして閉じる
        #driver.get(ticket_page)
        driver.get('https://rt.tstar.jp/orderreview/mypage')
        if not "楽天会員ログイン" in driver.page_source:
            print('bad proxy')
            driver.close()
            return False
        driver.close()
    except:
        driver.close()
        print("タイムアウト")
        return False

    return True

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

    global loopflg, proxy, fifo, cookie_fifo, cookie_file
    
    loopflg[idx] = True
    
    while(loopflg[idx]):
        do_exec(idx, tid)
        if not loopflg[idx]:
            break
        #ブラウザ終了
        driver[tid].close()
        #proxy返却
        if(do_proxy):
            fifo.put(proxy[idx])
        #cookie返却
        cookie_fifo.put(cookie_file[idx])
        #ブラウザ立ち上げ、IP再設定
        start_browser(idx, tid)
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
        
def run(idx, start_tiem):
    
    tid = threading.get_ident()
    #ブラウザ立ち上げ
    start_browser(idx, tid)
    #クッキー初期化
    init(idx, tid)
    #チケットページアクセス
    while True:
        driver[tid].get(ticket_page)
        if "公演名" in driver[tid].page_source:
            break
    #購入ボタンクリック
    scheduler = sched.scheduler(time.time, time.sleep)
    run_at    = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(seconds = 0.02)*idx #6 digit
    run_at    = int(time.mktime(run_at.utctimetuple()))
    scheduler.enterabs(run_at, 1, load, (idx, tid,))
    scheduler.run()
    
    
if __name__ == "__main__":

    #global fifo

    if(do_proxy):
        for i in proxys:
            if is_bad_proxy(i):
                fifo.put(i)
                print(fifo.qsize())
    
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
