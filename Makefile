all:
	pyinstaller --onefile --collect-submodules PIL --hidden-import=PIL._tkinter_finder retest.py

run-linux: 
	./dist/retest

run-windows:
	echo "not ready yet"

run-python:
	python retest.py