from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtWidgets import (
	QDialog, QLineEdit, QCheckBox, QComboBox, QVBoxLayout,
	QHBoxLayout, QWidget, QGridLayout, QLabel, QTabWidget
)

from requests.exceptions import RequestException

from erdesktop.util import Worker
from erdesktop.cloud import CloudStorage
from erdesktop.widgets.util import PushButton, popup
from erdesktop.widgets.waiting_spinner import WaitingSpinner
from erdesktop.util.exceptions import UserUpdatingError, RequestTokenError, ResetPasswordError, CloudStorageException
from erdesktop.settings import Settings, FONT_LARGE, FONT_SMALL, FONT_NORMAL, AVAILABLE_LANGUAGES, AVAILABLE_LANGUAGES_IDX


# noinspection PyArgumentList,PyUnresolvedReferences
class SettingsDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('SettingsDialog: calendar is not set')

		self.settings = Settings()

		if self.settings.app_lang == 'en_US':
			self.setFixedSize(500, 400)
		else:
			self.setFixedSize(650, 400)
		self.setWindowTitle(self.tr('Settings'))
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.spinner = WaitingSpinner()
		self.thread_pool = QThreadPool()
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.always_on_top_check_box = QCheckBox()
		self.font_combo_box = QComboBox()
		self.show_calendar_on_startup_check_box = QCheckBox()
		self.theme_combo_box = QComboBox()

		self.remove_after_time_up_check_box = QCheckBox()
		self.notification_duration_input = QLineEdit()
		self.remind_time_before_event_input = QLineEdit()

		self.include_settings_backup_check_box = QCheckBox()

		self.email_input = QLineEdit()
		self.new_password_input = QLineEdit()
		self.new_password_repeat_input = QLineEdit()
		self.verification_token_input = QLineEdit()
		self.lang_combo_box = QComboBox()
		self.backups_number_input = QLineEdit()
		btn_width = 170
		if self.settings.app_lang != 'en_US':
			btn_width = 230
		self.change_password_btn = PushButton(
			self.tr('Send Confirmation'), btn_width, 30, self.change_password_btn_click
		)

		self.token_is_sent = False

		self.ui_is_loaded = False
		self.setup_ui()

		self.refresh_settings_values()

		self.layout().addWidget(self.spinner)

		self.ui_is_loaded = True

	def showEvent(self, event):
		self.move(
			self.calendar.window().frameGeometry().topLeft() +
			self.calendar.window().rect().center() - self.rect().center()
		)
		max_backups = self.settings.app_max_backups
		try:
			user = self.cloud.user()
			max_backups = user['max_backups']
		except Exception as exc:
			print(exc)
		self.backups_number_input.setText(str(max_backups))
		super(SettingsDialog, self).showEvent(event)

	def refresh_settings_values(self):
		self.theme_combo_box.setCurrentIndex(1 if self.settings.is_dark_theme else 0)
		curr_idx = 0
		if self.settings.app_font == FONT_NORMAL:
			curr_idx = 1
		elif self.settings.app_font == FONT_LARGE:
			curr_idx = 2
		self.font_combo_box.setCurrentIndex(curr_idx)
		self.show_calendar_on_startup_check_box.setChecked(self.settings.show_calendar_on_startup)
		self.always_on_top_check_box.setChecked(self.settings.is_always_on_top)
		self.include_settings_backup_check_box.setChecked(self.settings.include_settings_backup)
		self.remove_after_time_up_check_box.setChecked(self.settings.remove_event_after_time_up)
		self.notification_duration_input.setText(str(self.settings.notification_duration))
		self.remind_time_before_event_input.setText(str(self.settings.remind_time_before_event))

	def setup_ui(self):
		content = QVBoxLayout()
		tab_widget = QTabWidget(self)
		tab_widget.setMinimumWidth(self.width() - 22)
		self.setup_app_settings_ui(tab_widget)
		self.setup_events_settings_ui(tab_widget)
		self.setup_account_settings_ui(tab_widget)
		content.addWidget(tab_widget, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_app_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(50, 10, 50, 10)
		layout.setSpacing(20)

		layout.addWidget(QLabel(self.tr('Theme')), 0, 0)
		self.theme_combo_box.currentIndexChanged.connect(self.theme_changed)
		self.theme_combo_box.addItems([self.tr('Light'), self.tr('Dark')])
		layout.addWidget(self.theme_combo_box, 0, 1)

		layout.addWidget(QLabel(self.tr('Font')), 1, 0)
		self.font_combo_box.currentIndexChanged.connect(self.font_changed)
		self.font_combo_box.addItems([self.tr('Small'), self.tr('Normal'), self.tr('Large')])
		layout.addWidget(self.font_combo_box, 1, 1)

		layout.addWidget(QLabel(self.tr('Show calendar on startup')), 2, 0)
		self.show_calendar_on_startup_check_box.stateChanged.connect(self.show_calendar_on_startup_changed)
		layout.addWidget(self.show_calendar_on_startup_check_box, 2, 1)

		layout.addWidget(QLabel(self.tr('Always on top (restart required)')), 3, 0)
		self.always_on_top_check_box.stateChanged.connect(self.always_on_top_changed)
		layout.addWidget(self.always_on_top_check_box, 3, 1)

		layout.addWidget(QLabel(self.tr('Backup settings')), 4, 0)
		self.include_settings_backup_check_box.stateChanged.connect(self.include_settings_backup_changed)
		layout.addWidget(self.include_settings_backup_check_box, 4, 1)

		layout.addWidget(QLabel(self.tr('Language (restart required)')), 5, 0)
		self.lang_combo_box.addItems(AVAILABLE_LANGUAGES.keys())
		try:
			idx = AVAILABLE_LANGUAGES_IDX[self.settings.app_lang]
		except KeyError:
			idx = 0
		self.lang_combo_box.setCurrentIndex(idx)
		self.lang_combo_box.currentIndexChanged.connect(self.lang_changed)
		layout.addWidget(self.lang_combo_box, 5, 1)

		layout.addWidget(QLabel(self.tr('Maximum backups number')), 6, 0)
		self.backups_number_input.setValidator(QIntValidator())
		self.backups_number_input.textChanged.connect(self.max_backups_changed)
		layout.addWidget(self.backups_number_input, 6, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('App'))

	def setup_events_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(50, 30, 50, 10)
		layout.setSpacing(20)

		layout.addWidget(QLabel(self.tr('Remove event after time is up')), 0,  0)
		self.remove_after_time_up_check_box.stateChanged.connect(self.remove_after_time_up_changed)
		layout.addWidget(self.remove_after_time_up_check_box, 0, 1)

		layout.addWidget(QLabel(self.tr('Notification duration (sec)')), 1, 0)
		self.notification_duration_input.setValidator(QIntValidator())
		self.notification_duration_input.textChanged.connect(self.notification_duration_changed)
		layout.addWidget(self.notification_duration_input, 1, 1)

		layout.addWidget(QLabel(self.tr('Notify before event (min)')), 2, 0)
		self.remind_time_before_event_input.setValidator(QIntValidator())
		self.remind_time_before_event_input.textChanged.connect(self.remind_time_before_event_changed)
		layout.addWidget(self.remind_time_before_event_input, 2, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Events'))

	@staticmethod
	def create_field(title, enabled, func, field_input):
		layout = QVBoxLayout()
		layout.setContentsMargins(50, 0, 50, 10)
		layout.addWidget(QLabel('{}:'.format(title)))
		field_input.textChanged.connect(func)
		field_input.setEnabled(enabled)
		layout.addWidget(field_input)
		return layout

	def setup_account_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QVBoxLayout()

		layout.addLayout(
			self.create_field(self.tr('Email'), True, self.change_password_inputs_changed, self.email_input)
		)

		self.new_password_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(
			self.create_field(self.tr('New Password'), False, self.change_password_inputs_changed, self.new_password_input)
		)

		self.new_password_repeat_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(
			self.create_field(self.tr('Repeat Password'), False, self.change_password_inputs_changed, self.new_password_repeat_input)
		)

		layout.addLayout(
			self.create_field(self.tr('Verification Token'), False, self.change_password_inputs_changed, self.verification_token_input)
		)

		h_layout = QHBoxLayout()
		self.change_password_btn.setEnabled(False)
		h_layout.addWidget(self.change_password_btn)
		btn_width = 150
		if self.settings.app_lang != 'en_US':
			btn_width = 200
		reset_change_password_btn = PushButton(
			self.tr('Reset Inputs'), btn_width, 30, self.reset_change_password_btn_click
		)
		h_layout.addWidget(reset_change_password_btn)
		layout.addLayout(h_layout)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Reset Password'))

	def always_on_top_changed(self):
		if self.ui_is_loaded:
			self.settings.set_is_always_on_top(self.always_on_top_check_box.isChecked())

	def font_changed(self, current):
		if self.ui_is_loaded:
			new_font = FONT_SMALL
			if current == 1:
				new_font = FONT_NORMAL
			elif current == 2:
				new_font = FONT_LARGE
			font = QFont('SansSerif', new_font)
			self.settings.set_font(new_font)
			self.calendar.reset_font(font)

	def show_calendar_on_startup_changed(self):
		if self.ui_is_loaded:
			self.settings.set_show_calendar_on_startup(self.show_calendar_on_startup_check_box.isChecked())

	def theme_changed(self, current):
		if self.ui_is_loaded:
			self.settings.set_theme(current == 1)
			self.calendar.reset_palette(self.settings.app_theme)

	def remove_after_time_up_changed(self):
		self.settings.set_remove_event_after_time_up(self.remove_after_time_up_check_box.isChecked())

	def notification_duration_changed(self):
		text = self.notification_duration_input.text()
		if len(text) > 0:
			self.settings.set_notification_duration(int(text))

	def remind_time_before_event_changed(self):
		text = self.remind_time_before_event_input.text()
		if len(text) > 0:
			self.settings.set_remind_time_before_event(int(text))

	def include_settings_backup_changed(self):
		if self.ui_is_loaded:
			self.settings.set_include_settings_backup(self.include_settings_backup_check_box.isChecked())

	def lang_changed(self):
		lang = AVAILABLE_LANGUAGES[self.lang_combo_box.currentText()]
		self.settings.set_lang(lang)

	def max_backups_changed(self):
		max_backups = self.backups_number_input.text()
		if len(max_backups) > 0:
			self.settings.set_max_backups(int(max_backups))
			worker = Worker(self.cloud.update_user, **{
				'max_backups': max_backups if max_backups != '' else None
			})
			self.thread_pool.start(worker)

	def reset_change_password_btn_click(self):
		self.email_input.clear()
		self.new_password_input.clear()
		self.new_password_repeat_input.clear()
		self.verification_token_input.clear()
		self.new_password_input.setEnabled(False)
		self.new_password_repeat_input.setEnabled(False)
		self.verification_token_input.setEnabled(False)
		self.change_password_btn.setText(self.tr('Send Confirmation'))
		self.change_password_btn.setEnabled(False)

	def change_password_inputs_changed(self):
		self.change_password_btn.setEnabled(False)
		if len(self.email_input.text()) > 0:
			if not self.token_is_sent:
				self.change_password_btn.setEnabled(True)
			else:
				if all(
						(
							len(self.verification_token_input.text()) > 0,
							len(self.new_password_input.text()) > 0,
							len(self.new_password_repeat_input.text()) > 0
						)
				):
					self.change_password_btn.setEnabled(True)

	def change_password_btn_click(self):
		if self.token_is_sent:
			if self.new_password_input.text() != self.new_password_repeat_input.text():
				popup.error(self, self.tr('Password confirmation failed'))
			else:
				self.exec_worker(
					self.cloud.reset_password,
					self.change_password_success,
					*(
						self.email_input.text(),
						self.new_password_input.text(),
						self.new_password_repeat_input.text(),
						self.verification_token_input.text()
					)
				)
		else:
			self.exec_worker(
				self.cloud.request_token,
				self.change_password_request_token_success,
				*(self.email_input.text(),)
			)

	def change_password_request_token_success(self):
		popup.info(self, self.tr('Check your email box for verification token'))
		self.token_is_sent = True
		self.new_password_input.setEnabled(True)
		self.new_password_input.setFocus()
		self.new_password_repeat_input.setEnabled(True)
		self.verification_token_input.setEnabled(True)
		self.change_password_btn.setText(self.tr('Change'))
		self.change_password_btn.setEnabled(False)

	def change_password_success(self):
		self.reset_change_password_btn_click()
		self.cloud.remove_token()
		popup.info(self, self.tr('New password has been set'))

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
		except UserUpdatingError:
			err_msg = '{} {}'.format(self.tr('Updating user failure: unable to update user account, status'), err[1])
		except RequestTokenError:
			err_msg = '{} {}'.format(self.tr('Reset password failure: unable to request token, status'), err[1])
		except ResetPasswordError:
			err_msg = '{} {}'.format(self.tr('Reset password failure: unable to reset user password, status'), err[1])
		except (CloudStorageException, RequestException, Exception):
			err_msg = str(err[1])
		popup.error(self, err_msg)