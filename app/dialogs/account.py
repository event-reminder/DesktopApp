import re
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
	QLabel,
	QWidget,
	QDialog,
	QLineEdit,
	QCheckBox,
	QTabWidget,
	QVBoxLayout
)

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
		self.setWindowTitle('Account')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.settings = Settings()
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.first_name_signup_input = QLineEdit()
		self.last_name_signup_input = QLineEdit()
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
		self.remember_login_check_box.setChecked(False)
		rl_layout.addWidget(self.remember_login_check_box)
		layout.addLayout(rl_layout)

		btn = create_button('Login', 70, 30, self.login_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, 'Login'

	def build_account_info_menu(self):
		user_data = self.cloud.user()
		layout = QVBoxLayout()

		header_layout = QVBoxLayout()
		header_layout.setContentsMargins(0, 0, 0, 10)
		header_layout.addWidget(
			QLabel('{}'.format(user_data['email'])),
			alignment=Qt.AlignCenter
		)
		username_lbl = QLabel('{}'.format(user_data['username']))
		username_lbl.setFont(QFont('SansSerif', 9))
		header_layout.addWidget(username_lbl, alignment=Qt.AlignCenter)
		layout.addLayout(header_layout)

		email_lbl = QLabel('{} {}'.format(user_data['first_name'], user_data['last_name']))
		email_lbl.setFont(QFont('SansSerif', 16))
		email_lbl.setContentsMargins(0, 0, 0, 10)
		layout.addWidget(email_lbl, alignment=Qt.AlignCenter)

		btn = create_button('Logout', 70, 30, self.logout_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, '{} {}'.format(user_data['first_name'], user_data['last_name'])

	def setup_login_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		tab_name = 'Login'
		try:
			if self.cloud.token_id_valid():
				self.account_info_menu, tab_name = self.build_account_info_menu()
				self.layout.addLayout(self.account_info_menu)
			else:
				self.login_menu, tab_name = self.build_login_menu()
				self.layout.addLayout(self.login_menu)
		except requests.exceptions.ConnectionError:
			self.layout.setContentsMargins(0, 90, 0, 90)
			self.layout.addWidget(QLabel('Connection error'), alignment=Qt.AlignCenter)
			self.layout.addWidget(QLabel('Server is not working or your internet connection is failed'), alignment=Qt.AlignCenter)
			self.layout.addWidget(QLabel('Check your connection and restart app'), alignment=Qt.AlignCenter)
		tab.setLayout(self.layout)
		tabs.addTab(tab, tab_name)

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

		btn = create_button('Register', 70, 30, self.signup_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, 'New account')

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
			try:
				self.cloud.register_account(
					self.first_name_signup_input.text(),
					self.last_name_signup_input.text(),
					self.email_signup_input.text()
				)
				info(
					self,
					'Thank you for registration.'
					'Check out {} for credentials information.'
					.format(
						self.email_signup_input.text()
					)
				)
				self.first_name_signup_input.clear()
				self.last_name_signup_input.clear()
				self.email_signup_input.clear()
			except requests.exceptions.ConnectionError:
				error(
					self,
					'Connection error'
					'Server is not working or your internet connection is failed.'
					'Check your connection and restart app.'
				)
		except Exception as exc:
			error(self, str(exc))

	def validate_login_fields(self):
		errors = ''
		if len(self.username_login_input.text()) < 1:
			errors += '* username field can not be empty\n'
		if len(self.password_login_input.text()) < 1:
			errors += '* password field can not be empty\n'
		if errors != '':
			raise RuntimeError(errors)

	def login_click(self):
		try:
			self.validate_login_fields()
			try:
				self.cloud.login(
					self.username_login_input.text(),
					self.password_login_input.text(),
					self.remember_login_check_box.isChecked()
				)
				info(self, 'Logged in as {}'.format(self.username_login_input.text()))
				self.close()
			except requests.exceptions.ConnectionError:
				error(
					self,
					'Connection error'
					'Server is not working or your internet connection is failed.'
					'Check your connection and restart app.'
				)
		except Exception as exc:
			error(self, str(exc))

	def logout_click(self):
		try:
			self.cloud.logout()
			info(self, 'Successfully logged out.')
			self.close()
		except requests.exceptions.ConnectionError:
			error(
				self,
				'Connection error'
				'Server is not working or your internet connection is failed.'
				'Check your connection and restart app.'
			)
