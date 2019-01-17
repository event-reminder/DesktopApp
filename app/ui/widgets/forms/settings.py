from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QListWidgetItem

from app.ui.utils import create_button


class SettingsForm:

	def __init__(self, parent):
		self.parent = parent
		self.parent.setFixedSize(500, 400)
		self.parent.setWindowTitle('Settings')
		self.calendar = None
		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()

		settings_general_tabs = QTabWidget(self.parent)

		settings_general_tabs.setMinimumWidth(self.parent.width() - 22)

		app_tab = QWidget(flags=settings_general_tabs.windowFlags())
		notifications_tab = QWidget(flags=settings_general_tabs.windowFlags())
		settings_general_tabs.addTab(app_tab, 'App')
		settings_general_tabs.addTab(notifications_tab, 'Notifications')

		content.addWidget(settings_general_tabs, alignment=Qt.AlignLeft)

		self.set_app_settings(content)
		self.set_user_settings(content)

		self.parent.setLayout(content)

	def set_app_settings(self, content):
		pass

	def set_user_settings(self, content):
		pass

	def set_calendar_widget(self, calendar):
		self.calendar = calendar

	def save_btn_click(self):
		self.parent.close()
