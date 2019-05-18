from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtWidgets import (
	QDialog, QLineEdit, QCheckBox, QComboBox, QVBoxLayout,
	QHBoxLayout, QWidget, QGridLayout, QLabel, QTabWidget
)

from requests.exceptions import RequestException

from erdesktop.util import Worker
from erdesktop.system import autostart
from erdesktop.cloud import CloudStorage
from erdesktop.widgets.util import PushButton, popup
from erdesktop.widgets.waiting_spinner import WaitingSpinner
from erdesktop.settings import (
	Settings, FONT_LARGE, FONT_SMALL, FONT_NORMAL, AVAILABLE_LANGUAGES,
	AVAILABLE_LANGUAGES_IDX, UNIT_MINUTES, UNIT_HOURS, UNIT_DAYS, UNIT_WEEKS
)
from erdesktop.util.exceptions import (
	UserUpdatingError, RequestTokenError, ResetPasswordError, CloudStorageException, AutoStartIsNotSupportedError
)


class SettingsDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super(SettingsDialog, self).__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('SettingsDialog: calendar is not set')

		self.settings = Settings()

		if self.settings.app_lang == 'en_US':
			self.setFixedSize(600, 450)
		else:
			self.setFixedSize(650, 450)
		self.setWindowTitle(self.tr('Settings'))
		self.setWindowFlags(Qt.Dialog)

		self.spinner = WaitingSpinner()
		self.thread_pool = QThreadPool()
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.font_combo_box = QComboBox()
		self.start_in_tray_check_box = QCheckBox()
		self.theme_combo_box = QComboBox()

		self.remove_after_time_up_check_box = QCheckBox()
		self.notification_duration_input = QLineEdit()
		self.remind_time_before_event_input = QLineEdit()
		self.remind_time_units_combo_box = QComboBox()

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
			self.tr('Send confirmation'), btn_width, 30, self.change_password_btn_click
		)

		self.run_with_system_start_check_box = QCheckBox()

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
		self.backups_number_input.setText(str(self.settings.app_max_backups))
		worker = Worker(self.load_max_backups)
		worker.signals.param_success.connect(self.load_max_backups_success)
		self.thread_pool.start(worker)
		super(SettingsDialog, self).showEvent(event)

	def load_max_backups(self):
		return self.cloud.user()['max_backups']

	def load_max_backups_success(self, result):
		self.backups_number_input.setText(str(result))

	def refresh_settings_values(self):
		self.theme_combo_box.setCurrentIndex(1 if self.settings.is_dark_theme else 0)
		curr_idx = 0
		if self.settings.app_font == FONT_NORMAL:
			curr_idx = 1
		elif self.settings.app_font == FONT_LARGE:
			curr_idx = 2
		self.font_combo_box.setCurrentIndex(curr_idx)
		self.start_in_tray_check_box.setChecked(self.settings.start_in_tray)
		self.run_with_system_start_check_box.setChecked(self.settings.run_with_system_start)

		self.include_settings_backup_check_box.setChecked(self.settings.include_settings_backup)
		self.remove_after_time_up_check_box.setChecked(self.settings.remove_event_after_time_up)
		self.notification_duration_input.setText(str(self.settings.notification_duration))
		self.remind_time_before_event_input.setText(str(self.settings.remind_time_before_event()))
		self.remind_time_units_combo_box.setCurrentIndex(self.settings.remind_time_unit)

	def setup_ui(self):
		content = QVBoxLayout()
		tab_widget = QTabWidget(self)
		tab_widget.setMinimumWidth(self.width() - 22)
		self.setup_app_settings_ui(tab_widget)
		self.setup_events_settings_ui(tab_widget)
		self.setup_account_settings_ui(tab_widget)
		content.addWidget(tab_widget, alignment=Qt.AlignLeft)
		self.setLayout(content)

	# noinspection PyUnresolvedReferences,PyArgumentList
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

		layout.addWidget(QLabel(self.tr('Start in tray')), 2, 0)
		self.start_in_tray_check_box.stateChanged.connect(self.start_in_tray_changed)
		layout.addWidget(self.start_in_tray_check_box, 2, 1)

		layout.addWidget(QLabel(self.tr('Backup settings')), 4, 0)
		self.include_settings_backup_check_box.stateChanged.connect(self.include_settings_backup_changed)
		layout.addWidget(self.include_settings_backup_check_box, 4, 1)

		layout.addWidget(QLabel(self.tr('Run with system start')), 5, 0)
		self.run_with_system_start_check_box.stateChanged.connect(self.run_with_system_start_changed)
		layout.addWidget(self.run_with_system_start_check_box, 5, 1)

		layout.addWidget(QLabel(self.tr('Language (restart required)')), 6, 0)
		self.lang_combo_box.addItems(AVAILABLE_LANGUAGES.keys())
		try:
			idx = AVAILABLE_LANGUAGES_IDX[self.settings.app_lang]
		except KeyError:
			idx = 0
		self.lang_combo_box.setCurrentIndex(idx)
		self.lang_combo_box.currentIndexChanged.connect(self.lang_changed)
		layout.addWidget(self.lang_combo_box, 6, 1)

		layout.addWidget(QLabel(self.tr('Maximum backups number')), 7, 0)
		self.backups_number_input.setValidator(QIntValidator())
		self.backups_number_input.textChanged.connect(self.max_backups_changed)
		layout.addWidget(self.backups_number_input, 7, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('App'))

	# noinspection PyUnresolvedReferences,PyArgumentList
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
		self.notification_duration_input.setMaxLength(3)
		self.notification_duration_input.textChanged.connect(self.notification_duration_changed)
		layout.addWidget(self.notification_duration_input, 1, 1)

		layout.addWidget(QLabel(self.tr('Notify before event')), 2, 0)
		self.remind_time_before_event_input.setValidator(QIntValidator())
		self.remind_time_before_event_input.setMaxLength(2)
		self.remind_time_before_event_input.textChanged.connect(self.remind_time_before_event_changed)
		layout.addWidget(self.remind_time_before_event_input, 2, 1)

		self.remind_time_units_combo_box.currentIndexChanged.connect(self.remind_time_units_changed)
		self.remind_time_units_combo_box.addItems(
			[self.tr(UNIT_MINUTES), self.tr(UNIT_HOURS), self.tr(UNIT_DAYS), self.tr(UNIT_WEEKS)]
		)
		layout.addWidget(self.remind_time_units_combo_box, 2, 2)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Events'))

	@staticmethod
	def create_field(title, enabled, func, field_input):
		layout = QVBoxLayout()
		layout.setContentsMargins(50, 0, 50, 10)

		# noinspection PyArgumentList
		layout.addWidget(QLabel('{}:'.format(title)))
		field_input.textChanged.connect(func)
		field_input.setEnabled(enabled)

		# noinspection PyArgumentList
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
			self.create_field(self.tr('New password'), False, self.change_password_inputs_changed, self.new_password_input)
		)

		self.new_password_repeat_input.setEchoMode(QLineEdit.Password)
		layout.addLayout(
			self.create_field(
				self.tr('Repeat password'), False, self.change_password_inputs_changed, self.new_password_repeat_input
			)
		)

		layout.addLayout(
			self.create_field(
				self.tr('Confirmation code'), False, self.change_password_inputs_changed, self.verification_token_input
			)
		)

		h_layout = QHBoxLayout()
		self.change_password_btn.setEnabled(False)

		# noinspection PyArgumentList
		h_layout.addWidget(self.change_password_btn)
		btn_width = 150
		if self.settings.app_lang != 'en_US':
			btn_width = 200
		reset_change_password_btn = PushButton(
			self.tr('Reset inputs'), btn_width, 30, self.reset_change_password_btn_click
		)

		# noinspection PyArgumentList
		h_layout.addWidget(reset_change_password_btn)
		layout.addLayout(h_layout)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Reset password'))

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

	def remind_time_units_changed(self, current):
		if self.ui_is_loaded:
			self.settings.set_remind_time_unit(current)

	def start_in_tray_changed(self):
		if self.ui_is_loaded:
			self.settings.set_start_in_tray(self.start_in_tray_check_box.isChecked())

	def run_with_system_start_changed(self):
		if self.ui_is_loaded:
			try:
				val = self.run_with_system_start_check_box.isChecked()
				if val:
					autostart.add()
				else:
					autostart.remove()
				self.settings.set_run_with_system_start(val)
			except AutoStartIsNotSupportedError as exc:
				popup.error(self, self.tr('Auto start setting is not supported on {}').format(exc))

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
		self.change_password_btn.setText(self.tr('Send confirmation'))
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
					None,
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
				None,
				*(self.email_input.text(),)
			)

	def change_password_request_token_success(self):
		popup.info(self, self.tr('Check your email box for confirmation code'))
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
		self.token_is_sent = False
		popup.info(self, self.tr('New password has been set'))

	def exec_worker(self, fn, fn_success, fn_param_success, *args, **kwargs):
		self.spinner.start()
		worker = Worker(fn, *args, **kwargs)
		if fn_success is not None:
			worker.signals.success.connect(fn_success)
		if fn_param_success is not None:
			worker.signals.param_success.connect(fn_param_success)
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
