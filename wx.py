#!/usr/bin/python
# -*- coding: utf-8 -*-

from wxpy import *

class Wx:
    def __init__(self):
        self.bot = Bot(cache_path = True, console_qr = True)
        self.main_friend = ensure_one(self.bot.friends().search('shouliang'))
        self.msg_handler = None

    def msg_start(self, text):
        self.msg_save = ''

    def msg_interm(self, text):
        self.msg_save += text + '\n'

    def msg_end(self, text = ''):
        self.msg_save += text + '\n'
        self.msg(self.msg_save)
        self.msg_save = ''

    def msg(self, text):
        _ = self.bot.file_helper.send(text)

    def log(self, text):
        self.msg(text)

    def install_msg_handler(self, func):
        self.msg_handler = func

    #@self.bot.register(self.main_friend)
    def deal_msg(self, msg):
        text = msg.text
        if text.strip().lower().endswith('bot'):
            msg.forward(self.bot.file_helper, prefix='Bot:')
            if self.msg_handler: self.msg_handler(msg)

    def run_forever(self):
        embed()
        #self.bot.join()
