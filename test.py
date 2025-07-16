import tkinter as tk
from ttkbootstrap import Window

app = Window(themename="darkly")
app.minsize(600, 600)             # Set minimum size
app.resizable(True, True)         # Ensure resizing is enabled
frame = tk.Frame(app)             # Ensure something fills the space
frame.pack(fill="both", expand=True)

app.mainloop()