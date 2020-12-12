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
import threading
import re
import pickle
from queue import Queue
import os
import configparser
import base64


# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
# --------------------------------------------------
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

# --------------------------------------------------
# config.iniから値取得
# --------------------------------------------------
nbrowser         = int(config_ini['DEFAULT']['nbrowser'])
start_time       = config_ini['DEFAULT']['start_time']
ticket_page      = config_ini['DEFAULT']['ticket_page']
performance_date = config_ini['DEFAULT']['performance_date']
userID           = config_ini['DEFAULT']['userID']
password         = config_ini['DEFAULT']['password']

# --------------------------------------------------
# 初期化処理
# --------------------------------------------------
th_objs    = [] #スレッドの配列
driver     = {} #各スレッドのwebdriverオブジェクト格納用
recaptchas = []
break_cap  = 0
recaptcha_page = None
purchase_page  = None
loopflg     = [None]*nbrowser
cookie      = [None]*nbrowser
cookie_file = [None]*nbrowser

options = webdriver.ChromeOptions()

cookie_fifo = Queue()
for x in os.listdir('.\\cookie\\'):
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
else:
    browsers = [
        { "size-x": "1280", "size-y": "720", "pos-x": "0",   "pos-y": "0"}
    ]

options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')


def start_browser(idx, tid):
    
    browser     = browsers[idx]
    driver[tid] = webdriver.Chrome(executable_path='c:\\Users\\kento\\driver\\chromedriver.exe',options=options)

    #位置とサイズ指定
    driver[tid].set_window_size(browser['size-x'], browser['size-y'])
    driver[tid].set_window_position(browser['pos-x'], browser['pos-y'])

    
def init(idx, tid):

    global cookie, cookie_fifo, cookie_file

    cookie_file[idx] = cookie_fifo.get()
    cookie[idx]      = pickle.load(open('cookie\\{}'.format(cookie_file[idx]), "rb"))
    print(cookie_file[idx])

    #driver[tid].get('http://www.google.com')
    content = requests.get('http://www.google.com').content

    data_encode_bytes = base64.b64encode(content)
    data_encode_str = data_encode_bytes.decode('utf-8')
    #print(data_encode_str)
    #driver[tid].get("data:text/html;charset=utf-8," + str(content, 'utf-8'))
    #driver[tid].get("data:text/html;charset=utf-8:base64," + str(data_encode_str))
    
    
    #data_bytes = bytes(content)
    # data_encode_bytes = base64.b64encode(content)
    # data_encode_str = data_encode_bytes.decode('utf-8')
    # print(data_encode_str)
    driver[tid].execute_script("""
    document.location = 'about:blank';
    document.open();
    document.write(arguments[0]);
    document.close();
    """, "PGh0bWw+PGhlYWQ+PG1ldGEgY2hhcnNldD0iVVRGLTgiPjx0aXRsZT7jgr/jgqTjg4jjg6s8L3RpdGxlPjxzY3JpcHQgc3JjPSJodHRwOi8vYWpheC5nb29nbGVhcGlzLmNvbS9hamF4L2xpYnMvanF1ZXJ5LzIuMS4zL2pxdWVyeS5taW4uanMiPjwvc2NyaXB0PjxzdHlsZT5kaXYgeyBib3JkZXItYm90dG9tOnNvbGlkOyB3aWR0aDo2MDBweDsgfWltZyB7IHdpZHRoOjUwcHg7IGhlaWdodDo1MHB4O31saSB7IGZsb2F0OmxlZnQ7IGxpc3Qtc3R5bGU6bm9uZTsgd2lkdGg6NTAwcHg7IGhlaWdodDogNjBweDsgfS5jbGVhciB7IGNsZWFyOmJvdGg7IH08L3N0eWxlPjwvaGVhZD48Ym9keT48ZGl2IGNsYXNzPSJjbGVhciI+44Kz44Oz44OG44Oz44OE6Kqt44G/6L6844G/PC9kaXY+PHVsPjxsaSBjbGFzcz0iY2xlYXIiPuebuOWvviA9PjwvbGk+PGxpPjxpbWcgc3JjPSIuL3JlbGF0aXZlLnBuZyI+PC9saT48bGkgY2xhc3M9ImNsZWFyIj7jg5vjgrnjg4jnm7jlr74gPT48L2xpPjxsaT48aW1nIHNyYz0iL2Fic29sdXRlLnBuZyI+PC9saT48bGkgY2xhc3M9ImNsZWFyIj7ntbblr74oaHR0cDrjgYLjgoopID0+PC9saT48bGk+PGltZyBzcmM9Imh0dHA6Ly9jZG4ucWlpdGEuY29tL2Fzc2V0cy9zaXRlaWQtcmV2ZXJzZS05YjM4ZTI5N2JiZDAyMDM4MGZlZWQ5OWI0NDRjNjIwMi5wbmciPjwvbGk+PGxpIGNsYXNzPSJjbGVhciI+57W25a++KGh0dHA644Gq44GXKSA9PjwvbGk+PGxpPjxpbWcgc3JjPSIvL2Nkbi5xaWl0YS5jb20vYXNzZXRzL3NpdGVpZC1yZXZlcnNlLTliMzhlMjk3YmJkMDIwMzgwZmVlZDk5YjQ0NGM2MjAyLnBuZyI+PC9saT48L3VsPjxkaXYgY2xhc3M9ImNsZWFyIj5KYXZhU2NyaXB0PC9kaXY+PHVsPjxsaSBjbGFzcz0iY2xlYXIiPkNvb2tpZSh3aW5kb3cuZG9jdW1lbnQud3JpdGUod2luZG93LmRvY3VtZW50LmNvb2tpZSkpID0+PC9saT48bGk+PHNjcmlwdD53aW5kb3cuZG9jdW1lbnQud3JpdGUod2luZG93LmRvY3VtZW50LmNvb2tpZSk8L3NjcmlwdD48L2xpPjxsaSBjbGFzcz0iY2xlYXIiPuODreODvOOCq+ODq+OCueODiOODrOODvOOCuCh3aW5kb3cuZG9jdW1lbnQud3JpdGUod2luZG93LmxvY2FsU3RvcmFnZSkpID0+PC9saT48bGk+PHNjcmlwdD53aW5kb3cuZG9jdW1lbnQud3JpdGUod2luZG93LmxvY2FsU3RvcmFnZSk8L3NjcmlwdD48L2xpPjxsaSBjbGFzcz0iY2xlYXIiPuOCu+ODg+OCt+ODp+ODs+OCueODiOODrOODvOOCuCh3aW5kb3cuZG9jdW1lbnQud3JpdGUod2luZG93LnNlc3Npb25TdG9yYWdlKSkgPT48L2xpPjxsaT48c2NyaXB0PndpbmRvdy5kb2N1bWVudC53cml0ZSh3aW5kb3cuc2Vzc2lvblN0b3JhZ2UpPC9zY3JpcHQ+PC9saT48bGkgY2xhc3M9ImNsZWFyIj5BamF4ID0+PC9saT48bGk+PHNjcmlwdD4kLmdldEpTT04oJ2h0dHA6Ly9leHByZXNzLmhlYXJ0cmFpbHMuY29tL2FwaS9qc29uP21ldGhvZD1nZXRTdGF0aW9ucyZsaW5lPUpSJUU1JUIxJUIxJUU2JTg5JThCJUU3JUI3JTlBJywge30sIGZ1bmN0aW9uKGpzb24pIHsgd2luZG93LmRvY3VtZW50LndyaXRlKGpzb24ucmVzcG9uc2Uuc3RhdGlvblswXS5uYW1lKTsgfSk8L3NjcmlwdD48L2xpPjxsaSBjbGFzcz0iY2xlYXIiPuOBoOOBn+OBruabuOi+vOOBvyh3aW5kb3cuZG9jdW1lbnQud3JpdGUoJ0phdmFTY3JpcHQgT0snKSkgPT48L2xpPjxsaT48c2NyaXB0PndpbmRvdy5kb2N1bWVudC53cml0ZSgnSmF2YVNjcmlwdCBPSycpPC9zY3JpcHQ+PC9saT48L3VsPjwvYm9keT48L2h0bWw+")
    for i in cookie[idx]:
        driver[tid].add_cookie(i)

        
