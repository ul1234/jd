#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
from wx import Wx

TEMP_PATH = os.path.join(os.path.dirname(__file__), 'temp')

def print_(str, important = False):
    if important:
        print str
    else:
        print str

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
    _ = raw_input('pause...')
