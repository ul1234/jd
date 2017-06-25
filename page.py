#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

def print_(str):
    print str

def chinese(word):
    return word.decode('utf-8')


class PageDriver:
    def __init__(self):
        self.cookie_loaded = False
        self.cookie_file = 'cookies.dat'

    def title(self, page_html = None):
        html = self.page_source() if page_html is None else page_html
        r = re.search(r'<title>([^<]+)<', html)
        if r:
            return r.group(1)
        else:
            return None

    def save_cookie(self):
        pickle.dump(self.get_cookies(), open(self.cookie_file, 'wb'))
        print_('cookie saved.')
        self.cookie_loaded = True

    def install_preload_cookie(self, preload_cookie_func):
        self.preload_cookie = preload_cookie_func

    def load_cookie(self):
        if hasattr(self, 'preload_cookie'): self.preload_cookie()
        if os.path.isfile(self.cookie_file):
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            self.add_cookies(cookies)
            self.cookie_loaded = True
            print_('cookie loaded.')
            return True
        return False

    def cookie_exist(self):
        return os.path.isfile(self.cookie_file)

    def invalidate_cookie(self):
        self.cookie_loaded = False
        if self.cookie_exist():
            os.remove(self.cookie_file)
            print_('cookie deleted.')

    def should_load_cookie(self):
        return self.cookie_exist() and not self.cookie_loaded

class RequestsDriver(PageDriver):
    def __init__(self):
        self.session = requests.Session()
        self.page_html = None
        self.cookies = {}
        PageDriver.__init__(self)

    def page_source(self):
        return self.page_html

    def get(self, url):
        r = self.session.get(url, cookies = self.cookies, verify = False)
        print_('get url [%s] status %d' % (url, r.status_code))
        self.page_html = r.text
        print_('title: %s' % self.title())


    def wait(self, timeout, condition_func):
        #if not condition_func(): raise Exception('wait timeout')
        return True if condition_func() else False
        #for i in xrange(timeout):
        #    if condition_func():
        #        return True
        #    time.sleep(1)
        #return False

    def add_cookies(self, cookies):
        self.cookies = {}
        for cookie in cookies:
            self.cookies[cookie['name']] = cookie['value']

class SeleniumDriver(PageDriver):
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        #self.driver = webdriver.Chrome()
        print_('selenium driver open browser.')
        PageDriver.__init__(self)

    def page_source(self):
        return self.driver.page_source

    def get(self, url):
        self.driver.get(url)
        print_('title: %s' % self.title())

    def wait(self, timeout, condition_func):
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: condition_func())
            return True
        except TimeoutException as e:
            print_(e)
            return False

    def get_cookies(self):
        return self.driver.get_cookies()

    def add_cookies(self, cookies):
        for cookie in cookies:
            #self.driver.add_cookie(cookie)
            self.driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry') if k in cookie})
    
    def close(self):
        self.driver.quit()

class PageNotloaded(Exception):
    pass

class CookieNotExist(Exception):
    pass

class Page:
    driver = None
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.save_html = True
        self.save_screen = False
        if hasattr(self, 'init_element'):
            self.init_element()

    @staticmethod
    def default_driver(web_driver):
        Page.driver = web_driver

    def install_driver(self, page_driver):
        self.driver = page_driver
        if hasattr(page_driver, 'driver'):
            self.webdriver = page_driver.driver

    def load(self, check_cookie = True):
        print_('loading %s: %s' % (self.name, self.url))
        if check_cookie:
            if not self.driver.cookie_exist(): raise CookieNotExist('cookie not found!')
            if self.driver.should_load_cookie(): self.driver.load_cookie()
        self.driver.get(self.url)
        self.wait_loaded()
        if not self.check_enter(): raise PageNotloaded('page not loaded!')
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title()))
        self.save('after_load')
        
    def pre_load(self):
        print_('preloading %s: %s' % (self.name, self.url))
        self.driver.get(self.url)
        
    def check_load(self):
        if not self.check_enter(): return False
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title()))
        self.save('jump_load')
        return True

    def check_page(self, pages):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            if page.check_enter(self.driver.page_source()):
                return page.name
        return ''

    def check_enter(self, page_html = None):
        return self.driver.title(page_html).find(self.title_identity) >= 0

    def wait_loaded(self, timeout = 10):
        #WebDriverWait(self.driver, timeout).until(lambda driver: self.check_enter())
        self.driver.wait(timeout, self.check_enter)
        
    def check_exit(self, page_html = None):
        return not self.check_enter(page_html)
        
    def wait_exit(self, timeout = 10):
        #WebDriverWait(self.driver, timeout).until(lambda driver: self.check_exit())
        self.driver.wait(timeout, self.check_exit)
        print_('exit %s page! enter page: %s' % (self.name, self.driver.title()))

    def submit(self):
        print_('submitting %s page: %s' % (self.name, self.url))
        self.webdriver.find_element(*self.submit_element).click()
        self.wait_exit()
        self.save('after_submit')

    def enable_save(self, html, screen):
        self.save_html = html
        self.save_screen = screen

    def save(self, info, html = None):
        if self.save_html:
            html = html if html is not None else self.driver.page_source()
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            r = re.search(r'<meta[^>]+charset="?(.*?)"', html)
            charset = 'utf-8' if not r else r.group(1)
            charset_str = '%s (%s)' % (charset, 'detected' if r else 'not detected')
            f = '%d_%s_%s.html' % (self.save_cnt, self.name, info)
            open(f, 'w').write(html.encode(charset, 'ignore'))
            print_('%s [%s] saved.' % (f, charset_str))
        if self.save_screen:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            f = '%d_%s_%s.png' % (self.save_cnt, self.name, info)
            self.webdriver.save_screenshot(f)
            print_('%s saved.' % f)
            
    def fill_elements(self, elements):
        for element, value in elements.items():
            elem = self.webdriver.find_element(*element)
            elem.clear()
            elem.send_keys(value)

