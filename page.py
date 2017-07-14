#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from page_driver import RequestsDriver, SeleniumDriver
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from miscellaneous import *

class PageNotloaded(Exception):
    pass

class CookieNotExist(Exception):
    pass

class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.save_html = True
        self.save_screen = False
        self.save_path = get_save_path()
        self.driver = None
        if not hasattr(self, 'is_mobile_page'): self.is_mobile_page = False
        if hasattr(self, 'init_element'): self.init_element()
        All_pages.append(self)

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

    def wait_element(self, element, timeout = 10):
        self.driver.wait(timeout, lambda: EC.presence_of_element_located(element)(self.webdriver))

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

    def is_mobile(self):
        return self.is_mobile_page

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
        self.wait_element(self.code_element)
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

class MobilePage(Page):
    def __init__(self, name, url):
        self.is_mobile_page = True
        Page.__init__(self, name, url)

    def click(self, element, offset_xscale = 0.5, offset_yscale = 0.5, wait_exit = False):
        #if not hasattr(self, 'action'): self.action = ActionChains(self.webdriver)
        action = ActionChains(self.webdriver)
        action.move_to_element_with_offset(element, element.size['width']*offset_xscale, element.size['height']*offset_yscale)
        action.perform()
        action.click()
        action.perform()
        action = None
        time.sleep(0.5)
        if wait_exit:
            self.wait_exit()
            self.save('after_click')

class MobileLoginPage(MobilePage):
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

class MobileMainPage(MobilePage):
    def __init__(self):
        Page.__init__(self, 'm_main', 'http://m.jd.com')

    def init_element(self):
        self.title_identity = chinese('品质保障')

class MobileDataPage(MobilePage):
    def __init__(self):
        Page.__init__(self, 'm_data', 'https://fbank.m.jd.com/')

    def init_element(self):
        self.sign_element = (By.XPATH, '//span[text()="%s"]' % chinese('签到'))
        self.sign_notice = (By.XPATH, '//span[text()="%s"]/following-sibling::span' % chinese('签到'))
        self.sign_word_link = (By.XPATH, '//img[1]')
        self.confirm_element = (By.XPATH, '//div[contains(@data-src, ".png")]')
        self.word_element = (By.XPATH, '//span[contains(text(),"%s")]/following-sibling::span' % chinese('流量口令'))
        self.word_input = (By.CLASS_NAME, 'liuliang_word')
        self.submit_word = (By.CLASS_NAME, 'liuliang_check')
        self.word_data_value = (By.CLASS_NAME, 'liuliang_title_correct_value')
        self.title_identity = chinese('流量加油站')

    def sign(self):
        try:
            confirm = self.webdriver.find_element(*self.confirm_element)
            #print_(confirm.get_attribute('outerHTML'))
            self.click(confirm, offset_yscale = 0.88)
        except NoSuchElementException:
            pass
        notice = self.webdriver.find_element(*self.sign_notice)
        btn = self.webdriver.find_element(*self.sign_element)
        self.click(btn)
        print_('notice: %s' % notice.text)
        self.sign_word()

    def sign_word(self):
        word_link = self.webdriver.find_elements(*self.sign_word_link)[4]
        #print word_link.get_attribute('outerHTML')
        self.click(word_link, offset_yscale = 0.1, wait_exit = True)
        word = self.webdriver.find_element(*self.word_element).get_attribute('innerHTML')
        print_('word: %s' % word)
        self.fill_elements({self.word_input: word})
        self.webdriver.find_element(*self.submit_word).click()
        time.sleep(1)
        data_value = self.webdriver.find_element(*self.word_data_value)
        if data_value.is_displayed():
            print_('get %s successfully.' % data_value.get_attribute('innerHTML'))
        else:
            print_('failed to get data')

