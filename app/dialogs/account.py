import re

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import Settings
from app.cloud import CloudStorage
from app.utils import create_button, info, error


# noinspection PyArgumentList,PyUnresolvedReferences
class AccountDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.setFixedSize(550, 300)
		self.setWindowTitle('Event Reminder Account')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.settings = Settings()
		self.cloud = CloudStorage()

		self.first_name_signup_input = QLineEdit()
		self.last_name_signup_input = QLineEdit()
		self.email_signup_input = QLineEdit()

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

		fn_layout = QVBoxLayout()
		fn_layout.setContentsMargins(50, 0, 50, 10)
		fn_layout.addWidget(QLabel('First name:'))
		fn_layout.addWidget(self.first_name_signup_input)
		layout.addLayout(fn_layout)

		ln_layout = QVBoxLayout()
		ln_layout.setContentsMargins(50, 0, 50, 10)
		ln_layout.addWidget(QLabel('Last name:'))
		ln_layout.addWidget(self.last_name_signup_input)
		layout.addLayout(ln_layout)

		e_layout = QVBoxLayout()
		e_layout.setContentsMargins(50, 0, 50, 10)
		e_layout.addWidget(QLabel('Email:'))
		e_layout.addWidget(self.email_signup_input)
		layout.addLayout(e_layout)

		btn = create_button('Sign Up', 70, 30, self.signup_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Create Account')

	def validate_signup_fields(self):
		errors = ''
		if len(self.first_name_signup_input.text()) < 1:
			errors += '* first name field can not be empty\n'
		if len(self.last_name_signup_input.text()) < 1:
			errors += '* last name field can not be empty\n'
		if len(self.email_signup_input.text()) < 1:
			errors += '* email field can not be empty\n'
		else:
			if not re.match(r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', self.email_signup_input.text()):
				errors += '* email is not valid'
		if errors != '':
			raise RuntimeError(errors)

	def signup_click(self):
		try:
			self.validate_signup_fields()
			self.cloud.register_account(
				self.first_name_signup_input.text(),
				self.last_name_signup_input.text(),
				self.email_signup_input.text()
			)
			info(self, 'Thank you for registration.\nCheck out {} for credentials information.'.format(
				self.email_signup_input.text()
			))
			self.first_name_signup_input.clear()
			self.last_name_signup_input.clear()
			self.email_signup_input.clear()
		except Exception as exc:
			error(self, str(exc))
