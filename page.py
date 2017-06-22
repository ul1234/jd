#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Page:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        if hasattr(self, 'init_element'):
            self.init_element()
        
    def check_exist(self):
        pass
        
    def check_enter(self):
        pass
        
    def wait_loaded(self):
        pass
        
    def submit(self):
        pass

        
class LoginPage(Page):
    def __init__(self):
        self.name = 'login'
        self.addr = r'https://passport.jd.com/new/login.aspx'
        Page.__init__(self)
    
    def init_element(self):
        pass
        
    def fill_form(self, user, pwd):
        pass
        
class ActiPage(Page):
    def __init__(self):
        self.name = 'activate'
        self.addr = ''
        Page.__init__(self)
    
    def init_element(self):
        pass
        
    def fill_form(self):
        pass

        
class ListPage(Page):
    def __init__(self):
        self.name = 'list'
        self.addr = r'http://order.jd.com/center/list.action'
        Page.__init__(self)
    
    def init_element(self):
        pass
        
        
class JD:
    login = LoginPage()
    activ = ActiPage()
    list = Page()

    def __init__(self):
        pass


class Account:
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        print 'before'
        self.driver = webdriver.PhantomJS()
        #self.driver = webdriver.Chrome()
        print 'after'
        self.cookie_file = 'cookies.dat'
        self.current_page = ''
        self.login()

    def get(self, page):
        self.driver.get(page.addr)
        self.current_page = page
        self.save_screen()
        self.save_html()

    def save_cookie(self):
        pickle.dump(self.driver.get_cookies() , open(self.cookie_file, 'wb'))

    def load_cookie(self):
        if os.path.isfile(self.cookie_file):
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            for cookie in cookies:
                #self.driver.add_cookie(cookie)
                self.driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry') if k in cookie})
            return True
        return False

    def cookie_exist(self):
        return os.path.isfile(self.cookie_file)

    def get_list(self):
        self.get(JD.list)

    def login(self):
        if self.cookie_exist():
            self.get(JD.main)
            self.load_cookie()
        else:
            self.login_without_cookie()

    def login_without_cookie(self):
        self.get(JD.login)
        self.driver.find_element_by_xpath("//div[@class='login-tab login-tab-r']/a").click()
        self.save_screen()
        self.fill_element('loginname', self.user)
        self.fill_element('nloginpwd', self.pwd)
        self.driver.find_element_by_id('loginsubmit').click()
        self.save_screen()
        self.print_page_title()
        WebDriverWait(self.driver, 10).until_not(EC.title_contains(chinese('')))
        self.save_screen()
        self.print_page_title()
        if chinese('') in self.driver.title:
            WebDriverWait(self.driver, 10).until_not(EC.presence_of_element_located((By.ID, "code")))
            code = raw_input('Please input the auth code:')
            self.fill_element('code', code)
            self.driver.find_element_by_id('submitBtn').click()
            self.save_screen()
            WebDriverWait(self.driver, 10).until_not(EC.title_contains(chinese('')))
            self.print_page_title()
            self.save_screen()
            self.save_cookie()
        else:
            print 'no'
        self.save_html(JD.main)

    def fill_element(self, element_name, value):
        elem = self.driver.find_element_by_id(element_name)
        elem.clear()
        elem.send_keys(value)

    def print_(self, str):
        print str

    def print_page_title(self):
        if Debug.debug_log:
            self.print_(self.driver.title)

    def save_screen(self, page = ''):
        if Debug.save_screen:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            page = page or self.current_page
            f = '%d_%s.png' % (self.save_cnt, page.name)
            self.driver.save_screenshot(f)
            self.print_('%s saved.' % f)

    def save_html(self, page = ''):
        if Debug.save_html:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            page = page or self.current_page
            f = '%d_%s.html' % (self.save_cnt, page.name)
            open('test.html', 'w').write(self.driver.page_source.encode('utf-8'))
            r = re.search(r'charset="(.*?)"', self.driver.page_source)
            charset = 'utf-8' if not r else r.group(1)
            if r:
                print r.group(0)
                print r.group(1)
            print charset
            open(f, 'w').write(self.driver.page_source.encode(charset))
            self.print_('%s saved.' % f)

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
    Debug.debug_level(Debug.ALL)
    a.get_list()
    a.close()
