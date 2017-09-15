#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, re
from website import Page, Website
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from miscellaneous import *
from account import Account

class LoginPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'login', r'https://passport.suning.com/ids/login')
        #self.enable_save(True, True)

    def init_element(self):
        self.switch_login_element = (By.XPATH, "//div[@class='login-tab']/a[2]")
        self.submit_element = (By.ID, 'submit')
        self.user_element = (By.ID, 'userName')
        self.pwd_element = (By.ID, 'password')
        self.title_identity = chinese('用户登录')

    def post_load(self):
        self.webdriver.find_element(*self.switch_login_element).click()

    def fill(self, user, pwd):
        self.fill_elements({self.user_element: user, self.pwd_element: pwd})
        #raise Exception('after fill') # for test

class MainPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'main', 'https://www.suning.com')

    def init_element(self):
        self.title_identity = chinese('苏宁易购')

class ListPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'list', r'https://order.suning.com/onlineOrder/orderList.do')

    def init_element(self):
        self.title_identity = chinese('订单')


class SuNing(Website):
    def __init__(self, user):
        Website.__init__(self, 'SuNing', user)
        self.login_page = LoginPage(self)
        self.main_page = MainPage(self)
        self.list_page = ListPage(self)

    def is_login_page(self, page):
        return page.is_page(self.login_page)

class SuningAccount(Account):
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        Account.__init__(self, SuNing, user, pwd, rk_user, rk_pwd)

    def get_orders(self):
        self.get(self.website.list_page)
        
    def get_coupon(self, url, driver_key = 'selenium'):
        if driver_key == 'requests':
            html = self.website.requests_page.get_html(url, log_name = 'coupon')
            # href="//quan.suning.com/.........."
            pattern = 'href="//(quan.suning.com/.*?)"'
            r = re.findall(pattern, html)
        else:
            self.website.page.get_html(url, log_name = 'coupon')
            quan_element = (By.XPATH, "//map[@name='quan']/area[1]")
            self.website.page.find_element(*quan_element).click()

if __name__ == '__main__':
    try:
        user, passwd = open('user2.dat').read().strip().split(':')
    except Exception as e:
        user, passwd = '#', '#'
        print(e)
    print user
    #raise '1'
    #print passwd
    
    a = SuningAccount(user, passwd)
    try:
        #a.coupon.list_coupons()
        #a.coupon.get_server_time()
        #a.data_sign()
        #a.quit()
        #a.login()
        #a.get_orders()
        a.login()
        a.get_coupon('https://cuxiao.suning.com/c0912phone.html')
    finally:
        #time.sleep(10)
        a.quit()

