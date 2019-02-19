import re
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QWidget, QDialog, QLineEdit, QCheckBox, QTabWidget, QVBoxLayout

from app.settings import Settings
from app.cloud import CloudStorage
from app.widgets.util import PushButton
from app.widgets.util.popup import info, error
from app.exceptions import CloudStorageException


# noinspection PyArgumentList,PyUnresolvedReferences
class AccountDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.setFixedSize(550, 300)
		self.setWindowTitle('Account')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

		self.settings = Settings()
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.username_signup_input = QLineEdit()
		self.email_signup_input = QLineEdit()

		self.username_login_input = QLineEdit()
		self.password_login_input = QLineEdit()
		self.remember_login_check_box = QCheckBox('Remember me')

		self.login_menu = None
		self.account_info_menu = None

		self.layout = QVBoxLayout()
		self.tabs = QTabWidget(self)

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()
		self.tabs.setMinimumWidth(self.width() - 22)
		self.setup_login_ui(self.tabs)
		self.setup_signup_ui(self.tabs)
		content.addWidget(self.tabs, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def build_login_menu(self):
		layout = QVBoxLayout()

		un_layout = QVBoxLayout()
		un_layout.setContentsMargins(50, 0, 50, 10)
		un_layout.addWidget(QLabel('Username:'))
		un_layout.addWidget(self.username_login_input)
		layout.addLayout(un_layout)

		pwd_layout = QVBoxLayout()
		pwd_layout.setContentsMargins(50, 0, 50, 10)
		pwd_layout.addWidget(QLabel('Password:'))
		self.password_login_input.setEchoMode(QLineEdit.Password)
		pwd_layout.addWidget(self.password_login_input)
		layout.addLayout(pwd_layout)

		rl_layout = QVBoxLayout()
		rl_layout.setContentsMargins(50, 0, 50, 10)
		self.remember_login_check_box.setChecked(True)
		rl_layout.addWidget(self.remember_login_check_box)
		layout.addLayout(rl_layout)

		btn = PushButton('Login', 70, 30, self.login_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, 'Login'

	def build_account_info_menu(self):
		user_data = self.cloud.user()
		layout = QVBoxLayout()

		header_layout = QVBoxLayout()
		header_layout.setContentsMargins(0, 0, 0, 10)

		username_lbl = QLabel('{}'.format(user_data['username']))
		username_lbl.setFont(QFont('SansSerif', 18))
		header_layout.addWidget(username_lbl, alignment=Qt.AlignCenter)
		layout.addLayout(header_layout)

		header_layout.addWidget(
			QLabel('{}'.format(user_data['email'])),
			alignment=Qt.AlignCenter
		)

		btn = PushButton('Logout', 70, 30, self.logout_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, user_data['username']

	def setup_login_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		tab_name = 'Login'
		# noinspection PyBroadException
		try:
			self.account_info_menu, tab_name = self.build_account_info_menu()
			self.layout.addLayout(self.account_info_menu)
		except requests.exceptions.ConnectionError:
			self.layout.setContentsMargins(0, 90, 0, 90)
			self.layout.addWidget(QLabel('Connection error'), alignment=Qt.AlignCenter)
			self.layout.addWidget(
				QLabel('Server is not working or your internet connection is failed'), alignment=Qt.AlignCenter
			)
			self.layout.addWidget(QLabel('Check your connection and reopen this dialog'), alignment=Qt.AlignCenter)
		except CloudStorageException as _:
			self.login_menu, tab_name = self.build_login_menu()
			self.layout.addLayout(self.login_menu)
		tab.setLayout(self.layout)
		tabs.addTab(tab, tab_name)

	def setup_signup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QVBoxLayout()

		un_layout = QVBoxLayout()
		un_layout.setContentsMargins(50, 0, 50, 10)
		un_layout.addWidget(QLabel('Username:'))
		un_layout.addWidget(self.username_signup_input)
		layout.addLayout(un_layout)

		e_layout = QVBoxLayout()
		e_layout.setContentsMargins(50, 0, 50, 10)
		e_layout.addWidget(QLabel('Email:'))
		e_layout.addWidget(self.email_signup_input)
		layout.addLayout(e_layout)

		btn = PushButton('Register', 70, 30, self.signup_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, 'New account')

	def validate_signup_fields(self):
		errors = ''
		if len(self.username_signup_input.text()) < 1:
			errors += '* Username field can not be empty\n'
		if len(self.email_signup_input.text()) < 1:
			errors += '* Email field can not be empty\n'
		else:
			if not re.match(r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', self.email_signup_input.text()):
				errors += '* Email is not valid'
		if errors != '':
			raise RuntimeError(errors)

	def validate_login_fields(self):
		errors = ''
		if len(self.username_login_input.text()) < 1:
			errors += '* Username field can not be empty\n'
		if len(self.password_login_input.text()) < 1:
			errors += '* Password field can not be empty\n'
		if errors != '':
			raise RuntimeError(errors)

	def signup_click(self):
		try:
			self.validate_signup_fields()
			self.cloud.register_account(
				self.username_signup_input.text(),
				self.email_signup_input.text()
			)
			info(
				self,
				'Thank you for registration.\n'
				'Check out {} for credentials information.\n'
				'To activate, simply login to Your account, otherwise'
				'it will be deleted in 24 hours after registration.'.format(self.email_signup_input.text())
			)
			self.email_signup_input.clear()
		except Exception as exc:
			error(self, str(exc))

	def login_click(self):
		try:
			self.validate_login_fields()
			self.cloud.login(
				self.username_login_input.text(),
				self.password_login_input.text(),
				self.remember_login_check_box.isChecked()
			)
			info(self, 'Logged in as {}'.format(self.username_login_input.text()))
			self.close()
		except Exception as exc:
			error(self, str(exc))

	def logout_click(self):
		try:
			self.cloud.logout()
			info(self, 'Successfully logged out.')
			self.close()
		except Exception as exc:
			error(self, str(exc))
