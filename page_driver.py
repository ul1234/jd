#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from miscellaneous import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class PageDriver:
    def __init__(self, site, user):
        self.cookie_loaded = False
        self.cookie_file = os.path.join(get_save_path(), 'cookies_%s_%s.dat' % (site, user))

    def title(self, page_html = None):
        html = self.page_source() if page_html is None else page_html
        return html_content(html, '<title>', '</title>').strip().replace('\n', '')\
               .replace('\t', '').replace('\r', '').replace(' ', '')
        #r = re.search(r'<title>([^<]+)<', html)
        #if r:
        #    return r.group(1).strip()
        #else:
        #    return None
            
    def get_html(self, url):
        self.get(url)
        return self.page_source()

    def save_cookie(self):
        pickle.dump(self.get_cookies(), open(self.cookie_file, 'wb'))
        print_('cookie saved.')
        self.cookie_loaded = True

    def install_preload_cookie(self, preload_cookie_func):
        self.preload_cookie = preload_cookie_func

    def load_cookie(self):
        if hasattr(self, 'preload_cookie'): self.preload_cookie()
        print_('start to load cookie...')
        if os.path.isfile(self.cookie_file):
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            self.add_cookies(cookies)
            self.cookie_loaded = True
            print_('cookie loaded.')
            return True
        return False

    def cookie_exist(self):
        return os.path.isfile(self.cookie_file)

    def invalidate_cookie(self):
        self.cookie_loaded = False
        if self.cookie_exist():
            os.remove(self.cookie_file)
            print_('cookie deleted.')

    def should_load_cookie(self):
        return self.cookie_exist() and not self.cookie_loaded

class RequestsDriver(PageDriver):
    def __init__(self, site, user = 'requests'):
        self.session = requests.Session()
        self.page_html = None
        self.cookies = {}
        PageDriver.__init__(self, site, user)

    def page_source(self):
        return self.page_html

    def get(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/54.0.2840.59 Safari/537.36 115Browser/8.0.0',
            'Accept': 'application / json',
            'Referer': url
        }
        r = self.session.get(url, headers = headers, cookies = self.cookies, verify = False)
        print_('get url [%s] status %d' % (url, r.status_code))
        self.page_html = r.text
        #print_('title: %s' % self.title())

    def wait(self, timeout, condition_func):
        #if not condition_func(): raise Exception('wait timeout')
        return True if condition_func() else False
        #for i in xrange(timeout):
        #    if condition_func():
        #        return True
        #    time.sleep(1)
        #return False

    def add_cookies(self, cookies):
        self.cookies = {}
        for cookie in cookies:
            self.cookies[cookie['name']] = cookie['value']

class SeleniumDriver(PageDriver):
    def __init__(self, site, user = 'selenium'):
        #self.driver = webdriver.PhantomJS()  # not work in many situations
        self.driver = webdriver.Chrome()
        #self.driver.set_window_position(-10000,0)  # hide the brower
        print_('selenium driver open browser.')
        PageDriver.__init__(self, site, user)

    def page_source(self):
        #html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return self.driver.page_source

    def get(self, url, timeout = -1):
        if timeout >= 0:
            self.driver.set_page_load_timeout(timeout)
            print_('set page load timeout to %ds.' % timeout, output_time = True)
        try:
            self.driver.get(url)
        except TimeoutException as e:
            print_('Stop loading %s due to %ds timeout.' % (url, timeout))
        finally:
            if timeout >= 0:
                self.driver.set_page_load_timeout(-1)   # restore
                print_('set page load timeout back to infinite.', output_time = True)
        #print_('title: %s' % self.title())

    def wait(self, timeout, condition_func):
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: condition_func())
            return True
        except TimeoutException as e:
            print_(e)
            return False

    def get_cookies(self):
        return self.driver.get_cookies()

    def add_cookies(self, cookies):
        for cookie in cookies:
            try:
                #self.driver.add_cookie(cookie)
                self.driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry') if k in cookie})
            except WebDriverException as e:
                if e.msg.find('invalid cookie domain') >= 0:   # ignore invalid cookie domain
                    pass
                else:
                    raise e

    def close(self):
        print_('selenium driver close browser.')
        self.driver.quit()
        
    def switch_to_newpage(self):
        self.backup_page_handle = self.driver.current_window_handle
        new_page_handle = None
        while not new_page_handle:
            for handle in self.driver.window_handles:
                if handle != self.backup_page_handle:
                    new_page_handle = handle
                    break
        self.driver.switch_to.window(new_page_handle)
        print_('switch to new page.')

    def switch_back(self):
        if self.backup_page_handle:
            self.driver.close()
            self.driver.switch_to.window(self.backup_page_handle)
            self.backup_page_handle = None
            print_('switch back the page.')
