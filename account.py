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
        self.jd = JD()
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
            if page.is_page(self.jd.login_page):
                need_login = True
            else:
                print_('please check the page.')
        if need_login:
            print_('start login...')
            self.login()
            self.get(page)

    def login(self):
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

    def quit(self):
        self.jd.quit()

    def get_orders(self):
        self.get(self.jd.list_page)
        orders = self.jd.list_page.my_order()
        print_('total %d orders.' % len(orders))
        import pprint
        pprint.pprint(orders[0])

    def data_sign(self):
        self.get(self.jd.data_page)
        self.jd.data_page.sign()


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
    a.coupon.list_coupons()
    #a.data_sign()
    #a.quit()