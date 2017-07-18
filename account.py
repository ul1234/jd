#!/usr/bin/python
# -*- coding: utf-8 -*-

from page import JD, PageNotloaded, CookieNotExist
from coupon import Coupon
from miscellaneous import *

class Account:
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        self.jd = JD(user)
        self.coupon = Coupon(self)
        clear_save()

    def get(self, page):
        need_login = False
        try:
            page.load()
        except CookieNotExist as e:
            print_(e)
            need_login = True
        except PageNotloaded:
            print_('page [%s] not load.' % page.name)
            if self.jd.is_login_page(page):
                need_login = True
            else:
                print_('please check the page.')
        if need_login:
            print_('start login...')
            self.m_login() if page.is_mobile else self.login()
            self.get(page)

    def _check_login_times(self, is_mobile = False):
        MAX_LOGIN_TIMES = 2
        login_times = 'm_login_times' if is_mobile else 'login_times'
        if not hasattr(self, login_times): setattr(self, login_times, 0)
        t = getattr(self, login_times)
        setattr(self, login_times, t+1)
        if t >= MAX_LOGIN_TIMES: raise Exception('cannot login in %d times.' % t)

    def login(self):
        self._check_login_times()
        self.jd.pre_login()

        self.jd.login_page.load(check_cookie = False)
        self.jd.login_page.fill(self.user, self.pwd)
        self.jd.login_page.submit()

        if self.jd.activ_page.check_load():
            self.jd.activ_page.fill()
            self.jd.activ_page.submit()
        if self.jd.main_page.check_load():
            print_('login in successfully.')
        self.jd.main_page.driver.save_cookie()

    def m_login(self):
        self._check_login_times(is_mobile = True)
        self.jd.pre_login()

        self.jd.m_login_page.load(check_cookie = False)
        self.jd.m_login_page.fill(self.user, self.pwd)
        self.jd.m_login_page.submit()

        if self.jd.m_main_page.check_load():
            print_('login in successfully.')
        self.jd.m_main_page.driver.save_cookie()

    def quit(self):
        #self.jd.quit()
        pass

    def get_orders(self):
        self.get(self.jd.list_page)
        orders = self.jd.list_page.my_order()
        print_('total %d orders.' % len(orders))
        import pprint
        pprint.pprint(orders[0])

    def data_sign(self):
        self.get(self.jd.data_page)
        self.jd.data_page.sign()

    def m_data_sign(self):
        self.get(self.jd.m_data_page)
        self.jd.m_data_page.sign()
        
    def m_charge_coupon(self):
        self.get(self.jd.m_charge_page)
        coupon_urls = self.jd.m_charge_page.get_coupon_page_urls()
        for i in [4, 2, 1, 0]:
            self.jd.m_get_coupon_page.get_coupon(url = coupon_urls[i])

if __name__ == '__main__':
    try:
        user, passwd = open('user.dat').read().strip().split(':')
    except Exception as e:
        user, passwd = '#', '#'
        print(e)
    print user
    #raise '1'
    #print passwd
    
    a = Account(user, passwd)
    try:
        #a.coupon.list_coupons()
        #a.coupon.get_server_time()
        #a.data_sign()
        #a.quit()
        a.m_data_sign()
    finally:
        a.quit()
