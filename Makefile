all:
	pyinstaller --onefile --collect-submodules PIL --hidden-import=PIL._tkinter_finder retest.py

run: 
	./dist/retest