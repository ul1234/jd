# encoding=utf-8

import Tkinter as tk
from PIL import ImageTk, Image

root = tk.Tk(className = 'Captcha')
root.withdraw()

def manual_captcha(img_file):
    captcha_text = []    
    image = Image.open(img_file)
    img = ImageTk.PhotoImage(image)
    identify = Identify(root, img, captcha_text)
    identify.mainloop()
    return captcha_text[0]


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
    manual_captcha(r'../temp/2361340.png')