# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:58:35 2023

@author: danie
"""

# Basic import libraries
import os
import sys

# Ploting
import matplotlib
matplotlib.use('TkAgg')

# TKinter imports
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Event as TKEvent, messagebox

# Frames
from janusFrame import JanusFrame
from transmitFrame import TransmitFrame

class PortaScope(ttk.Frame):
    """
    Creates 2x2 frame for transmitting and demodulating recieved signals
    """

    def __init__(self, master:ttk.Frame):
        super().__init__(master, padding=15)

        self.grid(row=0, column=0, sticky=NSEW)
        self.master = master 
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.prev_height = self.master.winfo_height()
        self.prev_width = self.master.winfo_width()
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

        # Janus frame
        # self.sections[1].config(text="Janus Demodulation")
        jF = JanusFrame(self)
        jF.grid(row=1, column=0, sticky=NSEW, padx=10, pady=10)
        self.sections.append(jF)

        # Transmit Frame
        tF = TransmitFrame(self)
        tF.grid(row=2, column=0, sticky=NSEW, padx=10, pady=10)
        self.sections.append(tF)

        # Used as filler, once actually filled, will remove
        for i in range(2,3):
            for j in range(2):
                frame = ttk.Labelframe(self, text=f"Default: Section {(i-1)*2 + j + 1}", padding=10)
                frame.grid(row=i, column=j, sticky=NSEW, padx=10, pady=10)
                self.sections.append(frame)

        # Bind configurations
        self.compact = False
        self.master.after_idle(lambda: self.master.bind("<Configure>", self.on_configure))
        self.master.after(50, lambda: self.update_height(self.master.winfo_width(), self.master.winfo_height()))

    def mini_sector(self):
        """
        Creates header for compact mode
        """
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
            text="Transmit",
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

    ### Call back functions ###

    def update_height(self, width, height):
        """
        Callback function when window size is updated. Updates to normal and compact mode when needed
        - width: Current width of window
        - height: Current height of window
        """
        if (width <= 775 or height <= 600):
            if not self.compact:
                if not self.sections[0].winfo_ismapped():
                    self.sections[0].grid(row=0,column=0, columnspan=2, sticky="ew",padx=10, pady=10)

                for i in range(1,5):
                    if self.sections[i].winfo_ismapped() and self.current_selection != i:
                        self.sections[i].grid_remove()
                    else:
                        self.sections[i].grid(row=1, column=0, sticky=NSEW, columnspan=2, rowspan=2)
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

    def select_window(self, select_window):
        """
        Call back function for selecting the window displayed in compact mode
        - select_window: Window selected to be displayed
        """
        if self.current_selection == select_window:
            return

        if self.sections[self.current_selection].winfo_ismapped():
            self.sections[self.current_selection].grid_remove()

        self.sections[select_window].grid(
            row=1, column=0, sticky=NSEW, columnspan=2, rowspan=2
        )
        self.current_selection = select_window

        # Force the GUI to refresh
        self.update_idletasks()
        self.update()

    ### Handler functions ###

    def on_configure(self, event:TKEvent):
        """
        Event handler when the window is updated. Currently looks only for width and height changes
        - event: All of the events of the Frame
        """
        # Check if the event comes from the window
        if event.widget == self.master:
            
            # Check if the height/width is updated
            if event.widget.winfo_width() != self.prev_width or event.widget.winfo_height() != self.prev_height:
                self.prev_height = event.widget.winfo_height()
                self.prev_width = event.widget.winfo_width()
                self.update_height(self.prev_width, self.prev_height)
            
def on_closing():
    """
    Callback when escaping program
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.quit()
        app.destroy()


if __name__ == '__main__':
    """
    Runs program from main
    """
    app = ttk.Window("Porta-Scope", "solar")
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.geometry("%dx%d" % (600, 600))

    app.bind("<Escape>", lambda e: on_closing())

    PortaScope(app)
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


