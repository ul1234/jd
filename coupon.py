#!/usr/bin/python
# -*- coding: utf-8 -*-

from website import PageNotloaded, CookieNotExist
#from jd import JD
from miscellaneous import *

class Coupon:
    def __init__(self, account):
        self.account = account
        self.jd = account.jd

    def list_coupons(self):
        self.account.get(self.jd.coupon_page)
        coupons = self.jd.coupon_page.get_coupons()
        filters = self.filter_coupons(coupons, [chinese('全品'), chinese('手机')])
        print_('filter %d from total %d coupons.' % (len(filters), len(coupons)))
        self.show_coupons(filters)
        return filters

    def filter_coupons(self, coupons, include_list, exclude_list = []):
        result = {}
        for key, coupon in coupons.items():
            if any([i in coupon['usage'] for i in include_list]) and all([i not in coupon['usage'] for i in exclude_list]):
                #print_(coupon['usage'])  # for test
                result[key] = coupon
        return result
        
    def show_coupons(self, coupons):
        index = 0
        for key, coupon in coupons.items():
            index += 1
            print_('[%d] %s-%s, %s, %s' % (index, coupon['available_price'], coupon['discount_price'], coupon['usage'], coupon['get_url']))
            
    def get_server_time(self):
        # http://a.jd.com/ajax/queryServerData.html?r=0.122334456
        url = r'http://a.jd.com/ajax/queryServerData.html?r=0.122334456'
        html = self.jd.page.get_html(url, 'server_time')
        print html

        