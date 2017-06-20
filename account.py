#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Page:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

class JD:
    login = Page('login', r'https://passport.jd.com/new/login.aspx')
    main = Page('main', r'')

    def __init__(self):
        pass

class Debug:
    save_html = False
    save_screen = False
    debug_log = False
    NONE = 0
    ALL = 1

    @staticmethod
    def debug_level(level):
        if level == Debug.ALL:
            Debug.enable_save_html()
            Debug.enable_save_screen()
            Debug.enable_debug_log()

    @staticmethod
    def enable_save_html():
        Debug.save_html = True

    @staticmethod
    def enable_save_screen():
        Debug.save_screen = True

    @staticmethod
    def enable_debug_log():
        Debug.debug_log = True


class Account:
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        print 'before'
        self.driver = webdriver.PhantomJS()
        print 'after'

    def get(self, page):
        self.driver.get(page.addr)
        self.save_screen(page)
        self.save_html(page)

    def login(self):
        self.get(JD.login)
        self.driver.find_element_by_xpath("//div[@class='login-tab login-tab-r']/a").click()
        self.save_screen(JD.login)
        self.fill_element('loginname', self.user)
        self.fill_element('nloginpwd', self.pwd)
        self.driver.find_element_by_id('loginsubmit').click()
        self.save_screen(JD.login)
        print '1: ', self.driver.title
        time.sleep(5)
        self.save_screen(JD.login)
        print '2: ', self.driver.title
        WebDriverWait(self.driver, 5).until_not(EC.title_contains('登录'.decode('utf-8')))
        self.save_screen(JD.login)
        print '3: ', self.driver.title
        self.save_html(JD.main)

    def fill_element(self, element_name, value):
        elem = self.driver.find_element_by_name(element_name)
        elem.clear()
        elem.send_keys(value)

    def print_(self, str):
        print str
        
    def save_screen(self, page):
        if Debug.save_screen:
            if not hasattr(self, 'save_screen_cnt'): self.save_screen_cnt = 0
            self.save_screen_cnt += 1
            f = '%d_%s.png' % (self.save_screen_cnt, page.name)
            self.driver.save_screenshot(f)
            self.print_('%s saved.' % f)
            
    def save_html(self, page):
        if Debug.save_html:
            if not hasattr(self, 'save_html_cnt'): self.save_html_cnt = 0
            self.save_html_cnt += 1
            f = '%d_%s.html' % (self.save_html_cnt, page.name)
            open(f, 'w').write(self.driver.page_source.encode('utf-8'))
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
    Debug.debug_level(Debug.ALL)
    #print passwd
    a = Account(user, passwd)
    a.login()
    a.close()