class LoginPage(Page):
    def __init__(self):
        Page.__init__(self, 'login', r'https://passport.jd.com/new/login.aspx')
        #self.enable_save(True, True)

    def init_element(self):
        self.switch_login_element = (By.XPATH, "//div[@class='login-tab login-tab-r']/a")
        self.submit_element = (By.ID, 'loginsubmit')
        self.user_element = (By.ID, 'loginname')
        self.pwd_element = (By.ID, 'nloginpwd')
        self.title_identity = chinese('登录')

    def post_load(self):
        self.webdriver.find_element(*self.switch_login_element).click()
        
    def fill(self, user, pwd):
        self.fill_elements({self.user_element: user, self.pwd_element: pwd})
        #raise Exception('after fill') # for test
                

class ActiPage(Page):
    def __init__(self):
        Page.__init__(self, 'activate', '')

    def init_element(self):
        self.submit_element = (By.ID, 'submitBtn')
        self.code_element = (By.ID, 'code')
        self.title_identity = chinese('激活')

    def fill(self):
        self.driver.wait(10, lambda: EC.presence_of_element_located(self.code_element)(self.webdriver))
        code = raw_input('Please input the auth code:')
        self.fill_elements({self.code_element: code})


class MainPage(Page):
    def __init__(self):
        Page.__init__(self, 'main', 'http://www.jd.com')

    def init_element(self):
        self.title_identity = chinese('正品低价')
        
        
class ListPage(Page):
    def __init__(self):
        Page.__init__(self, 'list', r'http://order.jd.com/center/list.action')

    def init_element(self):
        self.title_identity = chinese('订单')


class JD:
    login_page = LoginPage()
    activ_page = ActiPage()
    list_page = ListPage()
    main_page = MainPage()

    @staticmethod
    def install_driver(pages, driver):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            page.install_driver(driver)

    @staticmethod
    def install_selenium_driver():
        JD.selenium_driver = SeleniumDriver()
        JD.selenium_driver.install_preload_cookie(lambda: JD.main_page.pre_load())
        JD.install_driver([JD.login_page, JD.activ_page, JD.main_page], JD.selenium_driver) 

    @staticmethod
    def install_requests_driver():
        JD.requests_driver = RequestsDriver()
        Page.default_driver(JD.requests_driver)

    @staticmethod
    def pre_login():
        if not hasattr(JD, 'selenium_driver'): JD.install_selenium_driver()
        self.selenium_driver.invalidate_cookie()
        self.requests_driver.invalidate_cookie()

    @staticmethod 
    def quit():
        if hasattr(JD, 'selenium_driver'): JD.selenium_driver.close()


class Account:
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        JD.install_requests_driver()    

    def get(self, page):
        need_login = False
        try:
            page.load()
        except CookieNotExist as e:
            print_(e)
            need_login = True
        except PageNotloaded:
            print_('page [%s] not load.' % page.name)
            if page.check_page(JD.login_page) == JD.login_page.name:
                need_login = True
            else:
                print_('please check the page.')
        if need_login:
            print_('start login...')
            self.login()
            self.get(page)

    def login(self):
        JD.pre_login()

        JD.login_page.load(check_cookie = False)
        JD.login_page.fill(self.user, self.pwd)
        JD.login_page.submit()
        
        if JD.activ_page.check_load():
            JD.activ_page.fill()
            JD.activ_page.submit()
        if JD.main_page.check_load():
            print_('login in successfully.')            
        JD.main_page.driver.save_cookie()

    def quit(self):
        JD.quit()


if __name__ == '__main__':
    try:
        user, passwd = open('user.dat').read().strip().split(':')
    except Exception as e:
        user, passwd = '#', '#'
        print(e)
    print user
    #print passwd
    a = Account(user, passwd)
    a.get(JD.list_page)
    a.quit()