class MobileChargePage(MobilePage):
    def __init__(self):
        Page.__init__(self, 'm_charge', 'https://newcz.m.jd.com/')

    def init_element(self):
        self.title_identity = chinese('充值')
        self.recharge_banner = (By.XPATH, '//a[contains(@onclick, "MRecharge_Banner")]')
        self.coupon_link = (By.XPATH, '//a[contains(@href, "coupon.m.jd.com")]')

    def enter_coupon_page(self):
        banner = self.webdriver.find_element(*self.recharge_banner)
        self.click(banner, offset_yscale = 0.1, wait_exit = True)
        coupon_links = self.webdriver.find_elements(*self.coupon_link)
        print_('find %d coupons.' % len(coupon_links))
        self.click(coupon_links[4], wait_exit = True)  # here????????????????

class MobileGetCouponPage(MobilePage):
    def __init__(self):
        Page.__init__(self, 'm_get_coupon', 'https://coupon.m.jd.com/')

    def init_element(self):
        self.title_identity = chinese('领取优惠券')
        self.retrieve_button = (By.ID, 'btnSubmit')
        self.coupon_info_element = (By.CLASS_NAME, 'mjd-coupon')
        self.response_element = (By.CLASS_NAME, 'txt-response')

    def get_coupon_info(self):
        coupon_info_element = self.webdriver.find_element(*self.coupon_info_element)
        info = coupon_info_element.get_attribute('innerHTML')
        pattern = r'<strong>(.*?)</strong>.*?<p class="rule">\D*(\d+)\D*</p>.*?<i>(.*?)</i>(.*?)</p>.*?<p class="use-time">(.*?)</p>'
        r = re.search(pattern, info, flags = re.IGNORECASE|re.DOTALL)
        if r:
            discount_price, available_price, type, usage, time_range = [d.strip() for d in r.groups()]
            coupon_info = {'usage': usage, 'discount_price': discount_price, 'available_price': available_price,
                           'type': type, 'time_range': time_range}
        else:
            raise Exception('coupon info not found!')
        return coupon_info

    def get_coupon(self):
        coupon_info = self.get_coupon_info()
        btn = self.webdriver.find_element(*self.retrieve_button)
        btn.click()
        self.wait_element(self.response_element)
        response = self.webdriver.find_element(*self.response_element).get_attribute('innerHTML')
        print_('[Response] %s' % response)
        pause()

class AnyPage(Page):
    def __init__(self):
        Page.__init__(self, 'any', '')

    def get_html(self, url, log_name = ''):
        html = self.driver.get_html(url)
        if log_name: self.save(log_name)
        return html

All_pages = []

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
    m_data_page = MobileDataPage()
    m_charge_page = MobileChargePage()
    m_get_coupon_page = MobileGetCouponPage()

    def __init__(self, user):
        self.user = user
        self.install_requests_driver()
        self.install_selenium_driver()

    def install_driver(self, pages, driver):
        if not isinstance(pages, list): pages = [pages]
        for page in pages:
            page.install_driver(driver)

    def install_selenium_driver(self):
        self.selenium_driver = SeleniumDriver(self.user)
        self.selenium_driver.install_preload_cookie(lambda: self.main_page.pre_load())
        self.install_driver([self.login_page, self.activ_page, self.main_page, self.data_page], self.selenium_driver)

        self.mobile_selenium_driver = SeleniumDriver(self.user, is_mobile = True)
        self.mobile_selenium_driver.install_preload_cookie(lambda: self.m_main_page.pre_load())
        self.install_driver([self.m_login_page, self.m_main_page, self.m_data_page, self.m_charge_page, self.m_get_coupon_page], self.mobile_selenium_driver)

    def install_requests_driver(self):
        self.requests_driver = RequestsDriver(self.user)
        self.mobile_requests_driver = RequestsDriver(self.user, is_mobile = True)
        # default driver
        for page in All_pages:
            page.install_driver(self.mobile_requests_driver if page.is_mobile else self.requests_driver)

    def pre_login(self):
        #if not hasattr(self, 'selenium_driver'): self.install_selenium_driver()
        self.selenium_driver.invalidate_cookie()
        self.requests_driver.invalidate_cookie()

    def quit(self):
        if hasattr(self, 'selenium_driver'): self.selenium_driver.close()
        if hasattr(self, 'mobile_selenium_driver'): self.mobile_selenium_driver.close()

    def is_login_page(self, page):
        login_page = self.m_login_page if page.is_mobile else self.login_page
        return page.is_page(login_page)

