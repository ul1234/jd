#!/usr/bin/python
# -*- coding: utf-8 -*-

# 1. sign
# 2. get the regular coupon
# 3. check the good coupon
# 4. push to the wechat
# 5. for many users

# 6. sign for many apps
# 7. too slow for suning main page to fully loaded, try to escape earlier

from jd import JDAccount
from jd_mobile import JDMobileAccount
from miscellaneous import *
import wx


class Task:
    def __init__(self, wx = False):
        self.users = self.get_users()
        self.task_cnt = 0
        if wx: wx.init()

    def get_users(self):
        users = {}
        with open('user.dat', 'r') as f:
            for line in f:
                if line.strip():
                    u, p = line.strip().split(':')
                    users[u] = p
        print_([u for u in users])
        return users
    
    def data_sign(self, account):
        account.data_sign()
            
    def charge_coupon(self, account):
        account.charge_coupon()

    def do(self, func, account, users = []):
        user_cnt = 0
        for u, p in self.users.items():
            if not users or u in users:
                print_('\n\n############ Task %d [%s] User %d [%s] ############\n' % (self.task_cnt, func.__name__, user_cnt, u), info = True)
                acc = account(u, p)
                try:
                    func(acc)
                finally:
                    acc.quit()
                user_cnt += 1
                print_flush()
        self.task_cnt += 1

if __name__ == '__main__':
    task = Task()
    # 13917053319, jdcarol0701, jd_5f3fd86191c95, 15618233071
    task.do(task.data_sign, JDMobileAccount)
    #task.do(task.data_sign, ['13917053319', 'jdcarol0701', 'jd_5f3fd86191c95'])
    #task.do(task.data_sign, JDMobileAccount, ['13917053319'])
    #task.do(task.charge_coupon, ['jdcarol0701'])


        