#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, re
from page import Page, MobilePage
from page_driver import RequestsDriver, SeleniumDriver
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from miscellaneous import *

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
        if code_img.is_displayed():
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
        self.confirm_body = (By.XPATH, '//div[contains(@class, "jdreact-dialog-body")]')
        self.confirm_element = (By.XPATH, '//div[contains(@class, "jdreact-dialog-body")]/div')
        #self.confirm_element = (By.XPATH, '//div[contains(@data-src, ".png")]')
        self.word_element = (By.XPATH, '//span[contains(text(),"%s")]/following-sibling::span' % chinese('流量口令'))
        self.word_input = (By.CLASS_NAME, 'liuliang_word')
        self.submit_word = (By.CLASS_NAME, 'liuliang_check')
        self.word_data_value = (By.CLASS_NAME, 'liuliang_title_correct_value')
        self.goto_word_link = (By.XPATH, '//a[contains(@href, "pro.m.jd.com") and contains(@href, "active")]')
        #self.goto_word_link = (By.XPATH, '//a[contains(@href, "pro.m.jd.com")]')
        self.title_identity = chinese('流量加油站')

    def sign(self):
        try:
            #pause()
            #confirm = self.webdriver.find_element(*self.confirm_body)
            #print_(confirm.get_attribute('outerHTML'))
            #pause()
            confirm = self.webdriver.find_element(*self.confirm_element)
            #pause()
            #print_(confirm.get_attribute('outerHTML'))
            self.click(confirm, offset_yscale = 0.88)
            #pause()
        except NoSuchElementException as e:
            #pass
            raise e
        notice = self.webdriver.find_element(*self.sign_notice)
        btn = self.webdriver.find_element(*self.sign_element)
        self.click(btn)
        print_('notice: %s' % notice.text, info = True)
        self.sign_word()

    def goto_word_page(self):
        try:
            word_element = self.webdriver.find_element(*self.word_element)
        except NoSuchElementException:
            self.scroll_to_end()
            self.wait_element(self.goto_word_link)
            #self.save('before_search_go_to_word_driver')
            goto_word = self.webdriver.find_element(*self.goto_word_link)
            goto_word.click()
            time.sleep(0.5)

    def sign_word(self):
        word_link = self.webdriver.find_elements(*self.sign_word_link)[4]
        #print word_link.get_attribute('outerHTML')
        self.click(word_link, offset_yscale = 0.1, wait_exit = True)
        self.goto_word_page()  # there's a page sometimes
        word = self.webdriver.find_element(*self.word_element).get_attribute('innerHTML')
        print_('word: %s' % word)
        self.fill_elements({self.word_input: word})
        self.webdriver.find_element(*self.submit_word).click()
        time.sleep(1)
        data_value = self.webdriver.find_element(*self.word_data_value)
        if data_value.is_displayed():
            print_('[Result] Get %s successfully.' % data_value.get_attribute('innerHTML'), info = True)
        else:
            print_('[Result] Failed to get data.', info = True)

class MobileChargePage(MobilePage):
    def __init__(self):
        Page.__init__(self, 'm_charge', 'https://newcz.m.jd.com/')

    def init_element(self):
        self.title_identity = chinese('充值')
        self.recharge_banner = (By.XPATH, '//a[contains(@onclick, "MRecharge_Banner")]')
        self.coupon_link = (By.XPATH, '//a[contains(@href, "coupon.m.jd.com")]')

    def get_coupon_page_urls(self):
        banner = self.webdriver.find_element(*self.recharge_banner)
        self.click(banner, offset_yscale = 0.1, wait_exit = True)
        coupon_links = self.webdriver.find_elements(*self.coupon_link)
        coupon_num = len(coupon_links)
        print_('Find %d coupons.' % coupon_num, info = True)
        coupon_urls = [self._get_coupon_url(i) for i in range(coupon_num)]
        return coupon_urls

    def _get_coupon_url(self, index = 0):
        coupon_links = self.webdriver.find_elements(*self.coupon_link)
        self.click(coupon_links[index], wait_exit = True)
        coupon_url = self.webdriver.current_url
        print_('[%d]%s' % (index, coupon_url))
        self.webdriver.back()
        return coupon_url


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

    def _str(self, info):
        return '%s-%s, %s, %s' % (info['available_price'], info['discount_price'], info['usage'], info['time_range'])

    def get_coupon(self, url = ''):
        if url: self.driver.get(url)
        coupon_info = self.get_coupon_info()
        print_('Try to get [%s]' % self._str(coupon_info))
        btn = self.webdriver.find_element(*self.retrieve_button)
        if chinese('不可领取') in btn.get_attribute('innerHTML'):
            print_('[Response]Cannot get the coupon. Have to wait.', info = True)
        else:
            btn.click()
            self.wait_element(self.response_element)
            response = self.webdriver.find_element(*self.response_element).get_attribute('innerHTML')
            print_('[Response]%s' % html_content(response, '<span>', '</span>').strip(), info = True)

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
    m_data_page = MobileDataPage()
    m_charge_page = MobileChargePage()
    m_get_coupon_page = MobileGetCouponPage()

    def __init__(self, user):
        self.user = user
        self.install_requests_driver()
        self.install_selenium_driver()

    def install_drivers(self):
        self.requests_driver = RequestsDriver(self.user)
        self.selenium_driver = SeleniumDriver(self.user)
        self.selenium_driver.install_preload_cookie(lambda: self.main_page.pre_load())


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
        for page in Page.ALL_PAGES:
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
