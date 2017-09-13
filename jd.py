#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, re
from website import Page, Website
from page_driver import RequestsDriver, SeleniumDriver
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from miscellaneous import *
from account import Account

class LoginPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'login', r'https://passport.jd.com/new/login.aspx')
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
    def __init__(self, website):
        Page.__init__(self, website, 'activate')

    def init_element(self):
        self.submit_element = (By.ID, 'submitBtn')
        self.code_element = (By.ID, 'code')
        self.title_identity = chinese('激活')

    def fill(self):
        self.wait_element(self.code_element)
        code = raw_input('Please input the auth code:')
        self.fill_elements({self.code_element: code})


class MainPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'main', 'http://www.jd.com')

    def init_element(self):
        self.title_identity = chinese('正品低价')


class ListPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'list', r'http://order.jd.com/center/list.action', driver_key = 'requests')

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
    def __init__(self, website):
        Page.__init__(self, website, 'coupon', r'http://quan.jd.com/user_quan.action?couponType=-1&sort=1&page=1', driver_key = 'requests')

    def init_element(self):
        self.title_identity = chinese('优惠券')
        self.list_url = r'http://a.jd.com/coupons.html?page=%d'
        self.free_coupon_url = r'http://a.jd.com/ajax/freeGetCoupon.html?key=%s&r=0.7308938041372057'
        self.bean_coupon_url = r'http://a.jd.com/ajax/beanExchangeCoupon.html?id=%s&r=0.5559653794026669'

    def _last_page(self, html):
        pattern = r'>(\d+)</a>[\n\r\s]*<a[^>]*ui-pager-next'
        r = re.search(pattern, html)
        if r:
            return int(r.group(1))
        else:
            raise Exception('cannot find last page number, check the html file.')

    def get_coupons(self):
        html = self.driver.get_html(self.list_url % 1)  # page 1
        MAX_PAGES = 10
        last_page_num = min(MAX_PAGES, self._last_page(html))
        coupons = self._coupons_list(html = html)
        for page in xrange(2, last_page_num + 1):
            coupons.update(self._coupons_list(page))
        return coupons

    def _coupons_list(self, page = 1, html = ''):
        url = self.list_url % page
        if not html: html = self.driver.get_html(url)
        self.save('coupons_list_%d' % page)
        coupons_dict = {}
        coupons = re.findall('<div class="quan-item(.*?)<div class="q-state">', html, flags = re.DOTALL)
        for coupon in coupons:
            free_pattern = r'data-key="(.*?)"\s*data-linkUrl="(.*?)".*?<strong class="num">(.*?)</strong>.*?<div class="typ-txt">(.*?)</div>.*?<span class="ftx-06">\D*(\d+)\D*</span>.*?<p title="(.*?)".*?coupon-time.*?>(.*?)</div>'
            r = re.search(free_pattern, coupon, flags = re.IGNORECASE|re.DOTALL)
            if r:
                data_key, link_url, discount_price, type, available_price, usage, time_range = [d.strip() for d in r.groups()]
                get_url = self.free_coupon_url % data_key
                coupons_dict[data_key] = {'usage': usage, 'discount_price': discount_price, 'available_price': available_price,
                                         'data_key': data_key, 'link_url': link_url, 'type': type, 'get_url': get_url, 'time_range': time_range}
            else:
                bean_pattern = r'data-linkUrl="(.*?)".*?data-id="(.*?)".*?data-bean="(.*?)".*<strong class="num">(.*?)</strong>.*?<div class="typ-txt">(.*?)</div>.*?<span class="ftx-06">\D*(\d+)\D*</span>.*?<p title="(.*?)".*?coupon-time.*?>(.*?)</div>'
                r = re.search(bean_pattern, coupon, flags = re.IGNORECASE|re.DOTALL)
                if r:
                    link_url, data_id, data_bean, discount_price, type, available_price, usage, time_range = r.groups()
                    get_url = self.bean_coupon_url % data_id
                    coupons_dict[data_id] = {'usage': usage, 'discount_price': discount_price, 'available_price': available_price,
                                             'data_id': data_id, 'data_bean': data_bean, 'link_url': link_url, 'type': type, 'get_url': get_url, 'time_range': time_range}
                else:
                    print_('cannot find coupon list in url: %s' % url)
        print_('find %d coupons in page %d' % (len(coupons_dict), page))
        return coupons_dict

class DataPage(Page):
    def __init__(self, website):
        Page.__init__(self, website, 'data', r'http://datawallet.jd.com/profile.html')

    def init_element(self):
        self.title_identity = chinese('流量加油站')
        self.sign_button = (By.CLASS_NAME, 'btn-sign')
        self.sign_dialog = (By.CLASS_NAME, 'dialog-sign')
        self.sign_text = (By.XPATH, '//div[@class="dialog-sign"]/h3')
        self.sign_ok = (By.CLASS_NAME, 'btn-sign-cancel')
        self.key_input = (By.CLASS_NAME, 'input-key')
        self.key_button = (By.CLASS_NAME, 'btn-key')
        self.key_image = (By.CLASS_NAME, 'userDefinedArea')

    def sign(self):
        btn = self.webdriver.find_element(*self.sign_button)
        if btn.is_enabled():
            btn.click()
            print_('signed data.')
            self.wait_element(self.sign_dialog)
            text = self.webdriver.find_element(*self.sign_text)
            print_('alert: %s' % text.get_attribute('innerHTML'))
            btn = self.webdriver.find_element(*self.sign_ok)
            btn.click()
        else:
            print_('data already signed.')

    def key(self):
        btn = self.webdriver.find_element(*self.key_button)
        btn.click()
        print_('check key page...')
        self.webdriver.switch_to_newpage()
        self.wait_element(self.key_image)
        images = self.webdriver.find_elements(*self.key_image)
        for image in images:
            html = image.get_attribute('innerHTML')
            links = html_attributes(html, '<img', 'original')
            if len(links) == 1:
                # save the image????
                pass

class JD(Website):
    def __init__(self, user):
        Website.__init__(self, 'JD', user)
        self.login_page = LoginPage(self)
        self.activ_page = ActiPage(self)
        self.list_page = ListPage(self)
        self.main_page = MainPage(self)
        self.coupon_page = CouponPage(self)
        self.data_page = DataPage(self)

    def is_login_page(self, page):
        return page.is_page(self.login_page)

class JDAccount(Account):
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        Account.__init__(self, JD, user, pwd, rk_user, rk_pwd)

    def login_next_step(self):
        if self.website.activ_page.check_load():
            self.website.activ_page.fill()
            self.website.activ_page.submit()

    def get_orders(self):
        self.get(self.website.list_page)
        orders = self.website.list_page.my_order()
        print_('total %d orders.' % len(orders))
        import pprint
        pprint.pprint(orders[0])

    def data_sign(self):
        self.get(self.website.data_page)
        self.website.data_page.sign()

    