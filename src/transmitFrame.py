# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:58:35 2023

@author: lbryton
"""

# Basic libraries
from pathlib import Path
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
from tkinter import filedialog, messagebox

# Frame to transmit file through TCP/IP and run commands
class TransmitFrame(ttk.Labelframe):
    """
    Creates LabelFrame for transmitting file to server. The server will then interpret file as signal and transmit that signal
    """

    # Initalization of frame and connection lock
    def __init__(self, master:ttk.Frame):
        super().__init__(master, text="Transmit Signal")
        self.transmit_sector()
        self.transmitting_data = Lock()

    ### Frame/Widget Instantiation ###

    # Set up for GUI (calls required builder functions)
    def transmit_sector(self):
        """
        Fill in the Transmit frame to get port and IP address to send file over to
        """
        _path = Path().absolute().as_posix()
        self.file_type_var = ttk.StringVar(value='wav')

        # Add janus path row to labelframe 
        self.transmit_path_var = ttk.StringVar(value=_path)
        self.create_path_browser("Transmit File", self.transmit_path_var)

        self.ip_addr = ttk.StringVar(value="10.0.0.0")
        self.create_ip_addr("IP address", self.ip_addr)

        self.port_addr = ttk.StringVar(value="5000")
        self.create_ip_addr("Server Port", self.port_addr)

        option_list = ['Pick gain', '1','2','3','4','5','6','7']
        self.tx_gain = ttk.StringVar(value='1')
        self.transmit_file(self.tx_gain,option_list)

    # Create path browser row for GUI
    def create_path_browser(self, text, text_var):
        """
        Creates a frame row to capture input file (and directory)
        - text: Descriptor text of the row
        - text_var: Variable to store file/directory path
        - include_dir: Flag whether or not to include search for directory
        """
        # Instantiating widgets
        row = ttk.Frame(self)
        row_label = ttk.Label(row, text=text, width=15)
        row_entry = ttk.Entry(row, textvariable=text_var, width=10)
        
        file_btn = ttk.Button(
            master=row, 
            text="File", 
            command=lambda path_type=text_var: self.on_file_browse(path_type), 
            width=8
        )

        # Row orientation
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        row_label.pack(side=LEFT, padx=3)
        row_entry.pack(side=LEFT, fill=X, expand=YES, padx=3)
        file_btn.pack(side=LEFT, padx=3)
        return row_entry

    # Create textbox for server port/ip
    def create_ip_addr(self, text, text_var):
        """
        Creates a frame row to capture input port/ IP address
        - text: Descriptor text of the row
        - text_var: Variable to store text
        """
        # Instantiating widgets
        row = ttk.Frame(self)
        row_label = ttk.Label(row, text=text, width=15)
        row_entry = ttk.Entry(row, textvariable=text_var, width=10)
        
        # Row orientation
        row.pack(fill=X, expand=NO, anchor=N, pady=(0,5))
        row_label.pack(side=LEFT, padx=3)
        row_entry.pack(side=LEFT, fill=X, expand=YES, padx=3)
        return row_entry
    
    # Creates row to transmit file
    def transmit_file(self, stringVar, option_list):
        """
        Sets up row to run Janus demodulation and a guide on how to use the Janus frame
        - stringVar: 
        - option_list: Available options to pick from in a drop down menu
        """
        row = ttk.Frame(self)
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
        """
        Checks to make sure all input variables are valid, then creates a new thread to run file transmission
        """
        if os.path.isfile(self.transmit_path_var.get()) == False:
            self.show_message("Please provide a file to transmit")
            return
        else:
            transmit_file = self.transmit_path_var.get()

        try:
            ipaddress.ip_address(self.ip_addr.get())
            server_ip = self.ip_addr.get()
        except ValueError:
            self.show_message("IP address should be written as #.#.#.# with # ranging from 0 to 255")
            return
        except Exception as E:
            self.on_except(E)
            return
        
        if not self.port_addr.get().isdigit():
            self.show_message("Server port should be a digit")
            return
        else:
            server_port = int(self.port_addr.get())

        if not self.tx_gain.get().isdigit():
            self.show_message("Gain should be a digit")
            return
        else:
            tx_gain = self.tx_gain.get()
    
        print(f"Attempting to connect to:\tPort: {server_port}; ipaddr: {server_ip}")

        # Lock to prevent multiple connections to server at once
        if self.transmitting_data.acquire_lock(blocking=False):
            thread = Thread(target=self.handle_to_server, args=(server_ip, server_port, transmit_file, tx_gain))
            thread.daemon = True
            thread.start()
        else:
            self.show_message("Still transmitting data")
        
    # Pulls up file system for ease of locating file
    def on_file_browse(self, path_var):
        """
        Callback for file browse
        - path_var: the variable to update with the file path
        """
        path = filedialog.askopenfilename(title="File Browse")
        if path:
            path_var.set(path)

    # Pulls up file system for ease of locating directory
    def on_typing(self, gain_var):
        """
        Callback for updating gain
        - gain_var: The new gain value
        """
        self.tx_gain = ttk.StringVar(value=gain_var)

    ### Ran on seperate thread ###

    # Handles connection/interactions with server
    def handle_to_server(self, server_ip, server_port, transmit_file, tx_gain):
        """
        Comunicates with server for ability to send file. If possible, send file, and disconnect socket
        - server_ip: Server IP
        - server_port: Server Port
        - transmit_file: File to be transmitted and ran on server side
        - tx_gain: Gain of how strong the sever should transmit the TX wave
        """
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
                print("Writing to server")

                # Get file size and gain for header
                file_size = os.path.getsize(transmit_file)
                header = f"{file_size};{tx_gain}"
                client_socket.sendall(header.encode())

                # Wait for server acknowledgement of header
                ack = client_socket.recv(64).decode()
                if ack != "Ok":
                    # self.transmitting_data.release_lock()
                    return
                
                # Send over file data
                with open(transmit_file, "rb") as f:
                    bytes_sent = 0
                    while bytes_sent != file_size:

                        curr_sent = client_socket.sendfile(f)
                        if curr_sent == 0:
                            break
                        bytes_sent += curr_sent
                if bytes_sent != file_size:
                    self.show_message(f"File failed to send through properly; sent= {bytes_sent}; file size= {file_size}")
                client_socket.shutdown(socket.SHUT_WR)
            else:
                self.show_message("Server in use")
        except socket.timeout:
            self.show_message("Connection attempt failed. Issue - Timeout")
        except Exception as E:
            self.on_except(E)
        finally:
            client_socket.close()
            self.transmitting_data.release_lock()

    ### Error/message windows ###

    def show_message(self,msg = "Default message"):
        """
        Displays a message window with the provided string.
        """
        messagebox.showinfo("Information", msg)

    def on_except(self, E):
        """
        Displays an error window with the provided string.
        """
        messagebox.showerror("Error", str(E))