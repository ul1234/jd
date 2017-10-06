#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, re, random, json
from website import Page, Website
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from miscellaneous import *
from account import Account


class MobilePage(Page):
    def click(self, element, offset_xscale = 0.5, offset_yscale = 0.5, wait_exit = False):
        #if self.webdriver.name == 'phantomjs':
        if 0:
            try:
                self.webdriver.phantomjs_click(element)
                element.click()
                #element.click()
            except:
                pass
        else:
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

class LoginPage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'm_login', r'http://passport.m.jd.com/user/login.action?returnurl=https://m.jd.com?indexloc=1')

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

class MainPage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'm_main', 'http://m.jd.com')

    def init_element(self):
        self.title_identity = chinese('品质保障')

class DataPage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'm_data', 'https://fbank.m.jd.com/')

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
            #pause()
        except NoSuchElementException as e:
            print_('no confirm element found! pass...')
            pass
            #raise e
        notice = self.webdriver.find_element(*self.sign_notice)
        btn = self.webdriver.find_element(*self.sign_element)
        #pause()
        self.click(btn)
        print_('notice: %s' % notice.text, info = True)
        self.goto_word_page()
        self.sign_word()
        pause()

    def goto_word_page(self):
        word_link = self.webdriver.find_elements(*self.sign_word_link)[4]
        #print word_link.get_attribute('outerHTML')
        pause()
        self.click(word_link, offset_yscale = 0.1, wait_exit = True)
        try:
            word_element = self.webdriver.find_element(*self.word_element)
        except NoSuchElementException:
            self.scroll_to_end()        # there's a page sometimes
            self.wait_element(self.goto_word_link)
            #self.save('before_search_go_to_word_driver')
            goto_word = self.webdriver.find_element(*self.goto_word_link)
            goto_word.click()
            time.sleep(0.5)

    def sign_word(self):
        word = self.webdriver.find_element(*self.word_element).get_attribute('innerHTML')
        print_('word: %s' % word)
        self.fill_elements({self.word_input: word})
        self.webdriver.find_element(*self.submit_word).click()
        time.sleep(2)
        data_value = self.webdriver.find_element(*self.word_data_value)
        if data_value.is_displayed():
            print_('[Result] Get %s successfully.' % data_value.get_attribute('innerHTML'), info = True)
        else:
            print_('[Result] Failed to get data.', info = True)

class ChargePage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'm_charge', 'https://newcz.m.jd.com/')

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

class GetCouponPage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'm_get_coupon', 'https://coupon.m.jd.com/')

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

class JsonPage(MobilePage):
    def __init__(self, website):
        Page.__init__(self, website, 'jsonp', r'https://api.m.jd.com', driver_key = 'requests')
        # https://api.m.jd.com/client.action?functionId=getFbankIndex&body=%7B%7D&client=ld&clientVersion=1.0.0&jsonp=jsonp_1507223536611_17111
        self.jd_api = r'https://api.m.jd.com/client.action?functionId=%s&body=%%7B%%7D&client=ld&clientVersion=1.0.0&jsonp=%s'
        self.data_info_id = 'getFbankIndex'
        self.data_sign_id = 'fBankSign'

    def _get_json(self, function_id):
        timestamp = int(time.time())
        temp = random.randint(10**4,10**5-1)
        jsonp_str = 'jsonp_%d_%d' % (timestamp, temp)
        api = self.jd_api % (function_id, jsonp_str)
        html = self.get_html(api, log_name = function_id)
        content = re.search(r'%s\((.*?)\)' % jsonp_str, html)
        if not content:
            print_('Error json response: %s' % html)
            return ''
        else:
            return json.loads(content.group(1))

    def data_info(self):
        response = self._get_json(self.data_info_id)
        #p_(response)
        sign_info = response['signInfo']
        sign_code, sign_message = int(sign_info['signCode']), sign_info['message']
        signed = (sign_code == 403)
        print_('Signed %s [%s].' % ('OK' if signed else 'FAIL', sign_message))
        channel_conf = response['channelConf']
        urls = [conf['url'] for conf in channel_conf if conf['name'] == chinese('口令流量')]
        if not urls: raise Exception('cannot find url for data more page.')
        data_more_url = urls[0]
        return signed, data_more_url

    def _data_sign(self):
        response = self._get_json(self.data_sign_id)
        #p_(response)
        code = int(response['errorCode'])
        sign_message = response['errorMessage'] or response['message']
        signed = (code != 302)
        print_('Signed %s [%s].' % ('OK' if signed else 'FAIL', sign_message))
        return signed

    def data_sign(self):
        signed, data_more_url = self.data_info()
        if not signed: self._data_sign()
        self.website.data_page.get_html(data_more_url, log_name = 'data_more')
        self.website.data_page.sign_word()

class JDMobile(Website):
    def __init__(self, user):
        Website.__init__(self, 'JD_mobile', user)
        self.login_page = LoginPage(self)
        self.main_page = MainPage(self)
        self.data_page = DataPage(self)
        self.charge_page = ChargePage(self)
        self.get_coupon_page = GetCouponPage(self)
        self.json_page = JsonPage(self)

    def is_login_page(self, page):
        return page.is_page(self.login_page)

class JDMobileAccount(Account):
    def __init__(self, user, pwd, rk_user = '', rk_pwd = ''):
        Account.__init__(self, JDMobile, user, pwd, rk_user, rk_pwd)

    def data_sign(self):
        #self.get(self.website.data_page)
        #self.website.data_page.sign()
        self.website.json_page.data_sign()
        
    def charge_coupon(self):
        self.get(self.website.charge_page)
        coupon_urls = self.website.charge_page.get_coupon_page_urls()
        for i in [4, 2, 1, 0]:
            self.website.get_coupon_page.get_coupon(url = coupon_urls[i])

