from PyQt5 import QtCore, QtWidgets
import subprocess
import sys
import os
import gui
import time

INTERCEPT_TOOL_PATH = os.path.join(os.path.dirname(__file__), 'intercept')

class HaltWindow(QtWidgets.QWidget, gui.Ui_halt):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		gui.Ui_halt.__init__(self)
		self.executable_path = sys.argv[1]
		self.executable = os.path.basename(self.executable_path)
		self.setupUi(self)
		self.setup_functionality()

	def setup_functionality(self):
		self.summary_label.setText(f"The executable {self.executable} has been blocked! Why not do something productive instead?")
		self.continue_button.clicked.connect(self.unlock_relock)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	def unlock_relock(self):
		subprocess.Popen(f'{INTERCEPT_TOOL_PATH} --remove {self.executable}', stdout=subprocess.PIPE)
		time.sleep(0.5)
		os.startfile(self.executable_path)
		time.sleep(1.5)
		subprocess.Popen(f'{INTERCEPT_TOOL_PATH} --add "{self.executable_path}" --target "{__file__}"', stdout=subprocess.PIPE)
		self.close()


if __name__ == '__main__' and len(sys.argv) == 2:
	app = QtWidgets.QApplication(sys.argv)
	window = HaltWindow()
	window.show()
	sys.exit(app.exec_())
