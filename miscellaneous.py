#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
import wx
from datetime import datetime
import pprint
import HTMLParser

TEMP_PATH = os.path.join(os.path.dirname(__file__), 'temp')

print_buffer = ''

html_parser = None

def unescape(html):
    global html_parser
    if not html_parser: html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(html)

def p_(str):
    pprint.pprint(str)

def print_(str, info = False, output_time = False):
    global print_buffer
    time_str = '[%s]' % datetime.now().strftime('%H:%M:%S') if output_time else ''
    str_ = '%s%s' % (time_str, str)
    print str_
    if info: print_buffer += '%s\n' % str_.strip()

def print_flush():
    global print_buffer
    wx.msg(print_buffer)
    print_buffer = ''
    
def chinese(word):
    return word.decode('utf-8')

def get_save_path():
    if not os.path.isdir(TEMP_PATH): os.makedirs(TEMP_PATH)
    return TEMP_PATH

def clear_save():
    clear_postfix = ['.html', '.png', '.jpg']
    folder = get_save_path()
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f)[-1] in clear_postfix]
    for f in files:
        os.remove(f)
    print_('clear all [%d] temp files!' % len(files))

def html_contents(html, start_tag, end_tag):
    if start_tag.endswith('>'):
        pattern = '%s(.*?)%s' % (start_tag, end_tag)
    else:
        pattern = '%s[^>]*>(.*?)%s' % (start_tag, end_tag)
    #print 'pattern:', pattern
    #print re.findall(pattern, html, re.MULTILINE|re.DOTALL)
    return re.findall(pattern, html, re.MULTILINE|re.DOTALL)

def html_content(html, start_tag, end_tag):
    return html_contents(html, start_tag, end_tag)[0]

def html_attributes(html, start_tag, attr):
    pattern = '%s[^>]*%s=["\']([^"\']*)["\']' % (start_tag, attr)
    #print pattern
    return re.findall(pattern, html, re.MULTILINE|re.DOTALL)

def html_attribute(html, start_tag, attr):
    return html_attributes(html, start_tag, attr)[0]

def pause():
    c = raw_input('pause... (Press g for pdb, others continue)')
    if c == 'g':
        import ipdb
        ipdb.set_trace()
    
def print_element(element):
    p_('The outerHTML of element:')
    p_(element.get_attribute('outerHTML'))
