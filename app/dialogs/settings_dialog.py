from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtWidgets import (
	QDialog, QLineEdit, QCheckBox, QComboBox, QVBoxLayout,
	QHBoxLayout, QWidget, QGridLayout, QLabel, QTabWidget
)

from requests.exceptions import RequestException

from app.util import Worker
from app.cloud import CloudStorage
from app.widgets.util import PushButton, popup
from app.widgets.waiting_spinner import WaitingSpinner
from app.util.exceptions import UserUpdatingError, RequestTokenError, ResetPasswordError, CloudStorageException
from app.settings import Settings, FONT_LARGE, FONT_SMALL, FONT_NORMAL, AVAILABLE_LANGUAGES, AVAILABLE_LANGUAGES_IDX


# noinspection PyArgumentList,PyUnresolvedReferences
class SettingsDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs['calendar']

		self.setFixedSize(500, 400)
		self.setWindowTitle('Settings')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.settings = Settings()
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
		self.change_password_btn = PushButton('Send Token', 150, 30, self.change_password_btn_click)

		self.token_is_sent = False

		self.ui_is_loaded = False
		self.setup_ui()

		self.refresh_settings_values()

		self.layout().addWidget(self.spinner)

		self.ui_is_loaded = True

	def showEvent(self, event):
		lang = self.settings.app_lang
		max_backups = self.settings.app_max_backups
		try:
			self.cloud.user()
			lang = AVAILABLE_LANGUAGES[self.lang_combo_box.currentText()]
			worker = Worker(self.cloud.update_user, **{
				'lang': lang if lang != '' else None,
				'max_backups': max_backups if max_backups != '' else None
			})
			self.thread_pool.start(worker)
		except Exception as exc:
			print(exc)
		try:
			idx = AVAILABLE_LANGUAGES_IDX[lang]
		except KeyError:
			idx = 0
		self.lang_combo_box.setCurrentIndex(idx)
		self.backups_number_input.setText(str(max_backups))
		super().showEvent(event)

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

		layout.addWidget(QLabel('Theme'), 0, 0)
		self.theme_combo_box.currentIndexChanged.connect(self.theme_changed)
		self.theme_combo_box.addItems(['Light', 'Dark'])
		layout.addWidget(self.theme_combo_box, 0, 1)

		layout.addWidget(QLabel('Font'), 1, 0)
		self.font_combo_box.currentIndexChanged.connect(self.font_changed)
		self.font_combo_box.addItems(['Small', 'Normal', 'Large'])
		layout.addWidget(self.font_combo_box, 1, 1)

		layout.addWidget(QLabel('Show calendar on startup'), 2, 0)
		self.show_calendar_on_startup_check_box.stateChanged.connect(self.show_calendar_on_startup_changed)
		layout.addWidget(self.show_calendar_on_startup_check_box, 2, 1)

		layout.addWidget(QLabel('Always on top (restart required)'), 3, 0)
		self.always_on_top_check_box.stateChanged.connect(self.always_on_top_changed)
		layout.addWidget(self.always_on_top_check_box, 3, 1)

		layout.addWidget(QLabel('Backup settings'), 4, 0)
		self.include_settings_backup_check_box.stateChanged.connect(self.include_settings_backup_changed)
		layout.addWidget(self.include_settings_backup_check_box, 4, 1)

		layout.addWidget(QLabel('Language (restart required)'), 5, 0)
		self.lang_combo_box.addItems(AVAILABLE_LANGUAGES.keys())
		self.lang_combo_box.currentIndexChanged.connect(self.lang_changed)
		layout.addWidget(self.lang_combo_box, 5, 1)

		layout.addWidget(QLabel('Backups number'), 6, 0)
		self.backups_number_input.setValidator(QIntValidator())
		self.backups_number_input.textChanged.connect(self.max_backups_changed)
		layout.addWidget(self.backups_number_input, 6, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, 'App')

	def setup_events_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(50, 30, 50, 10)
		layout.setSpacing(20)

		layout.addWidget(QLabel('Remove event after time is up'), 0,  0)
		self.remove_after_time_up_check_box.stateChanged.connect(self.remove_after_time_up_changed)
		layout.addWidget(self.remove_after_time_up_check_box, 0, 1)

		layout.addWidget(QLabel('Notification duration (sec)'), 1, 0)
		self.notification_duration_input.setValidator(QIntValidator())
		self.notification_duration_input.textChanged.connect(self.notification_duration_changed)
		layout.addWidget(self.notification_duration_input, 1, 1)

		layout.addWidget(QLabel('Notify before event (min)'), 2, 0)
		self.remind_time_before_event_input.setValidator(QIntValidator())
		self.remind_time_before_event_input.textChanged.connect(self.remind_time_before_event_changed)
		layout.addWidget(self.remind_time_before_event_input, 2, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Events')

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
			self.create_field('Email', True, self.change_password_inputs_changed, self.email_input)
		)

		self.new_password_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(
			self.create_field('New Password', False, self.change_password_inputs_changed, self.new_password_input)
		)

		self.new_password_repeat_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(
			self.create_field('Repeat Password', False, self.change_password_inputs_changed, self.new_password_repeat_input)
		)

		layout.addLayout(
			self.create_field('Verification Token', False, self.change_password_inputs_changed, self.verification_token_input)
		)

		h_layout = QHBoxLayout()
		self.change_password_btn.setEnabled(False)
		h_layout.addWidget(self.change_password_btn)
		reset_change_password_btn = PushButton('Reset Inputs', 150, 30, self.reset_change_password_btn_click)
		h_layout.addWidget(reset_change_password_btn)
		layout.addLayout(h_layout)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Reset Password')

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
		worker = Worker(self.cloud.update_user, **{
			'lang': lang if lang != '' else None
		})
		self.thread_pool.start(worker)

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
		self.change_password_btn.setText('Send Token')
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
				popup.error(self, 'Password confirmation failed')
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
		popup.info(self, 'Check your email box for verification token')
		self.token_is_sent = True
		self.new_password_input.setEnabled(True)
		self.new_password_input.setFocus()
		self.new_password_repeat_input.setEnabled(True)
		self.verification_token_input.setEnabled(True)
		self.change_password_btn.setText('Change')
		self.change_password_btn.setEnabled(False)

	def change_password_success(self):
		self.reset_change_password_btn_click()
		self.cloud.remove_token()
		popup.info(self, 'New password has been set')

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
			err_msg = 'Updating user failure: unable to update user account, status {}'.format(err[1])
		except RequestTokenError:
			err_msg = 'Reset password failure: unable to request token, status {}'.format(err[1])
		except ResetPasswordError:
			err_msg = 'Reset password failure: unable to reset user password, status {}'.format(err[1])
		except (CloudStorageException, RequestException, Exception):
			err_msg = str(err[1])
		popup.error(self, err_msg)
