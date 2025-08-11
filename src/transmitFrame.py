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

    # Initalization of frame and connection lock
    def __init__(self, master:ttk.Frame):
        super().__init__(master)
        self.transmit_sector(master)
        self.transmitting_data = Lock()

    ### GUI SETUP ###

    # Set up for GUI (calls required builder functions)
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

        option_list = ['Pick gain', '1','2','3','4','5','6','7']
        self.tx_gain = ttk.StringVar(value='1')
        self.transmit_file(section, self.tx_gain,option_list)

    # Create path browser row for GUI
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

    # Create textbox for server port/ip
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
    
    # Creates row to transmit file
    def transmit_file(self, master, stringVar, option_list):
        row = ttk.Frame(master)
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        run_btn = ttk.Button(
            master=row,
            text="Run",
            command=self.on_transmit_run,
            width=8
        )
        gain_options = ttk.OptionMenu(row, stringVar, *option_list, bootstyle= INFO, 
                                            command=self.on_typing)
        
        run_btn.pack(side=RIGHT, padx=3)
        gain_options.pack(side=RIGHT, padx=3)

    ### HANDLER FUNCTION ###

    # Handles when transmit button is pressed
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

        if not self.tx_gain.get().isdigit():
            return
        else:
            tx_gain = self.tx_gain.get()
        try:
            ipaddress.ip_address(self.ip_addr.get())
            server_ip = self.ip_addr.get()
        except ValueError:
            return
    
        print(f"Attempting to connect to:\tPort: {server_port}; ipaddr: {server_ip}")

        # Lock to prevent multiple connections to server at once
        if self.transmitting_data.acquire_lock(blocking=False):
            thread = Thread(target=self.handle_to_server, args=(server_ip, server_port, transmit_file, tx_gain))
            thread.daemon = True
            thread.start()
        else:
            print("Still transmitting data")
        
    # Handles connection/interactions with server
    def handle_to_server(self, server_ip, server_port, transmit_file, tx_gain):
        # Create TCP socket to connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO: Check if this is worth setting up
        client_socket.settimeout(5.0)
        
        try:
            # Try connecting to server
            client_socket.connect((server_ip, server_port))

            # Server will send data if it is busy at the moment (if it is, we stop)
            data = client_socket.recv(64).decode()
            if "Continue" == data:
                print("Can now write to server")

                # Get file size and gain for header
                file_size = os.path.getsize(transmit_file)
                header = str(file_size) + ";" + tx_gain
                print(f"Header: {header}")
                client_socket.sendall(header.encode())
                print(file_size)

                # Wait for server acknowledgement of header
                ack = client_socket.recv(64).decode()
                if ack != "Ok":
                    self.transmitting_data.release_lock()
                    return
                
                # Send over file data
                with open(transmit_file, "rb") as f:
                    bytes_sent = 0
                    while bytes_sent != file_size:

                        curr_sent = client_socket.sendfile(f)
                        if curr_sent == 0:
                            break
                        bytes_sent += curr_sent
                print(f"{bytes_sent}, {type(bytes_sent)}, {file_size}, {type(file_size)}")
                if bytes_sent != file_size:
                    print(f"File failed to send through properly; sent: {bytes_sent}")
                client_socket.shutdown(socket.SHUT_WR)
            else:
                print("Failed to connect")
        except Exception as E:
          print(f"Error {E}")
        finally:
            client_socket.close()
            self.transmitting_data.release_lock()
        
    # Pulls up file system for ease of locating file
    def on_file_browse(self, path_var):
        path = filedialog.askopenfilename(title="File Browse")
        if path:
            path_var.set(path)

    # Pulls up file system for ease of locating directory
    def on_folder_browse(self, path_var):
        path = filedialog.askdirectory(title="Folder Browse")
        if path:
            path_var.set(path)
    def on_typing(self, gain_var):
        self.tx_gain = ttk.StringVar(value=gain_var)