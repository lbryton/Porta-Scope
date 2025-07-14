# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:58:35 2023

@author: danie
"""

import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
from tkinter import messagebox
import sys
import matplotlib
matplotlib.use('TkAgg')
import datetime
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import binascii
# from untitled0 import *
from tkinter import filedialog


class FileSearchEngine(ttk.Frame):

    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.term_var = ttk.StringVar(value='md')
        self.type_var = ttk.StringVar(value='endswidth')
        self.cast_var = ttk.StringVar(value='uint16')


        # header and labelframe option container
        option_text = "Complete the form to begin your search"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row()
        self.create_go_row()
        self.create_demodulation_row()
        self.progressbar = ttk.Progressbar(
            master=self, 
            mode=INDETERMINATE, 
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row, 
            text="Browse", 
            command=self.on_browse, 
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_go_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Plot graph", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        #path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        #path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        make_btn = ttk.Button(
            master=path_row,
            text="Plot",
            command=self.Make,
            width=8
        )
        make_btn.pack(side=LEFT, padx=5)
        option_list = ['Pick a data type', 'uint16', 'int16', 'uint32']
        op = ttk.OptionMenu(self, self.cast_var, *option_list, command=self.on_typing)
        op.pack(side=RIGHT, padx=(15, 0))
    def create_demodulation_row(self):
        """Add term row to labelframe"""
        demod_row = ttk.Frame(self.option_lf)

    def on_typing(self, cast_var):
        """Callback for cast type"""
        self.cast_fn = getattr(np, cast_var)
        return
    
    def on_browse(self):
        """Callback for directory browse"""
        path = filedialog.askopenfilename(title="Browse")
        if path:
            self.path_var.set(path)

    def show_error(self, msg):
        messagebox.showerror("Error", msg)


    def Make(self):
        """Callback for plotting data"""

        a = ""
        teststring = []

        # file loader
        rx_data1 = None
        try:
            rx_data1 = np.loadtxt(self.path_var.get(), dtype=self.cast_var.get(), 
                              converters={_: lambda s: self.cast_fn(s) for _ in range(1)}, encoding="utf8")
        except ValueError as E:
            self.show_error(f"Failed to convert: {E}")
            return
        except IsADirectoryError as E:
            self.show_error(f"Path is a file: {E}")
            return
        except TypeError as E:
            self.show_error(f"Pick a data type")
            return

        for y in rx_data1:  # separates the bits into highs and lows
            if y < 1000:
                a += "0"
                teststring.append(0)
            else:
                a += "1"
                teststring.append(1)

        arr1 = list(range(0, len(rx_data1)))
        plt.figure()
        plt.plot(arr1, rx_data1)
        plt.show()
            
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.quit()
        app.destroy()
        
            
if __name__ == '__main__':

    app = ttk.Window("Porta-Scope", "solar")
    app.protocol("WM_DELETE_WINDOW", on_closing)
    FileSearchEngine(app)
    app.mainloop()
    sys.modules[__name__].__dict__.clear()

