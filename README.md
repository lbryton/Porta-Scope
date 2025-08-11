# Porta-Scope

A GUI that provides access to demodulation of Janus log files and transmission of `.wav` files. This GUI is build via ttkbootstrap and tkinter and handles heavier applications of the GUI on seperate threads.

## Running Locally

1. Clone the Repo
2. Install required libraries (`pip install -r requirements.txt`). Set up with `Python 3.9.6`.
3. Run Porta-Scope:

    * Windows: `python .\src\portaScope.py`
    * Linux: `python ./src/portaScope.py`
    * Apple: Same as Linux. Can do everything except run Janus demodulation
4. Create single file executables using `make linux` or `make windows` to make Linux and Windows executables respectively.

## File structure
```
Porta-Scope/
├── configs/                # Example Janus configurations for demodulation
├── porta-janus-lin/        # Contains Linux executable to run Janus demodulation
├── porta-janus-win/        # Contains Window exectuable to run Janus demodulation
├── sample_janus/           # Example expected Janus demodulation output
├── src/                    
│   ├── portaScope.py       # Main window for Porta-Scope. Handles window size and closure.
│   ├── janusFrame.py       # Sub window for demodulating Janus.
│   ├── transmitFrame.py    # Sub window for temporarily writing a file and transmitting it.
│
├── Socket/
│   ├── server.ipynb        # Simulation server to test Porta-Scope client-server interactions
│   ├── server.py           # Stored copy of deployed server
│
├── Makefile/               # Constructs single file executable for Porta-Scope
├── requirements.txt/       # Contains libraries to install
└── README.md               # This file
```