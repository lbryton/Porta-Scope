# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:58:35 2023

@author: lbryton
"""

# Basic libraries
from pathlib import Path
import sys
import subprocess
import os
import socket
import ipaddress



# Threading/Concurrency Libraries
from threading import Thread, Lock

# Plotting library
import matplotlib
matplotlib.use('TkAgg')

# TKinter Libraries
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog

# Frame to transmit file through TCP/IP and run commands
class TransmitFrame(ttk.Labelframe):
    def __init__(self, master:ttk.Frame):
        super().__init__(master)
        self.transmit_sector(master)
        self.transmitting_data = Lock()

    def transmit_sector(self, section):
        _path = Path().absolute().as_posix()
        self.file_type_var = ttk.StringVar(value='wav')

        # Add janus path row to labelframe 
        self.transmit_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "Transmit File", self.transmit_path_var)

        self.ip_addr = ttk.StringVar(value="10.0.0.0")
        self.create_ip_addr(section, "IP address", self.ip_addr)

        self.port_addr = ttk.StringVar(value="5000")
        self.create_ip_addr(section, "Server Port", self.port_addr)

        self.transmit_file(section)

    def create_path_browser(self, master, text, text_var, include_dir=False):
        # Instantiating widgets
        row = ttk.Frame(master)
        row_label = ttk.Label(row, text=text, width=15)
        row_entry = ttk.Entry(row, textvariable=text_var, width=10)
        
        file_btn = ttk.Button(
            master=row, 
            text="File", 
            command=lambda path_type=text_var: self.on_file_browse(path_type), 
            width=8
        )
        if include_dir:
            dir_btn = ttk.Button(
            master=row, 
            text="Folder", 
            command=lambda path_type=text_var: self.on_folder_browse(path_type), 
            width=8
        )
        # Row orientation
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        row_label.pack(side=LEFT, padx=3)
        row_entry.pack(side=LEFT, fill=X, expand=YES, padx=3)
        file_btn.pack(side=LEFT, padx=3)
        if include_dir:
            dir_btn.pack(side=LEFT, padx=3)
        return row_entry

    def create_ip_addr(self, master, text, text_var):
        # Instantiating widgets
        row = ttk.Frame(master)
        row_label = ttk.Label(row, text=text, width=15)
        row_entry = ttk.Entry(row, textvariable=text_var, width=10)
        
        # Row orientation
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        row_label.pack(side=LEFT, padx=3)
        row_entry.pack(side=LEFT, fill=X, expand=YES, padx=3)
        return row_entry
    
    def transmit_file(self, master):
        row = ttk.Frame(master)
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        run_btn = ttk.Button(
            master=row,
            text="Run",
            command=self.on_transmit_run,
            width=8
        )
        run_btn.pack(side=RIGHT, padx=3)

    def on_transmit_run(self):
      # File checking and checking if ports are fine
      if os.path.isfile(self.transmit_path_var.get()) == False:
          return
      else:
        transmit_file = self.transmit_path_var.get()
      if not self.port_addr.get().isdigit():
          return
      else:
          server_port = int(self.port_addr.get())
      try:
          ipaddress.ip_address(self.ip_addr.get())
          server_ip = self.ip_addr.get()
      except ValueError:
          return
    
      print(f"Attempting to connect to:\tPort: {server_port}; ipaddr: {server_ip}")
      if self.transmitting_data.acquire_lock(blocking=False):
          thread = Thread(target=self.handle_to_server, args=(server_ip, server_port, transmit_file))
          thread.start()
      else:
          print("Still transmitting data")
    
    def handle_to_server(self, server_ip, server_port, transmit_file):
        # Create TCP socket to connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO: Check if this is worth setting up
        # client_socket.settimeout(5.0)
        try:
            # Try connecting to server
            client_socket.connect((server_ip, server_port))

            # Server will send data if it is busy at the moment (if it is, we stop)
            data = client_socket.recv(1024).decode()
            if "Continue" == data:
                print("Can now write to server")
                # TODO: Handle when bytes sent is not the actual file size
                with open(transmit_file, "rb") as f:
                    
                    bytes_sent = client_socket.sendfile(f)

                client_socket.shutdown(socket.SHUT_WR)
            else:
                print("Failed to connect")
        except Exception as E:
          print(f"Error {E}")
        finally:
            client_socket.close()
            self.transmitting_data.release_lock()
        

    def on_file_browse(self, path_var):
        """Callback for directory browse"""
        path = filedialog.askopenfilename(title="File Browse")
        if path:
            path_var.set(path)
    def on_folder_browse(self, path_var):
        """Callback for directory browse"""
        path = filedialog.askdirectory(title="Folder Browse")
        if path:
            path_var.set(path)