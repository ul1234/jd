#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import Tkinter as tk
from PIL import ImageTk, Image
from miscellaneous import *


root = tk.Tk(className = 'Captcha')
root.withdraw()

class CaptchaNotResolved(Exception):
    pass
    
class Captcha:
    def __init__(self, auto_resolve = False):
        save_path = get_save_path()
        self.temp_img_file = os.path.join(save_path, 'all_page.png')
        self.img_file = os.path.join(save_path, 'code.jpg')
        self.auto_resolve = auto_resolve

    def resolve(self, img_file = ''):
        return self.resolve_auto(img_file) if self.auto_resolve else self.resolve_manual(img_file)

    def resolve_auto(self, img_file = ''):
        raise Exception('TBD')

    def resolve_manual(self, img_file = ''):
        captcha_text = []
        image = Image.open(img_file or self.img_file)
        img = ImageTk.PhotoImage(image)
        identify = Identify(root, img, captcha_text)
        identify.mainloop()
        if not captcha_text: raise CaptchaNotResolved('no captcha resolved.')
        return captcha_text[0]

    def img(self, webdriver, img_element):
        location = img_element.location
        size = img_element.size
        webdriver.save_screenshot(self.temp_img_file)
        image = Image.open(self.temp_img_file)

        left, right = location['x'], location['x'] + size['width']
        top, bottom = location['y'], location['y'] + size['height']
        print (left, top, right, bottom)
        print location
        image = image.crop((left, top, right, bottom))
        image = image.convert('RGB')
        image.save(self.img_file)
        return self


class Identify(tk.Toplevel):
    def __init__(self, master, img, captcha_text):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.resizable(0, 0)

        self.label_img = tk.Label(self, image = img)
        self.edit = tk.Entry(self)
        self.label_img.pack(side = "top", fill = "both", expand = "yes")
        self.edit.pack(padx = 10, pady = 10)
        self.edit.focus_set()
        self.bind('<Return>', self.output_text)
        self.captcha_text = captcha_text

        self.geometry('+%d+%d' % (self.winfo_screenwidth()/2, self.winfo_screenheight()/2))

    def output_text(self, event):
        text = self.edit.get()
        if len(text) == 4:
            self.captcha_text.append(text)
            self.quit()

    def quit(self):
        self.destroy()
        tk.Toplevel.quit(self)


if __name__ == '__main__':
    print Captcha().resolve(r'temp/2361340.png')