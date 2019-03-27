import re
import requests

from requests.exceptions import RequestException

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QLabel, QWidget, QDialog, QLineEdit, QCheckBox, QTabWidget, QVBoxLayout

from erdesktop.util import Worker
from erdesktop.settings import Settings
from erdesktop.cloud import CloudStorage
from erdesktop.widgets.util import PushButton
from erdesktop.widgets.util import info, error
from erdesktop.util.exceptions import CloudStorageException
from erdesktop.widgets.waiting_spinner import WaitingSpinner
from erdesktop.util.exceptions import (
	LoginFailedCredentialsError, LoginFailedError, LogoutFailedError,
	RegisterFailedEmailIsNotProvidedError, RegisterFailedUsernameIsNotProvidedError,
	RegisterFailedError, AuthRequiredError, UserRetrievingError, RegisterFailedUserAlreadyExistsError
)


class AccountDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super(AccountDialog, self).__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('AccountDialog: calendar is not set')

		self.setFixedSize(550, 280)
		self.setWindowTitle(self.tr('Account'))
		self.setWindowFlags(Qt.Dialog)

		self.settings = Settings()
		self.spinner = WaitingSpinner()
		self.thread_pool = QThreadPool()
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.username_signup_input = QLineEdit()
		self.email_signup_input = QLineEdit()

		self.username_login_input = QLineEdit()
		self.password_login_input = QLineEdit()
		self.remember_login_check_box = QCheckBox(self.tr('Remember me'))

		self.login_menu = None
		self.account_info_menu = None

		self.v_layout = QVBoxLayout()
		self.tabs = QTabWidget(self)

		self.setup_ui()

		self.layout().addWidget(self.spinner)

	def showEvent(self, event):
		self.move(
			self.calendar.window().frameGeometry().topLeft() +
			self.calendar.window().rect().center() - self.rect().center()
		)
		super(AccountDialog, self).showEvent(event)

	def setup_ui(self):
		content = QVBoxLayout()
		self.tabs.setMinimumWidth(self.width() - 22)
		self.setup_login_ui(self.tabs)
		self.setup_signup_ui(self.tabs)
		content.addWidget(self.tabs, alignment=Qt.AlignLeft)
		self.setLayout(content)

	@staticmethod
	def create_field(input_field, title=None):
		layout = QVBoxLayout()
		layout.setContentsMargins(50, 0, 50, 10)
		if title is not None:

			# noinspection PyArgumentList
			layout.addWidget(QLabel('{}:'.format(title)))

		# noinspection PyArgumentList
		layout.addWidget(input_field)
		return layout

	def build_login_menu(self):
		layout = QVBoxLayout()

		layout.addLayout(self.create_field(self.username_login_input, self.tr('Username')))

		self.password_login_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(self.create_field(self.password_login_input, self.tr('Password')))

		self.remember_login_check_box.setChecked(True)
		layout.addLayout(self.create_field(self.remember_login_check_box))

		btn = PushButton(self.tr('Login'), 70, 30, self.login_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, self.tr('Login')

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

		btn = PushButton(self.tr('Logout'), 70, 30, self.logout_click)
		btn.setFixedWidth(100)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		return layout, user_data['username']

	def setup_login_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		tab_name = self.tr('Login')
		try:
			self.account_info_menu, tab_name = self.build_account_info_menu()
			self.v_layout.addLayout(self.account_info_menu)
		except requests.exceptions.ConnectionError:
			self.v_layout.setContentsMargins(0, 50, 0, 50)
			self.v_layout.addWidget(QLabel(self.tr('Connection error')), alignment=Qt.AlignCenter)
			self.v_layout.addWidget(
				QLabel(self.tr(
					'Server is not working or your internet connection is failed'
				)), alignment=Qt.AlignCenter
			)
			self.v_layout.addWidget(QLabel(
				self.tr('Check your connection and reopen this dialog')
			), alignment=Qt.AlignCenter)
		except CloudStorageException as _:
			self.cloud.remove_token()
			self.login_menu, tab_name = self.build_login_menu()
			self.v_layout.addLayout(self.login_menu)
		tab.setLayout(self.v_layout)
		tabs.addTab(tab, tab_name)

	def setup_signup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QVBoxLayout()

		layout.addLayout(self.create_field(self.username_signup_input, self.tr('Username')))

		layout.addLayout(self.create_field(self.email_signup_input, self.tr('Email')))

		btn = PushButton(self.tr('Register'), 150, 30, self.signup_click)
		layout.addWidget(btn, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('New account'))

	def validate_signup_fields(self):
		errors = ''
		if len(self.username_signup_input.text()) < 1:
			errors += '* {}\n'.format(self.tr('Username field can not be empty'))
		if len(self.email_signup_input.text()) < 1:
			errors += '* {}\n'.format(self.tr('Email field can not be empty'))
		else:
			if not re.match(r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', self.email_signup_input.text()):
				errors += '* {}'.format(self.tr('Email is not valid'))
		return errors

	def validate_login_fields(self):
		errors = ''
		if len(self.username_login_input.text()) < 1:
			errors += '* {}\n'.format(self.tr('Username field can not be empty'))
		if len(self.password_login_input.text()) < 1:
			errors += '* {}\n'.format(self.tr('Password field can not be empty'))
		return errors

	def signup_click(self):
		errors = self.validate_signup_fields()
		if errors != '':
			error(self, errors)
		else:
			self.exec_worker(
				self.cloud.register_account,
				self.signup_success,
				*(self.username_signup_input.text(), self.email_signup_input.text())
			)

	def signup_success(self):
		info(
			self,
			'{}.\n{}. {}.'.format(
				self.tr('Thank you for registration'),
				self.tr('Check out {} for credentials information').format(self.email_signup_input.text()),
				self.tr('To activate, simply login to Your account, otherwise it will be deleted in 24 hours after registration')
			)
		)
		self.email_signup_input.clear()

	def login_click(self):
		errors = self.validate_login_fields()
		if errors != '':
			pass
		else:
			self.exec_worker(
				self.cloud.login,
				self.login_success,
				*(
					self.username_login_input.text(),
					self.password_login_input.text(),
					self.remember_login_check_box.isChecked()
				)
			)

	def login_success(self):
		self.close()
		info(self, '{} {}'.format(self.tr('Logged in as'), self.username_login_input.text()))

	def logout_click(self):
		self.exec_worker(
			self.cloud.logout,
			self.logout_success
		)

	def logout_success(self):
		self.close()
		info(self, '{}.'.format(self.tr('Successfully logged out')))

	def exec_worker(self, fn, fn_success, *args, **kwargs):
		self.spinner.start()
		worker = Worker(fn, *args, **kwargs)
		worker.signals.success.connect(fn_success)
		worker.signals.error.connect(self.popup_error)
		worker.signals.finished.connect(self.spinner.stop)
		self.thread_pool.start(worker)

	def popup_error(self, err):
		try:
			raise err[0](err[1])
		except LoginFailedCredentialsError:
			err_msg = self.tr('Login failure: unable to log in with provided credentials')
		except LoginFailedError:
			err_msg = '{} {}'.format(self.tr('Login failure: unable to log in, status'), err[1])
		except LogoutFailedError:
			err_msg = '{} {}'.format(self.tr('Logout failure: unable to log out, status'), err[1])
		except RegisterFailedUsernameIsNotProvidedError:
			err_msg = self.tr('Registration failure: username is not provided')
		except RegisterFailedEmailIsNotProvidedError:
			err_msg = self.tr('Registration failure: email is not provided')
		except RegisterFailedUserAlreadyExistsError:
			err_msg = self.tr('Registration failure: user already exists')
		except RegisterFailedError:
			err_msg = self.tr('Registration failure: unable to register an account, status')
		except AuthRequiredError:
			err_msg = self.tr('Reading account failure: authentication is required')
		except UserRetrievingError:
			err_msg = '{} {}'.format(self.tr('Reading account failure: unable to retrieve account information, status'), err[1])
		except (CloudStorageException, RequestException, Exception):
			err_msg = str(err[1])
		error(self, err_msg)
