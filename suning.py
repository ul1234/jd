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
        
    def get_coupon(self, url, coupon_info = []):
        html = self.website.page.get_html(url, log_name = 'coupon')
        coupon_urls = re.findall('href="//(quan.suning.com/.*?activityId.*?)"', html)
        if not coupon_urls:
            print_('No coupon is found! quit...')
            return
        coupon_urls = map(unescape, coupon_urls)
        p_(coupon_urls)
        #pause()
        coupons = []
        for i, u in enumerate(coupon_urls):
            coupon_url = r'https://%s' % u
            html = self.website.requests_page.get_html(coupon_url, log_name = 'check_coupon_%d' % i)
            info = self._parse_coupon_info(html, i)
            if info: coupons.append((info, coupon_url))
        p_(coupons)
        #pause()
        if not coupon_info:
            get_coupons = coupons
        else:
            get_coupons = []
            for info in coupon_info:
                if isinstance(info, tuple):
                    discount, name = info
                else:
                    discount, name = info, ''
                match_coupons = [(i, c) for i, c in coupons if i.find('-%s' % discount) >= 0 and i.find(name) >= 0]
                if match_coupons:
                    if len(match_coupons) > 1:
                        print_('found %d coupons for %s, change or add both.' % (len(match_coupons), str(info)))
                    else:
                        print_('found coupon for %s.' % str(info))
                    get_coupons += match_coupons
        p_(get_coupons)
        for info, url in get_coupons:
            if info.find('Available') >= 0:
                self._get_coupon_now(url, info)
                break  # test???
            else:
                print_('skip getting coupon, not available: %s' % info)





    def get_coupon_1(self, url, coupon_index = [], driver_key = 'selenium'):
        page = self.website.requests_page if driver_key == 'requests' else self.website.page
        html = page.get_html(url, log_name = 'coupon')
        # href="//quan.suning.com/.........."
        quan = html_content(html, '<map name="\w*quan"', '</map>')
        r = re.findall('coords="(.*?)"\s*href="(.*?)"', quan)
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
            self.website.page.wait_element(quan_info_element)
            pause()
            quan_info = self.website.page.webdriver.find_element(*quan_info_element)
            pprint.pprint(quan_info.get_attribute('innerHTML'))
            info = self._parse_coupon_info(quan_info.get_attribute('innerHTML'), i)
            pause()
            self._get_coupon_now(info)
            pause()
            self.website.page.driver.switch_back()
            pause()
            ########## here ????????


    def _parse_coupon_info(self, html, index = 0):
        pattern = r'class="price".*?</span>(.*?)</div>.*?<em>\D*(\d+)\D.*?</em>.*?class="quan-body".*?</span>(.*?)</p>.*?</span>(.*?)</p>.*?</span>(.*?)</p>'
        r = re.search(pattern, html, flags = re.IGNORECASE|re.DOTALL)
        if r:
            discount_price, available_price, usage, time_range, get_coupon_time = [d.strip() for d in r.groups()]
            coupon = {'usage': usage, 'discount_price': discount_price, 'available_price': available_price,
                      'time_range': time_range, 'get_coupon_time': get_coupon_time}
            pattern = r'id="getCouponNow"\s*(style="display:none")?\s*>.*id="goToUse"\s*(style="display:none")?\s*>.*id="getMoreCouponDiv"\s*(style="display:none")?\s*>'
            stat = re.search(pattern, html, flags = re.IGNORECASE|re.DOTALL)
            if stat:
                quan_stat = stat.groups()
                coupon['stat'] = 'Available' if quan_stat[0] == None else ('Usable' if quan_stat[1] == None else 'SoldOut')
            else:
                print_('cannot detect the coupon state, please check')
            p_(r.groups())
            p_(coupon)
            info_str = '[%s] %s-%s, %s, %s' % (coupon['stat'], coupon['available_price'], coupon['discount_price'], coupon['usage'], coupon['get_coupon_time'])
            print_('found coupon! %s' % info_str)
            return info_str
        print_('no valid coupon found!')
        return ''
        

    def _get_coupon_now(self, url, info = ''):
        p_('URL: %s' % url)
        self.website.page.get_html(url, log_name = 'get_coupon')
        pause()
        quan_get_now = (By.ID, 'getCouponNow')
        quan_goto_use = (By.ID, 'goToUse')
        quan_get_more = (By.ID, 'getMoreCouponDiv')
        quan_get = self.website.page.webdriver.find_element(*quan_get_now)
        quan_use = self.website.page.webdriver.find_element(*quan_goto_use)
        quan_more = self.website.page.webdriver.find_element(*quan_get_more)

        if quan_get.is_displayed():
            quan_get.find_element(By.TAG_NAME, 'a').click()
            print_('get coupon successfully! %s' % info)
        elif quan_use.is_displayed():
            print_('you have got the coupon! please use it.')
        elif quan_more.is_displayed():
            print_('you are late, the coupon is sold out.')
        pause()


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
        a.get_coupon('https://cuxiao.suning.com/915djpjlzn.html')
    finally:
        #time.sleep(10)
        a.quit()