def do_exec(idx, tid):
    
    global recaptcha_page, purchase_page, loopflg
    
    if purchase_page is not None:
        driver[tid].get(purchase_page)
        
    else:
        while True:
            try:
                driver[tid].get(ticket_page)
            except:
                continue
            driver[tid].execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #actions = ActionChains(driver[tid])
            #actions.move_to_element(driver[tid].find_element_by_xpath(performance_date))
            #actions.

            try:
                page1 = driver[tid].find_element_by_xpath(performance_date).get_attribute('href').split('/agreement')[0]
                purchase_page = driver[tid].find_element_by_xpath(performance_date).get_attribute('href')
            except:
                continue
            page2 = driver[tid].find_element_by_xpath(performance_date).get_attribute('href').split('/agreement')[1]
            try:
                driver[tid].find_element_by_xpath(performance_date).click()
            except:
                continue
            recaptcha_page = page1 + page2 + '/recaptcha'
            break

    WebDriverWait(driver[tid], 30).until(EC.presence_of_all_elements_located)

    if "楽天会員ログイン" in driver[tid].page_source:
        driver[tid].find_element_by_id('loginInner_u').clear()
        driver[tid].find_element_by_id('loginInner_p').clear()
        driver[tid].find_element_by_id('loginInner_u').send_keys(userID)
        driver[tid].find_element_by_id('loginInner_p').send_keys(password)        
        # driver[tid].find_element_by_id('loginInner_u').send_keys('kentookumura6@gmail.com')
        # driver[tid].find_element_by_id('loginInner_p').send_keys('kento5735')
        try:
            driver[tid].find_element_by_class_name('loginButton').click()
        except:
            time.sleep(10)        
        
    if (driver[tid].current_url == recaptcha_page and ('不正な申込みを防ぐため、認証を行います。チェックを入れて、次へボタンを押してください' in driver[tid].page_source)) or "開催日" in driver[tid].page_source:
        loopflg[idx] = False

        
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

    global loopflg, cookie_fifo, cookie_file, cookie
    
    loopflg[idx] = True
    
    while(loopflg[idx]):
        do_exec(idx, tid)
        if not loopflg[idx]:
            break
        #クッキー消去
        driver[tid].delete_all_cookies()
        #cookie返却
        cookie_fifo.put(cookie_file[idx])
        #cookie読み込み
        cookie_file[idx] = cookie_fifo.get()
        cookie[idx]      = pickle.load(open('cookie\\{}'.format(cookie_file[idx]), "rb"))        
        print(cookie_file[idx])
        
        for i in cookie[idx]:
            driver[tid].add_cookie(i)

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
    driver[tid].get(ticket_page)
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
