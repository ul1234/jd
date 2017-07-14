#!/usr/bin/python
# -*- coding: utf-8 -*-

from wxpy import *

class Wx:
    def __init__(self):
        self.bot = Bot(cache_path = True, console_qr = True)
        self.main_friend = ensure_one(self.bot.friends().search('shouliang'))
        
    def msg(self, text):
        _ = self.bot.file_helper.send(text)
        
    @self.bot.register(self.main_friend)
    def deal_msg(self, msg):
        text = msg.text
        if text.strip().lower().endswith('bot'):
            msg.forward(self.bot.file_helper, prefix='Bot:')
            
    def run_forever(self):
        embed()
        #self.bot.join()
    