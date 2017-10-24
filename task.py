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
import time
from datetime import datetime
import wx, ConfigParser


class TaskList:
    def __init__(self):
        self.wait_task = [] 
        self.running_task = [] 

    def add_task(self, task_class, users = []):
        user_file = task_class.USER_FILE
        users = self.get_users(user_file) 
        for u, p in users.items():
            if not users or u in users:
                self._add_task(task_class(u, p))
                print_('add task %s for user %s!' % (task_class.__name__, u))

    def get_users(self, user_file):
        users = {}
        with open(user_file, 'r') as f:
            for line in f:
                if line.strip():
                    u, p = line.strip().split(':')
                    users[u] = p
        print_([u for u in users])
        return users

    def load_tasks(self):
        if not hasattr(self, 'ini'): self.ini = ConfigParser.ConfigParser()
        for n in self.ini.sections():
            pass

    def _add_task(self, task):
        self.wait_task.append(task)
        
    #@thread_func()
    @pass_exception
    def run_task(self, _task):
        t = _task[0]
        t.state = 'running'
        t.run()
            
    def log(self, message, output_time = True):
        time_str = '[%s]' % datetime.now().strftime('%y%m%d %H:%M:%S') if output_time else ''
        msg = '%s%s' % (time_str, message)
        open(self.log_file, 'a').write(msg + '\n')

    def run_forever(self):
        WAIT_TIME = 30
        while True:
            for i, t in enumerate(self.wait_task):
                now = time.time()
                if ((t.next_start_time - now) < 2*WAIT_TIME):
                    task_state = []
                    self.running_task.append(t)
                    del self.wait_task[i]
                    self.run_task([t])
            for i, t in enumerate(self.running_task):
               if t.state == 'finished':
                   del self.running_task[i]
               elif t.state == 'wait':
                   del self.running_task[i]
                   self.wait_task.append(t)
            time.sleep(WAIT_TIME)



class Task:
    def __init__(self, name, account, day, start_time, priority = 'low'):
        self.name = name
        self.day = day
        self.start_time = start_time
        self.next_start_time = 0 
        self.account = account
        self.priority = priority
        self.config_file = 'task.ini'
        self.ini_file = '%s_%s.ini' % (name, account.user)

    def set_next_time(self, today):
        pass

    def load_config(self):
        if not os.path.isfile(self.ini_file):
            return
        self.ini.read(self.ini_file)
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
        if self.day == 'everyday':
            self.next_start_time = 0
            self.state = 'wait'
        else:
            self.state = 'finished'

class SignTask(Task):
    def __init__(self, name, account):
        start_time = '00:05'
        day = 'everyday'
        priority = 'low'
        Task.__init__(self, name, account, day, start_time, priority)


class JDDataSignTask(SignTask):
    USER_FILE = 'user.dat'
    def __init__(self, user, passwd):
        acc = JDMobileAccount(user, passwd)
        SignTask.__init__(self, 'jd_data_sign', acc)

    def do(self):
       self.account.data_sign()


class TaskBak:
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
    s = 1
    if s == 1:
        task = TaskBak()
        # 13917053319, jdcarol0701, jd_5f3fd86191c95, 15618233071
        task.do(task.data_sign, JDMobileAccount)
        #task.do(task.data_sign, JDMobileAccount, ['13917053319']) #, 'jdcarol0701', 'jd_5f3fd86191c95'])
        #task.do(task.data_sign, JDMobileAccount, ['13917053319'])
        #task.do(task.charge_coupon, ['jdcarol0701'])
    elif s == 2:
        task_list = TaskList()
        task_list.add_task(JDDataSignTask)
        task_list.run_forever()

