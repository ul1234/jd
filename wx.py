#!/usr/bin/python
# -*- coding: utf-8 -*-

from wxpy import *

bot = None
main_friend = None
msg_handler = None

def init():
    global bot, main_friend
    bot = Bot(cache_path = True, console_qr = True)
    main_friend = ensure_one(bot.friends().search('shouliang'))
    deal_msg = bot.register(main_friend)(deal_msg)

def msg(text):
    if bot:
        _ = bot.file_helper.send(text)

def install_msg_handler(func):
    global msg_handler
    msg_handler = func

#@bot.register(main_friend)
def deal_msg(msg):
    text = msg.text
    if text.strip().lower().endswith('bot'):
        msg.forward(bot.file_helper, prefix='Bot:')
        if msg_handler: msg_handler(msg)

def run_forever():
    embed()
    #bot.join()
