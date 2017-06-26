#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from page_driver import RequestsDriver, SeleniumDriver
from selenium.webdriver.common.by import By
from miscellaneous import *

class PageNotloaded(Exception):
    pass

class CookieNotExist(Exception):
    pass

class Page:
    driver = None
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.save_html = True
        self.save_screen = False
        if hasattr(self, 'init_element'):
            self.init_element()

    @staticmethod
    def default_driver(web_driver):
        Page.driver = web_driver

    def install_driver(self, page_driver):
        self.driver = page_driver
        if hasattr(page_driver, 'driver'):
            self.webdriver = page_driver.driver

    def load(self, check_cookie = True):
        print_('loading %s: %s' % (self.name, self.url))
        if check_cookie:
            if not self.driver.cookie_exist(): raise CookieNotExist('cookie not found!')
            if self.driver.should_load_cookie(): self.driver.load_cookie()
        self.driver.get(self.url)
        self.wait_loaded()
        if not self.check_enter(): raise PageNotloaded('page not loaded!')
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title()))
        self.save('after_load')

    def pre_load(self):
        print_('preloading %s: %s' % (self.name, self.url))
        self.driver.get(self.url)

    def check_load(self):
        if not self.check_enter(): return False
        if hasattr(self, 'post_load'): self.post_load()
        print_('entered %s page! title: %s' % (self.name, self.driver.title()))
        self.save('jump_load')
        return True

    def is_page(self, page):
        return page.check_enter(self.driver.page_source())
        
    def check_pages(self, pages):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            if self.is_page(page):
                return page.name
        return ''

    def check_enter(self, page_html = None):
        return self.driver.title(page_html).find(self.title_identity) >= 0

    def wait_loaded(self, timeout = 10):
        #WebDriverWait(self.driver, timeout).until(lambda driver: self.check_enter())
        self.driver.wait(timeout, self.check_enter)

    def check_exit(self, page_html = None):
        return not self.check_enter(page_html)

    def wait_exit(self, timeout = 10):
        #WebDriverWait(self.driver, timeout).until(lambda driver: self.check_exit())
        self.driver.wait(timeout, self.check_exit)
        print_('exit %s page! enter page: %s' % (self.name, self.driver.title()))

    def submit(self):
        print_('submitting %s page: %s' % (self.name, self.url))
        self.webdriver.find_element(*self.submit_element).click()
        self.wait_exit()
        self.save('after_submit')

    def enable_save(self, html, screen):
        self.save_html = html
        self.save_screen = screen

    def save(self, info, html = None):
        if self.save_html:
            html = html if not html is None else self.driver.page_source()
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            r = re.search(r'<meta[^>]+charset="?(.*?)"', html)
            charset = 'utf-8' if not r else r.group(1)
            charset_str = '%s (%s)' % (charset, 'detected' if r else 'not detected')
            f = '%d_%s_%s.html' % (self.save_cnt, self.name, info)
            open(f, 'w').write(html.encode(charset, 'ignore'))
            print_('%s [%s] saved.' % (f, charset_str))
        if self.save_screen:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            f = '%d_%s_%s.png' % (self.save_cnt, self.name, info)
            self.webdriver.save_screenshot(f)
            print_('%s saved.' % f)

    def fill_elements(self, elements):
        for element, value in elements.items():
            elem = self.webdriver.find_element(*element)
            elem.clear()
            elem.send_keys(value)

class LoginPage(Page):
    def __init__(self):
        Page.__init__(self, 'login', r'https://passport.jd.com/new/login.aspx')
        #self.enable_save(True, True)

    def init_element(self):
        self.switch_login_element = (By.XPATH, "//div[@class='login-tab login-tab-r']/a")
        self.submit_element = (By.ID, 'loginsubmit')
        self.user_element = (By.ID, 'loginname')
        self.pwd_element = (By.ID, 'nloginpwd')
        self.title_identity = chinese('登录')

    def post_load(self):
        self.webdriver.find_element(*self.switch_login_element).click()

    def fill(self, user, pwd):
        self.fill_elements({self.user_element: user, self.pwd_element: pwd})
        #raise Exception('after fill') # for test


class ActiPage(Page):
    def __init__(self):
        Page.__init__(self, 'activate', '')

    def init_element(self):
        self.submit_element = (By.ID, 'submitBtn')
        self.code_element = (By.ID, 'code')
        self.title_identity = chinese('激活')

    def fill(self):
        self.driver.wait(10, lambda: EC.presence_of_element_located(self.code_element)(self.webdriver))
        code = raw_input('Please input the auth code:')
        self.fill_elements({self.code_element: code})


class MainPage(Page):
    def __init__(self):
        Page.__init__(self, 'main', 'http://www.jd.com')

    def init_element(self):
        self.title_identity = chinese('正品低价')


class ListPage(Page):
    def __init__(self):
        Page.__init__(self, 'list', r'http://order.jd.com/center/list.action')

    def init_element(self):
        self.title_identity = chinese('订单')

    def my_order(self, html = None):
        html = html if not html is None else self.driver.page_source()
        orders = html_contents(html, '<tbody id=', '</tbody>')
        print len(orders)
        order_list = []
        for order in orders:
            try:
                order_time = html_content(order, '<span class="dealtime"', '</span>')
                order_id = html_content(order, '<a name=.orderIdLinks.', '</a>')
                order_link = html_attribute(order, '<a name=.orderIdLinks.', 'href')
                order_info = html_content(order, '<div class="pc"', '</div>')
                order_name = html_content(order_info, '<strong>', '</strong>')
                order_addr = html_content(order_info, '<p>', '</p>')
                order_phone = html_contents(order_info, '<p>', '</p>')[1]
                order_item_id = html_attribute(order, '<span', 'data-sku')
                item_html = self.driver.get_html('http://item.jd.com/%s.html' % str(order_item_id))
                order_item_name = html_content(item_html, '<title>', '</title>')
                order_list.append({'id': order_id, 'time': order_time, 'item_id': order_item_id, 'item': order_item_name, 
                                   'link': order_link, 'name': order_name, 'addr': order_addr, 'phone': order_phone})
            except Exception as e:
                print_(e)
                #raise
        return order_list
        
class CouponPage(Page):
    def __init__(self):
        Page.__init__(self, 'coupon', r'http://quan.jd.com/user_quan.action?couponType=-1&sort=1&page=1')
        
    def init_element(self):
        self.title_identity = chinese('优惠券')
        
    def my_coupons(self):
        pass
        
        
class JD:
    login_page = LoginPage()
    activ_page = ActiPage()
    list_page = ListPage()
    main_page = MainPage()
    coupon_page = CouponPage()
        
    def __init__(self):
        self.install_requests_driver()

    def install_driver(self, pages, driver):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            page.install_driver(driver)

    def install_selenium_driver(self):
        self.selenium_driver = SeleniumDriver()
        self.selenium_driver.install_preload_cookie(lambda: self.main_page.pre_load())
        self.install_driver([self.login_page, self.activ_page, self.main_page], self.selenium_driver)

    def install_requests_driver(self):
        self.requests_driver = RequestsDriver()
        Page.default_driver(self.requests_driver)

    def pre_login(self):
        if not hasattr(self, 'selenium_driver'): self.install_selenium_driver()
        self.selenium_driver.invalidate_cookie()
        self.requests_driver.invalidate_cookie()

    def quit(self):
        if hasattr(self, 'selenium_driver'): self.selenium_driver.close()


