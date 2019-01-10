from PyQt5 import QtCore, QtWidgets
import subprocess
import sys
import os
import json
import gui


INTERCEPT_TARGET = os.path.join(os.path.dirname(__file__), 'halt.pyw')

class ManagerWindow(QtWidgets.QWidget, gui.Ui_pn_settings):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		gui.Ui_pn_settings.__init__(self)
		self.config = self.load_config()
		self.settings = self.config['settings']
		self.setupUi(self)
		self.setup_functionality()

	def load_config(self):
		with open('settings.json') as settings_file:
			return json.loads(settings_file.read())

	def save_config(self):
		with open('settings.json', 'w') as settings_file:
			settings_file.write(json.dumps(self.config, indent=2))

	def setup_functionality(self):
		self.refresh_list()
		self.add_interception_btn.clicked.connect(self.add_interception)
		self.remove_interception_btn.clicked.connect(self.remove_interception)
		self.apply_button.clicked.connect(self.apply_settings)
		# Return buttons to settings state
		self.notify_type_group.buttons()[self.settings['notify_type']].setChecked(True)
		self.interval_number.setValue(self.settings['notify_interval'])

	def apply_settings(self):
		notify_type = self.notify_type_group.buttons().index(self.notify_type_group.checkedButton())
		notify_interval = self.interval_number.value()
		self.settings['notify_type'] = notify_type
		self.settings['notify_interval'] = notify_interval
		self.config['settings'] = self.settings
		self.save_config()

	def refresh_list(self):
		self.interception_list.addItem('Refreshing List...')
		self.interception_list.setDisabled(True)
		self.list_refresher = InterceptionListRefresher()
		self.list_refresher.interceptions.connect(self.change_interception_list)
		self.list_refresher.start()

	def change_interception_list(self, interceptions):
		self.interception_list.clear()
		self.interception_list.addItems(interceptions)
		self.interception_list.setDisabled(False)

	def add_interception(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Executable',
											'C:\\', "Executable File (*.exe)")[0]
		file_name = os.path.basename(path)
		if file_name:
			item_list = [self.interception_list.item(i).text() for i in range(self.interception_list.count())]
			if file_name in item_list:
				QtWidgets.QMessageBox.critical(self, 'Already exists', 'You have already added that executable to the interception list')
			else:
				response = subprocess.Popen(f'elevate intercept --add "{path}" --target "{INTERCEPT_TARGET}"', stdout=subprocess.PIPE)
				out, err = response.communicate()
				self.interception_list.addItem(file_name)


	def remove_interception(self):
		try:
			widget = self.interception_list.selectedItems()[0]
		except IndexError:
			QtWidgets.QMessageBox.warning(self, 'No item selected', 'You need to select an item in the list to remove it')
		else:
			file_name = widget.text()
			self.interception_list.selectionModel().clear()
			response = subprocess.Popen(f'elevate intercept --remove "{file_name}"', stdout=subprocess.PIPE)
			out, err = response.communicate()
			self.interception_list.takeItem(self.interception_list.row(widget))


class InterceptionListRefresher(QtCore.QThread):
	interceptions = QtCore.pyqtSignal(list)

	def run(self):
		response = subprocess.Popen(f'intercept -l', stdout=subprocess.PIPE)
		out, err = response.communicate()
		interceptions = out.decode().strip().split('\r\n')
		if not (interceptions[0] == '' and len(interceptions) == 1):
			self.interceptions.emit(interceptions)
		else:
			self.interceptions.emit([])

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	window = ManagerWindow()
	window.show()
	sys.exit(app.exec_())
