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
import wx, ConfigParser


class TaskList:
    def __init__(self):
        self.wait_task = [] 
        self.running_task = [] 

    def load_tasks(self):
        if not hasattr(self, 'ini'): self.ini = ConfigParser.ConfigParser()
    def add_task(self, task):
        self.task_list.append(task)
        
    @thread_func()
    def run_task(self, _task):
        t = _task[0]
        t.state = 'running'
        t.run()
            
    def log(self, message):
        open(self.log_file, 'a').write(message + '\n')

    def run_forever(self):
        while True:
            for i, t in enumerate(self.wait_task):
                now = time.time()
                if ((t.next_start_time - now) < 60):
                    task_state = []
                    self.running_task.append(t)
                    del self.wait_task[i]
                    self.run_task([t])
            for i, t in enumerate(self.running_task):
               if t.state == 'finish':
                   del self.running_task[i]
               elif t.state == 'wait':
                   del self.running_task[i]
                   self.wait_task.append(t)
               
            time.sleep(30)


class Task1:
    def __init__(self, name, account, day, start_time, priority = 'low'):
        self.name = name
        self.next_start_time = 0 
        self.account = account
        self.priority = priority
        self.config_file = 'task.ini'

    def load_config(self):
        self.ini.read(self.config_file)
        if not self.name in self.ini.sections():
            print_('no task [%s] found!' % self.name)
            return []
        items = self.ini.items(name)

    def save_config(self, save_file):
        pass

    def prepare(self):
        pass

    def run(self):
        while time.time() < self.next_start_time:
            time.sleep(0.1)
        self.do()

class SignTask(Task1):
    def __init__(self, name, account):
        start_time = '00:05'
        day = 'everyday'
        priority = 'low'
        Task1.__init__(self, name, account, day, start_time, priority)


class JDDataSignTask(Task1):
    def __init__(self, account):
        self.account = account

    def do(self):
       self.account.data_sign()

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
    #task.do(task.data_sign, JDMobileAccount, ['13917053319']) #, 'jdcarol0701', 'jd_5f3fd86191c95'])
    #task.do(task.data_sign, JDMobileAccount, ['13917053319'])
    #task.do(task.charge_coupon, ['jdcarol0701'])


        
