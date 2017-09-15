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
        page = self.website.requests_page if driver_key == 'requests' else self.website.page
        html = page.get_html(url, log_name = 'coupon')
        # href="//quan.suning.com/.........."
        quan = html_content(html, '<map name="quan"', '</map>')
        r = re.findall('href="//(quan.suning.com/.*?)"', quan)
        if not r:
            print_('No coupon is found! quit...')
            return
        #quan_num = len(r)
        import pprint
        pprint.pprint(r)
        pause()
        quan_num = 1
        for i in range(quan_num):
            quan_element = (By.XPATH, "//map[@name='quan']/area[%d]" % (i+1))
            self.website.page.webdriver.find_element(*quan_element).click()
            self.website.page.driver.switch_to_newpage()
            quan_info_element = (By.CLASS_NAME, 'quan-c')
            print_('start wait...', output_time = True)
            self.website.page.wait_element(quan_info_element)
            print_('after wait...', output_time = True)
            pause()
            quan_info = self.website.page.webdriver.find_element(*quan_info_element)
            pprint.pprint(quan_info.get_attribute('innerHTML'))
            self._parge_coupon_info(quan_info.get_attribute('innerHTML'))
            pause()
            self.website.page.driver.switch_back()
            pause()
            ########## here ????????


    def _parge_coupon_info(self, html):
        pass

    def _get_coupon_now(self):
        quan_get_now = (By.ID, 'getCouponNow')
        quan_goto_use = (By.ID, 'goToUse')
        quan_get_more = (By.ID, 'getMoreCouponDiv')
        
        quan = self.website.page.webdriver.find_element(*quan_get_now)
        if quan.is_enabled():
            quan.find_element(By.XPATH, '//a[1]').click()
            print_('get coupon successfully!')


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

