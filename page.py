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
    def init_element(self):
        pass
        
    def fill_form(self, user, pwd):
        pass
        
class ActiPage(Page):
    def init_element(self):
        pass
        
    def fill_form(self):
        pass

        
class ListPage(Page):
    def init_element(self):
        pass
        
        
class JD:
    login = Page('login', r'https://passport.jd.com/new/login.aspx')
    main = Page('main', r'http://www.jd.com')
    list = Page('list', r'http://order.jd.com/center/list.action')

    def __init__(self):
        pass




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
