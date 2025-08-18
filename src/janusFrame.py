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
from tkinter import filedialog, messagebox


class JanusFrame(ttk.Labelframe):
    """
    Creates LabelFrame for Janus demodulation
    """

    # Initalization of frame and connection lock
    def __init__(self, master:ttk.Frame):
        super().__init__(master, text="Janus Demodulation")
        self.progress_bar = None
        self.janus_sector()
        self.processing_janus = Lock()

    ### Frame/Widget Instantiation ###

    def janus_sector(self):
        """
        Fill in the Janus frame to get Janus file/directory to read, config file, parameter file, output file, and the input file type
        """
        _path = Path().absolute().as_posix()
        self.file_type_var = ttk.StringVar(value='wav')


        # Add janus path row to labelframe 
        self.janus_path_var = ttk.StringVar(value=_path)
        self.create_path_browser("Janus Path (file/dir)", self.janus_path_var, include_dir=True)
        

        # # Add config path row to labelframe 
        self.config_path_var = ttk.StringVar(value=_path)
        self.create_path_browser("Config Path", self.config_path_var)

        # Add parameter_sets path row to labelframe
        self.pset_path_var = ttk.StringVar(value=_path)
        self.create_path_browser("Parameter Path", self.pset_path_var)

        # CSV Output location and file picker
        self.csv_path_var = ttk.StringVar(value=_path)
        self.create_path_browser("CSV Output Path", self.csv_path_var)

        option_list = ['Pick a file type', 'raw', 'wav','wmm']
        self.file_type_run(option_list)

        self.create_progress()

    def create_path_browser(self, text, text_var, include_dir=False):
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

    def file_type_run(self, option_list):
        """
        Sets up row to run Janus demodulation and a guide on how to use the Janus frame
        - option_list: Available options to pick from in a drop down menu
        """
        # Instantiating widgets
        row = ttk.Frame(self)
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
            command=self.on_help, 
            width=8
        )
        # Row orientation
        parameter_btn.pack(side=RIGHT, padx=3)
        parameter_options.pack(side=RIGHT, padx=3)
        help_btn.pack(side=RIGHT, padx=3)

    def create_progress(self):
        """
        Sets up a hotbar when running a directory of files
        """
        row = ttk.Frame(self)
        row.pack(fill=X, expand=YES, anchor=S, pady=(0,5), padx=(5,5))
        self.progress_bar = ttk.Progressbar(master=row, mode="determinate", maximum=100, value=0)
        self.progress_bar.pack(fill=X, expand=YES)
        # print(self.progress_bar.cget("maximum"))

    def update_progress(self, percent):
        """
        Updates progress bar when Janus is working on multiple files
        - percent: The total progress of Janus demodulation anging from 0 to 1 (inclusive)
        """
        if percent <= self.progress_bar.cget("maximum") and percent >= 0:
            self.progress_bar["value"] = percent * self.progress_bar.cget("maximum")
    ### Call Back Functions ###

    def on_help(self):

        config_flags = ["--verbose: Verbose level", "--pset-id: Parameter Set Identifier", "--chip-len-exp: Chip Length Dyadic Exponent", "--sequence-32-chips: Initial sequence of 32 chips (hex)",
                        "--stream-fs: Stream Sampling Frequency (Hz)", "--stream-format: Stream Format", "--stream-channels: Stream Channels configuration", "--stream-channel: Stream Active Channel",
                        "--stream-passband: Stream Passband signal", "--doppler-correctionEnabled/Disabled Doppler Correction", "--doppler-max-speed: Doppler Correction Maximum Speed [m/s]",
                        "--detection-threshold: Detection threshold", "--colored-bit-probabilities Enable/Disable Colored Bit Probabilities", "--cbp-high2medium: CBP High to Medium Threshold", 
                        "--cbp-medium2low: CBP Medium to Low Threshold"]
        config_lines = "- Config Path: Path to Janus configuration path (each seperated by a newline)"
        for flag in config_flags:
            config_lines += f"\n    {flag}"
        parameter_set_lines = "- Parameter Path: Path to Janus parameter set path (each seperated by a newline). Header is in the csv format of:\n    - \"# Id, Center Frequency (Hz), Bandwidth (Hz), Name\""
        self.show_message(f"How to demodulate Janus file(s):\n- Janus Path: File or directory holding files to demodulate\n{config_lines}\n{parameter_set_lines}")

    def on_file_browse(self, path_var):
        """
        Callback for file browse
        - path_var: the variable to update with the file path
        """
        path = filedialog.askopenfilename(title="File Browse")
        if path:
            path_var.set(path)

    def on_folder_browse(self, path_var):
        """
        Callback for directory browse
        - path_var: the variable to update with the directory path
        """
        path = filedialog.askdirectory(title="Folder Browse")
        if path:
            path_var.set(path)

    def on_janus_run(self):
        """
        Checks to make sure all input variables are valid, then creates a new thread to run Janus demodulation
        """
        # Check if we have a config file
        if os.path.isdir(self.config_path_var.get()) or not self.config_path_var.get().endswith('.conf'):
            self.show_message("Please pick an config file with .conf")
            return
        
        # Check if we have a parameter set file
        if os.path.isdir(self.pset_path_var.get()) or not self.pset_path_var.get().endswith('.csv'):
            self.show_message("Please pick an parameter set with .csv")
            return
        
        # Check if we have an output file
        if os.path.isdir(self.csv_path_var.get()) or not self.csv_path_var.get().endswith('.csv'):
            self.show_message("Please pick an output file with .csv")
            return
        
        # Check if we have 
        if not isinstance(self.file_type_var, str):
            self.show_message("Please pick a file type")
            return
        
        if not self.processing_janus.acquire_lock(blocking=False):
            self.show_message("Still processing")
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
            
    def janus_out(self, result:str, file_name, out_csv):
        """
        Post processing of Janus RX to look for payload and SNR
        - result: Janus RX executable output (from stderr)
        - file_name: Input Janus file name
        - out_csv: Output (.csv) file to store results
        """
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

    def on_typing(self, file_type_var):
        """
        Handler to update file variable
        """
        self.file_type_var = file_type_var

    ### Ran on seperate thread ###

    def run_subprocess(self, exe_path, janus_path, pset_path, file_type, config_path, csv_path):
        """
        Function to run on a new thread for Janus demodulation
        - exe_path: Path to Janus executable
        - janus_path: File/directory path to Janus RX files
        - pset_path: File path to parameter (.csv) file
        - file_type: File type of Janus RX files
        - config_path: File path to config (.conf) file
        - csv_path: File path to output (.csv) file
        """
        try:
            if os.path.isdir(janus_path):
                folder = Path(janus_path)
                wav_files = list(folder.glob(f"*.{file_type}"))
                total_files = len(wav_files)
                print(total_files)

                for i in range(total_files):
                    run_arr = [exe_path, 
                        "--pset-file", str(pset_path),
                        "--config-file", str(config_path),
                        "--stream-driver", str(file_type),
                        "--stream-driver-args", str(wav_files[i])
                                ] 
                    result = subprocess.run(run_arr, 
                                        capture_output=True, text=True)
                    if result.returncode == 0:
                        # print(result.stderr)
                        # print(result.stdout)
                        self.janus_out(result.stderr, os.path.basename(wav_files[i]), csv_path)
                    else:
                        print(result.returncode)
                        print("error: \n", result.stderr)
                    self.update_progress((i+1)/total_files)
            elif os.path.isfile(janus_path):
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
                self.update_progress(1)
        except Exception as E: 
            self.on_except(E)
        finally:
            self.processing_janus.release_lock()
            # print("done")

    ### Error/message windows ###

    def show_message(self,msg="Default message"):
        """
        Displays a message window with the provided string.
        """
        messagebox.showinfo("Information", msg)

    def on_except(self, E):
        """
        Displays an error window with the provided string.
        """
        messagebox.showerror("Error", str(E))

