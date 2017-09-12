#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pickle, os, re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from miscellaneous import *

class PageNotloaded(Exception):
    pass

class CookieNotExist(Exception):
    pass

class Page:
    ALL_PAGES = []
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.save_html = True
        self.save_screen = False
        self.save_path = get_save_path()
        self.driver = None
        self.driver_key = 'selenium'
        if not hasattr(self, 'is_mobile_page'): self.is_mobile_page = False
        if hasattr(self, 'init_element'): self.init_element()
        Page.ALL_PAGES.append(self)

    def _install_driver(self, page_driver):
        self.driver = page_driver
        if hasattr(page_driver, 'driver'):
            self.webdriver = page_driver.driver

    def install_drivers(self, page_driver_dict):
        self._install_driver(page_driver_dict[self.driver_key])

    def load(self, check_cookie = True, show_title = True):
        print_('loading %s: %s' % (self.name, self.url))
        if check_cookie:
            if not self.driver.cookie_exist(): raise CookieNotExist('cookie not found!')
            if self.driver.should_load_cookie(): self.driver.load_cookie()
        self.driver.get(self.url)
        self.wait_loaded()
        if not self.check_enter(): raise PageNotloaded('page not loaded!')
        if hasattr(self, 'post_load'): self.post_load()
        msg = 'entered %s page!' % self.name
        msg += 'title: %s' % self.driver.title() if show_title else ''
        print_(msg)
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

    def scroll_to_end(self):
        last_height = self.webdriver.execute_script("return document.body.scrollHeight")
        while True:
            self.webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)
            new_height = self.webdriver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height


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



