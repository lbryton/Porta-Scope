# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:58:35 2023

@author: danie
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
from tkinter import messagebox, filedialog
from tkinter import Event as TKEvent
from tkinter.filedialog import askdirectory

import datetime
import pathlib
from queue import Queue
from threading import Thread
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

import subprocess
import os
import platform


class JanusKey(ttk.Frame):
    queue = Queue()
    searching = False

    def __init__(self, master:ttk.Frame):
        super().__init__(master, padding=15)

        self.grid(row=0, column=0, sticky=NSEW)
        self.master = master 
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.prev_height = self.master.winfo_height()
        self.prev_width = self.master.winfo_width()
        self.cnt = 0
        self.current_selection = 1

        # Setup 2x2 grid inside this frame + header on 
        # top when decreasing window size
        self.rowconfigure(0, weight=0)
        for r in range(1,3):
            self.rowconfigure(r, weight=1, uniform='section')
        for c in range(2):
            self.columnconfigure(c, weight=1, uniform='section')

        # Fill grid with frames + default names
        self.sections = []
        header_frame = self.mini_sector()
        self.sections.append(header_frame)
        for i in range(1,3):
            for j in range(2):
                frame = ttk.Labelframe(self, text=f"Default: Section {(i-1)*2 + j + 1}", padding=10)
                frame.grid(row=i, column=j, sticky=NSEW, padx=10, pady=10)
                self.sections.append(frame)

        # Janus frame
        self.sections[1].config(text="Janus Demodulation")
        self.janus_sector(self.sections[1])
        self.compact = False

        # Bind configurations
        self.master.after_idle(lambda: self.master.bind("<Configure>", self.on_configure))
        self.master.after(50, lambda: self.update_height(self.master.winfo_width(), self.master.winfo_height()))



    def mini_sector(self):
        sector_row = ttk.Frame(self)
        sector_row.grid(row=0,column=0, columnspan=2, sticky="ew",padx=10, pady=5)
        sector_row.columnconfigure(0, weight=1)

        # Buttons to swap between each window
        janus_btn = ttk.Button(
            master=sector_row,
            text="Janus",
            command=lambda path_type=1: self.select_window(path_type),
            width=8
        )
        default2_btn = ttk.Button(
            master=sector_row,
            text="Default2",
            command=lambda path_type=2: self.select_window(path_type),
            width=8
        )
        default3_btn = ttk.Button(
            master=sector_row,
            text="Default3",
            command=lambda path_type=3: self.select_window(path_type),
            width=8
        )
        default4_btn = ttk.Button(
            master=sector_row,
            text="Default4",
            command=lambda path_type=4: self.select_window(path_type),
            width=8
        )
        default4_btn.pack(side=RIGHT, padx=3)
        default3_btn.pack(side=RIGHT, padx=3)
        default2_btn.pack(side=RIGHT, padx=3)
        janus_btn.pack(side=RIGHT, padx=3)
        sector_row.grid_remove()
        
        return sector_row

    ### Creating Frames in each section of the grid ###
    def janus_sector(self, section):
        _path = pathlib.Path().absolute().as_posix()
        self.file_type_var = ttk.StringVar(value='wav')


        # Add janus path row to labelframe 
        self.janus_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "Janus Path (file/dir)", self.janus_path_var)
        

        # # Add config path row to labelframe 
        self.config_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "Config Path", self.config_path_var)

        # Add parameter_sets path row to labelframe
        self.pset_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "Parameter Path", self.pset_path_var)

        # CSV Output location and file picker
        self.csv_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "CSV Output Path", self.csv_path_var)

        option_list = ['Pick a file type', 'raw', 'wav','wmm']
        self.file_type_run(section, option_list)
    
    ## Helper functions ##

    # Creates path browser pack row
    def create_path_browser(self, master, text, text_var):
        # Instantiating widgets
        row = ttk.Frame(master)
        row_label = ttk.Label(row, text=text, width=15)
        row_entry = ttk.Entry(row, textvariable=text_var, width=10)
        
        row_btn = ttk.Button(
            master=row, 
            text="Browse", 
            command=lambda path_type=text_var: self.on_path_browse(path_type), 
            width=8
        )
        # Row orientation
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        row_label.pack(side=LEFT, padx=3)
        row_entry.pack(side=LEFT, fill=X, expand=YES, padx=3)
        row_btn.pack(side=LEFT, padx=3)
        return row_entry
    
    # Setup buttons to actually run janus
    def file_type_run(self, master, option_list):
        # Instantiating widgets
        row = ttk.Frame(master)
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        parameter_options = ttk.OptionMenu(row, self.file_type_var, 
                                            *option_list, bootstyle= INFO, 
                                            command=self.on_typing)
        parameter_btn = ttk.Button(
            master=row, 
            text="Run", 
            command=self.on_janus_run, 
            width=8
        )
        help_btn = ttk.Button(
            master=row, 
            text="Help", 
            command=None, 
            width=8
        )
        # Row orientation
        parameter_btn.pack(side=RIGHT, padx=3)
        parameter_options.pack(side=RIGHT, padx=3)
        help_btn.pack(side=RIGHT, padx=3)

    def update_height(self, width, height):
        if (width <= 775 or height <= 600):
            if not self.compact:
                if not self.sections[0].winfo_ismapped():
                    self.sections[0].grid(row=0,column=0, columnspan=2, sticky="ew",padx=10, pady=10)
                self.sections[1].grid(row=1, column=0, sticky=NSEW, columnspan=2, rowspan=2)
                if self.sections[2].winfo_ismapped():
                    self.sections[2].grid_remove()
                if self.sections[3].winfo_ismapped():
                    self.sections[3].grid_remove()
                if self.sections[4].winfo_ismapped():
                    self.sections[4].grid_remove()
                self.compact = True

                # Force the GUI to refresh
                self.update_idletasks()
        elif self.compact:

            for i in range(5):
                if self.sections[i].winfo_ismapped():
                    self.sections[i].grid_remove()
            for i in range(4):
                self.sections[i+1].grid(row=i%2+1, column=i//2, columnspan=1, rowspan=1, sticky=NSEW, padx=10, pady=10)
            self.compact= False
        
            # Force the GUI to refresh
            self.update_idletasks()
        # self.update()

            

            # if not self.sections[2].winfo_ismapped():
            #     self.sections[2].grid(row=1, column=1, sticky=NSEW, padx=10, pady=10)
            # if not self.sections[3].winfo_ismapped():
            #     self.sections[3].grid(row=2, column=0, sticky=NSEW, padx=10, pady=10)
            # if not self.sections[4].winfo_ismapped():
            #     self.sections[4].grid(row=2, column=1, sticky=NSEW, padx=10, pady=10)

    ### Call back functions ###

    # Call back for any window events
    def on_configure(self, event:TKEvent):
        # Check if the event comes from the window
        if event.widget == self.master:
            # Check if the height/width is updated
            if event.widget.winfo_width() != self.prev_width or event.widget.winfo_height() != self.prev_height:
                self.current_selection = 1
                print(f"size_update {self.cnt}")
                self.cnt += 1
                self.prev_height = event.widget.winfo_height()
                self.prev_width = event.widget.winfo_width()
                self.update_height(self.prev_width, self.prev_height)

    # Call back to update selected window when in compact mode
    def select_window(self, select_window):
        if self.current_selection == select_window:
            return
        print(select_window)

        if self.sections[self.current_selection].winfo_ismapped():
            self.sections[self.current_selection].grid_remove()

        self.sections[select_window].grid(
            row=1, column=0, sticky=NSEW, columnspan=2, rowspan=2
        )
        self.current_selection = select_window

        # Force the GUI to refresh
        self.update_idletasks()
        self.update()


    # Callback for path browsing
    def on_path_browse(self, path_var):
        """Callback for directory browse"""
        path = filedialog.askopenfilename(title="Browse")
        if path:
            path_var.set(path)

    # Callback for updating file type
    def on_typing(self, file_type_var):
        self.file_type_var = file_type_var
            
    # Call back to run janus
    def on_janus_run(self):
        if not isinstance(self.file_type_var, str):
            print("Please pick a file type")
            return

        # Path to the C executable bundled with your Python app
        if getattr(sys, 'frozen', False):
            # When bundled by PyInstaller, files go into a special temp folder (_MEIPASS)
            base_path = sys._MEIPASS

            # Executable dependent on device
            if os.name == 'posix':
                exe_path = os.path.join(base_path, 'janus-rx')
            elif os.name == 'nt':
                exe_path = os.path.join(base_path, 'janus-rx.exe')
        else:
            # Running as normal python script (not bundled)
            if os.name == 'posix':
                exe_path = './porta-janus-lin/janus-rx'
            elif os.name == 'nt':
                exe_path = './porta-janus-win/janus-rx.exe'
        run_arr = [exe_path, 
                    "--pset-file", str(self.pset_path_var.get()),
                    "--config-file", str(self.config_path_var.get()),
                    "--stream-driver", str(self.file_type_var),
                    "--stream-driver-args", str(self.janus_path_var.get())
                  ]
        result = subprocess.run(run_arr, 
                                capture_output=True, text=True)
        if result.returncode == 0:
            self.janus_out(result.stderr)
        else:
            print(result.returncode)
            print("error: \n", result.stderr)
    def janus_out(self, result:str):
        in_payload = 0
        data = ""
        detect_time = 0.0
        with open("example.csv", "w") as file:
            janout = result.split("\n")
            file.write("Timestamp,payload,error,SINR\n")
            for line in janout:
                print(line)
                if line.startswith('-> Triggering detection'):
                    detect_time = line.split(" ")[3][1:-1]
                    in_payload = 1
                if in_payload and line.find("Application Data") != -1:
                    data = line.split(":")[2][1:]
                    file.write(f"{str(detect_time)},{data}\n")
                    in_payload = 0




def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.quit()
        app.destroy()

if __name__ == '__main__':
    app = ttk.Window("Porta-Scope", "solar")
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.geometry("%dx%d" % (600, 600))

    app.bind("<Escape>", lambda e: on_closing())

    JanusKey(app)
    app.update_idletasks()

    if os.name == 'posix':
        if os.uname().machine.lower() == 'arm64':
            app.after(100, lambda: app.state("zoomed"))
            app.minsize(600,600)
        else:
            app.after(100, lambda: app.wm_attributes("-zoomed", True))
    elif os.name == 'nt':
        app.after(100, lambda: app.state("zoomed"))
        app.minsize(600,600)
    app.mainloop()

    sys.modules[__name__].__dict__.clear()


