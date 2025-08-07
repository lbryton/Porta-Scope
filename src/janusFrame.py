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



# Threading/Concurrency Libraries
from threading import Thread, Lock

# Plotting library
import matplotlib
matplotlib.use('TkAgg')

# TKinter Libraries
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog


class JanusFrame(ttk.Labelframe):
    def __init__(self, master:ttk.Frame):
        super().__init__(master)
        self.janus_sector(master)
        self.processing_janus = Lock()


    def janus_sector(self, section):
        _path = Path().absolute().as_posix()
        self.file_type_var = ttk.StringVar(value='wav')


        # Add janus path row to labelframe 
        self.janus_path_var = ttk.StringVar(value=_path)
        self.create_path_browser(section, "Janus Path (file/dir)", self.janus_path_var, include_dir=True)
        

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

    def on_janus_run(self):
        if os.path.isdir(self.csv_path_var.get()) or not self.csv_path_var.get().endswith('.csv'):
            print("Please pick an output file with .csv")
            return
        if not isinstance(self.file_type_var, str):
            print("Please pick a file type")
            return
        if not self.processing_janus.acquire_lock(blocking=False):
            print("still processing")
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

        thread = Thread(target=self.run_subprocess,
                        args=(exe_path, self.janus_path_var.get(), 
                                self.pset_path_var.get(), self.file_type_var, 
                                self.config_path_var.get(), self.csv_path_var.get()))
        thread.start()
            
    def run_subprocess(self, exe_path, janus_path, pset_path, file_type, config_path, csv_path):
        try:
            if os.path.isdir(janus_path):
                print("test1")
                folder = Path(janus_path)  # or just 'path/to/folder'
                wav_files = list(folder.glob('*.wav'))
                print(len(wav_files))
                for wav_file in wav_files:
                    run_arr = [exe_path, 
                        "--pset-file", str(pset_path),
                        "--config-file", str(config_path),
                        "--stream-driver", str(file_type),
                        "--stream-driver-args", str(wav_file)
                                ] 
                    result = subprocess.run(run_arr, 
                                        capture_output=True, text=True)
                    if result.returncode == 0:
                        self.janus_out(result.stderr, os.path.basename(wav_file), csv_path)
                    else:
                        print(result.returncode)
                        print("error: \n", result.stderr)
            elif os.path.isfile(janus_path):
                print("test2")
                run_arr = [exe_path, 
                "--pset-file", str(pset_path),
                "--config-file", str(config_path),
                "--stream-driver", str(file_type),
                "--stream-driver-args", str(janus_path)
                        ]
                result = subprocess.run(run_arr, 
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    self.janus_out(result.stderr, os.path.basename(janus_path), csv_path)
                else:
                    print(result.returncode)
                    print("error: \n", result.stderr)
        except Exception as E: 
            print(E)
        finally:
          self.processing_janus.release_lock()
          print("done")

    def janus_out(self, result:str, file_name, out_csv):
        in_payload = 0
        detect_time = 0.0
        with open(out_csv, "a+") as file:
            # determine whether to write file is new or already has data
            file.seek(0)
            contents = file.read()
            if not contents:
                file.write("File,Detect,payload time,payload,payload size,snr,error\n")

            # Setting up parameters
            in_payload = False
            detect_time = ""
            payload_time = ""
            payload_data = ""
            payload_size = ""
            snr = ""
            janout = result.split("\n")

            # Iterates through data
            for line in janout:
                payload_cnt = 0
                if line.startswith('-> Triggering detection'):
                    if in_payload and payload_data != "":
                        file.write(f"{file_name},{str(detect_time)},{payload_time},{payload_data},{payload_size},{snr}\n")
                        payload_data = ""
                        payload_size = ""
                        snr = ""
                        payload_cnt += 1
                    elif in_payload:
                        file.write(f"{file_name},{str(detect_time)},,,,{snr},No data\n")
                    detect_time = line.split(" ")[3][1:-1]
                    in_payload = True

                elif in_payload:
                    if "SNR" in line:
                        snr = line.split(":")[2][1:]
                    elif "After (s)" in line:
                        payload_time = line.split(":")[2][1:]
                    elif "Payload Size" in line:
                        payload_size = line.split(":")[2][1:]
                    elif "Payload" in line:
                        payload_data = line.split(":")[2][1:]
            
            if in_payload:
                if payload_data != "":
                    file.write(f"{file_name},{str(detect_time)},{payload_time},{payload_data},{payload_size},{snr}\n")
                else:
                    file.write(f"{file_name},{str(detect_time)},,,,{snr},No data\n")
    # Callback for updating file type
    def on_typing(self, file_type_var):
        self.file_type_var = file_type_var