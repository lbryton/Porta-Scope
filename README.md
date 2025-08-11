# Porta-Scope
Portable Oscilloscope based off of input 

```
Porta-Scope/
├── configs/                # Example Janus configurations for demodulation
├── src/                    # 
│   ├── portaScope.py       # Main window for Porta-Scope. Handles window size and closure.
│   ├── janusFrame.py       # Sub window for demodulating Janus.
│   ├── transmitFrame.py    # Sub window for temporarily writing a file and transmitting it.
├── porta-janus-lin/        # Contains Linux executable to run Janus demodulation
├── porta-janus-win/        # Contains Window exectuable to run Janus demodulation
└── README.md            # This file
```