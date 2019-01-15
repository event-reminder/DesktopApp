from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils import create_button


class SettingsForm:

	def __init__(self, parent):
		self.parent = parent
		self.parent.setFixedSize(500, 400)
		self.calendar = None

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()

		# TODO: implement settings content

		self.parent.setLayout(content)

	def set_calendar_widget(self, calendar):
		self.calendar = calendar

	def save_btn_click(self):
		self.parent.close()
