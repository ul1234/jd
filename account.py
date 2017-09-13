#!/usr/bin/python
# -*- coding: utf-8 -*-

from website import PageNotloaded, CookieNotExist
from coupon import Coupon
from miscellaneous import *

class Account:
    def __init__(self, website, user, pwd, rk_user = '', rk_pwd = ''):
        self.user = user
        self.pwd = pwd
        self.rk_user = rk_user
        self.rk_pwd = rk_pwd
        self.website = website(user)
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
            if self.website.is_login_page(page):
                need_login = True
            else:
                print_('please check the page.')
        if need_login:
            print_('start login...')
            self.login()
            self.get(page)

    def check_login_times(self, max_login_times = 2):
        if not hasattr(self, 'login_times'): self.login_times = 0
        if self.login_times >= max_login_times: raise Exception('cannot login in %d times.' % self.login_times)
        self.login_times += 1

    def quit(self):
        self.website.quit()

    def login(self):
        self.check_login_times()
        self.website.pre_login()

        self.website.login_page.load(check_cookie = False)
        self.website.login_page.fill(self.user, self.pwd)
        self.website.login_page.submit()

        if hasattr(self, 'login_next_step'): self.login_next_step()
        
        if self.website.main_page.check_load():
            print_('login in successfully.')
        self.website.main_page.driver.save_cookie()


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
