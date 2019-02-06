from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import Settings


# noinspection PyArgumentList,PyUnresolvedReferences
class SettingsDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.setFixedSize(550, 400)
		self.setWindowTitle('Event Reminder Account')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.settings = Settings()

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()
		tabs = QTabWidget(self)
		tabs.setMinimumWidth(self.width() - 22)
		self.setup_login_ui(tabs)
		self.setup_signup_ui(tabs)
		content.addWidget(tabs, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_login_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QVBoxLayout()

		tab.setLayout(layout)
		tabs.addTab(tab, 'Login')

	def setup_signup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QVBoxLayout()

		tab.setLayout(layout)
		tabs.addTab(tab, 'Create Account')
