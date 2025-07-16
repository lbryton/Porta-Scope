all:
	pyinstaller --onefile --collect-submodules PIL --hidden-import=PIL._tkinter_finder \
			--add-data=./porta-janus-lin:. portaScope.py

windows:
	pyinstaller --onefile --collect-submodules PIL --hidden-import=PIL._tkinter_finder ^
			--add-data=.\porta-janus-win:. portaScope.py
run-linux: 
	./dist/retest

run-windows:
	echo "not ready yet"

run-python:
	python retest.py

