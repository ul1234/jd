#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from page_driver import RequestsDriver, SeleniumDriver
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
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
        self.save_path = get_save_path()
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
        print_('submitting %s page[%s]...' % (self.name, self.url))
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
            f = os.path.join(self.save_path, '%d_%s_%s.html' % (self.save_cnt, self.name, info))
            open(f, 'w').write(html.encode(charset, 'ignore'))
            print_('%s [%s] saved.' % (f, charset_str))
        if self.save_screen:
            if not hasattr(self, 'save_cnt'): self.save_cnt = 0
            self.save_cnt += 1
            f = os.path.join(self.save_path, '%d_%s_%s.png' % (self.save_cnt, self.name, info))
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
    def __init__(self):
        Page.__init__(self, 'data', r'http://datawallet.jd.com/profile.html')

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
            self.driver.wait(10, lambda: EC.presence_of_element_located(self.sign_dialog)(self.webdriver))
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
        self.driver.wait(10, lambda: EC.presence_of_element_located(self.key_image)(self.webdriver))
        images = self.webdriver.find_elements(*self.key_image)
        for image in images:
            html = image.get_attribute('innerHTML')
            links = html_attributes(html, '<img', 'original')
            if len(links) == 1:
                # save the image????
                pass

class MobileLoginPage(Page):
    def __init__(self):
        Page.__init__(self, 'm_login', r'http://passport.m.jd.com/user/login.action?returnurl=https://m.jd.com?indexloc=1')

    def init_element(self):
        self.submit_element = (By.ID, 'loginBtn')
        self.user_element = (By.ID, 'username')
        self.pwd_element = (By.ID, 'password')
        self.code_element = (By.ID, 'code')
        self.code_img = (By.ID, 'imgCode')
        self.title_identity = chinese('登录')

    def fill(self, user, pwd):
        self.fill_code()
        self.fill_elements({self.user_element: user, self.pwd_element: pwd})
        #raise Exception('after fill') # for test

    def fill_code(self):
        code_img = self.webdriver.find_element(*self.code_img)
        code = Captcha().img(self.webdriver, code_img).resolve()
        self.fill_elements({self.code_element: code})

class MobileMainPage(Page):
    def __init__(self):
        Page.__init__(self, 'm_main', 'http://m.jd.com')

    def init_element(self):
        self.title_identity = chinese('品质保障')

class AnyPage(Page):
    def __init__(self):
        Page.__init__(self, 'any', '')

    def get_html(self, url, log_name = ''):
        html = self.driver.get_html(url)
        if log_name: self.save(log_name)
        return html


class JD:
    login_page = LoginPage()
    activ_page = ActiPage()
    list_page = ListPage()
    main_page = MainPage()
    coupon_page = CouponPage()
    data_page = DataPage()
    page = AnyPage()

    m_login_page = MobileLoginPage()
    m_main_page = MobileMainPage()

    def __init__(self):
        self.install_requests_driver()
        self.install_selenium_driver()

    def install_driver(self, pages, driver):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            page.install_driver(driver)

    def install_selenium_driver(self):
        self.selenium_driver = SeleniumDriver()
        self.selenium_driver.install_preload_cookie(lambda: self.main_page.pre_load())
        self.install_driver([self.login_page, self.activ_page, self.main_page, self.data_page, self.m_login_page, self.m_main_page], self.selenium_driver)

    def install_requests_driver(self):
        self.requests_driver = RequestsDriver()
        Page.default_driver(self.requests_driver)

    def pre_login(self):
        #if not hasattr(self, 'selenium_driver'): self.install_selenium_driver()
        self.selenium_driver.invalidate_cookie()
        self.requests_driver.invalidate_cookie()

    def quit(self):
        if hasattr(self, 'selenium_driver'): self.selenium_driver.close()


