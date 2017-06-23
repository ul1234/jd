#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def print_(str):
    print str

def chinese(word):
    return word.decode('utf-8')
    
class PageNotloaded(Exception):
    pass

class Page:
    driver = None
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.save_html = True
        self.save_screen = False
        if hasattr(self, 'init_element'):
            self.init_element()

    @staticmethod
    def init_driver(web_driver):
        Page.driver = web_driver

    def load(self):
        print_('loading %s: %s' % (self.name, self.addr))
        self.driver.get(self.addr)
        self.wait_loaded()
        if not self.check_enter(): raise PageNotloaded('page not loaded')
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title))
        self.save('after_load')
        
    def pre_load(self):
        print_('preloading %s: %s' % (self.name, self.addr))
        self.driver.get(self.addr)
        
    def check_load(self):
        if not self.check_enter(): return False
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title))
        self.save('jump_load')
        return True

    def check_enter(self):
        return EC.title_contains(self.title_identity)(self.driver)

    def wait_loaded(self, timeout = 10):
        WebDriverWait(self.driver, timeout).until(lambda driver: self.check_enter())
        
    def check_exit(self):
        return not EC.title_contains(self.title_identity)(self.driver)
        
    def wait_exit(self, timeout = 10):
        WebDriverWait(self.driver, timeout).until(lambda driver: self.check_exit())
        print_('exit %s page! enter page: %s' % (self.name, self.driver.title))

    def submit(self):
        print_('submitting %s page: %s' % (self.name, self.addr))
        self.driver.find_element(*self.submit_element).click()
        self.wait_exit()
        self.save('after_submit')

    def enable_save(self, html, screen):
        self.save_html = html
        self.save_screen = screen

    def save(self, info):
        if self.save_html:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            r = re.search(r'<meta[^>]+charset="?(.*?)"', self.driver.page_source)
            if r:
                print r.group(0)
                print r.group(1)
            charset = 'utf-8' if not r else r.group(1)
            charset_str = '%s (%s)' % (charset, 'detected' if r else 'not detected')
            f = '%d_%s_%s.html' % (self.save_cnt, self.name, info)
            open(f, 'w').write(self.driver.page_source.encode(charset, 'ignore'))
            print_('%s [%s] saved.' % (f, charset_str))
        if self.save_screen:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            f = '%d_%s_%s.png' % (self.save_cnt, self.name, info)
            self.driver.save_screenshot(f)
            print_('%s saved.' % f)
            
    def fill_elements(self, elements):
        for element, value in elements.items():
            elem = self.driver.find_element(*element)
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
        self.driver.find_element(*self.switch_login_element).click()
        
    def fill(self, user, pwd):
        self.fill_elements({self.user_element: user, self.pwd_element: pwd})
                

class ActiPage(Page):
    def __init__(self):
        Page.__init__(self, 'activate', '')

    def init_element(self):
        self.submit_element = (By.ID, 'submitBtn')
        self.code_element = (By.ID, 'code')
        self.title_identity = chinese('激活')

    def fill(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.code_element))
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
    login = LoginPage()
    activ = ActiPage()
    list = ListPage()
    main = MainPage()

    def __init__(self):
        pass


class Account:
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        #self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        print_('open browser.')
        Page.init_driver(self.driver)
        self.cookie_file = 'cookies.dat'

    def save_cookie(self):
        pickle.dump(self.driver.get_cookies() , open(self.cookie_file, 'wb'))
        print_('cookie saved.')

    def load_cookie(self):
        if os.path.isfile(self.cookie_file):
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            for cookie in cookies:
                #self.driver.add_cookie(cookie)
                self.driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry') if k in cookie})
            print_('cookie loaded.')
            return True
        return False

    def cookie_exist(self):
        return os.path.isfile(self.cookie_file)

    def get(self, page):
        need_login = False
        if self.cookie_exist():
            JD.main.pre_load()
            self.load_cookie()
            try:
                page.load()
            except PageNotloaded:
                if JD.login.check_load():
                    need_login = True
        else:
            need_login = True
        if need_login:
            raise 'login'
            self.login()
            page.load()

    def login(self):
        JD.login.load()
        JD.login.fill(self.user, self.pwd)
        JD.login.submit()
        
        if JD.activ.check_load():
            JD.activ.fill()
            JD.activ.submit()
        if JD.main.check_load():
            print_('login in successfully.')            
        self.save_cookie()

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    try:
        user, passwd = open('user.dat').read().strip().split(':')
    except Exception as e:
        user, passwd = '#', '#'
        print(e)
    print user
    #print passwd
    a = Account(user, passwd)
    a.get(JD.list)
    a.close()
