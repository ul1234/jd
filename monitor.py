#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time, re
from page import Page
from page_driver import RequestsDriver
from miscellaneous import *


class MonitorPage(Page):
    def __init__(self, url):
        Page.__init__(self, 'monitor', url)
        self.enable_save(False, False)
        self.install_driver(RequestsDriver())

    def init_element(self):
        self.title_identity = chinese('百善')

class Monitor:
    def __init__(self):
        pass

    def cond_re(self, html, pattern):
        r = re.search(pattern, html)
        if r:
            return True, r.groups()
        return False

    def monitor(self, url, cond):
        page = MonitorPage(url)
        PERIOD = 5
        times_second = 0
        while True:
            page.load(check_cookie = False, show_title = False)
            html = page.driver.page_source()
            result = cond(html)
            if result: break
            time.sleep(PERIOD)
            times_second += PERIOD
            if times_second > 30:
                print_('monitor working...')
                times_second = 0
        msg = ','.join(result[1]) if result[1] else ''
        msg += '[condition triggered!!!]'
        print msg
        self.MessageBox(msg)

    def MessageBox(self, text, title = 'Monitor', style = 0):
        from ctypes import windll
        MB_OK = 0x0
        MB_OKCANCEL = 0x1
        MB_ABORTRETRYIGNORE = 0x2
        MB_YESNOCANCEL = 0x3
        MB_YESNO = 0x4
        MB_RETRYCANCEL = 0x5

        MB_ICONHAND = MB_ICONSTOP = MB_ICONERRPR = 0x10
        MB_ICONQUESTION = 0x20
        MB_ICONEXCLAIMATION = 0x30
        MB_ICONASTERISK = MB_ICONINFOMRAITON = 0x40

        MB_DEFAULTBUTTON1 = 0x0
        MB_DEFAULTBUTTON2 = 0x100
        MB_DEFAULTBUTTON3 = 0x200
        MB_DEFAULTBUTTON4 = 0x300

        MB_SETFOREGROUND = 0x10000
        MB_TOPMOST = 0x40000
        windll.user32.MessageBoxA(0, text, title, MB_OK | MB_TOPMOST)

if __name__ == '__main__':
    m = Monitor()
    cond = lambda html: m.cond_re(html, chinese('金饭碗福利标(201707210[^1])'))
    m.monitor(r'https://www.jfwcaifu.com/loan/category/welfare.html', cond)
