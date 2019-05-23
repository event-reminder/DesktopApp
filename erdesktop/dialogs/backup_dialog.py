import os
from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import (
	QTabWidget, QFileDialog, QScrollArea, QListWidgetItem, QDialog,
	QLineEdit, QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel
)

from requests.exceptions import RequestException

from erdesktop.storage.models import EventModel
from erdesktop.util import Worker
from erdesktop.storage import Storage
from erdesktop.settings import Settings
from erdesktop.cloud import CloudStorage
from erdesktop.widgets import BackupWidget
from erdesktop.widgets.util import PushButton, popup
from erdesktop.widgets.waiting_spinner import WaitingSpinner
from erdesktop.util.exceptions import (
	BackupAlreadyExistsError, BackupDownloadingError, CloudStorageException,
	AuthRequiredError, UserRetrievingError, ReadingBackupsError, BackupDeletingError
)

import qtawesome as qta


class BackupDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super(BackupDialog, self).__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))
		self.setWindowFlags(Qt.Dialog)

		self.spinner = WaitingSpinner()

		self.thread_pool = QThreadPool()

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('BackupDialog: calendar is not set')

		self.storage = kwargs.get('storage', Storage())
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.setFixedSize(500, 320)
		self.setWindowTitle(self.tr('Backup and Restore'))

		self.backups_pool = []

		self.settings = Settings()

		self.backup_file_input = QLineEdit()
		self.restore_file_input = QLineEdit()

		self.backup_file_button = PushButton('', 40, 30, self.get_folder_path)
		self.restore_file_button = PushButton('', 40, 30, self.get_file_path)

		self.launch_restore_button = PushButton(self.tr('Start'), 120, 35, self.launch_restore_local)
		self.launch_backup_button = PushButton(self.tr('Start'), 120, 35, self.launch_backup_local)

		self.backups_cloud_list_widget = QListWidget()

		self.upload_backup_button = PushButton(' {}'.format(self.tr('Upload')), 120, 35, self.upload_backup_cloud)
		self.download_backup_button = PushButton(
			' {}'.format(self.tr('Download')),
			150 if self.settings.app_lang == 'uk_UA' else 120,
			35,
			self.download_backup_cloud
		)
		self.delete_backup_button = PushButton(' {}'.format(self.tr('Delete')), 120, 35, self.delete_backup_cloud)

		self.setup_ui()

		self.layout().addWidget(self.spinner)

	def showEvent(self, event):
		self.move(
			self.calendar.window().frameGeometry().topLeft() +
			self.calendar.window().rect().center() - self.rect().center()
		)
		self.refresh_backups_cloud()

		btn_color = 'white' if self.settings.is_dark_theme else 'black'
		self.backup_file_button.setIcon(qta.icon('mdi.folder-open', color=btn_color, scale_factor=1.5))
		self.restore_file_button.setIcon(qta.icon('mdi.file-plus', color=btn_color, scale_factor=1.5))

		self.upload_backup_button.setIcon(qta.icon('mdi.cloud-upload', color=btn_color, scale_factor=1.2))
		self.download_backup_button.setIcon(qta.icon('mdi.cloud-download', color=btn_color, scale_factor=1.2))
		self.delete_backup_button.setIcon(qta.icon('mdi.delete', color=btn_color, scale_factor=1.2))

		super(BackupDialog, self).showEvent(event)

	def setup_ui(self):
		tabs_widget = QTabWidget(self)
		tabs_widget.setMinimumWidth(self.width() - 22)

		self.setup_cloud_ui(tabs_widget)
		self.setup_local_ui(tabs_widget)

		content = QVBoxLayout()
		content.addWidget(tabs_widget, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_local_ui(self, tabs):
		local_backup_tab = QTabWidget(self)

		self.setup_local_backup_ui(local_backup_tab)
		self.setup_local_restore_ui(local_backup_tab)

		tabs.addTab(local_backup_tab, self.tr('Local'))

	def setup_local_backup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h2_layout = QHBoxLayout()

		# noinspection PyArgumentList
		h2_layout.addWidget(QLabel('{}:'.format(self.tr('Location'))))
		h2_layout.setContentsMargins(10, 0, 10, 20)
		if os.path.exists(self.settings.app_last_backup_path):
			self.backup_file_input.setText(self.settings.app_last_backup_path)

		# noinspection PyArgumentList
		h2_layout.addWidget(self.backup_file_input)

		# noinspection PyArgumentList
		h2_layout.addWidget(self.backup_file_button)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)
		label = QLabel(self.tr('Create full backup of your calendar notes'))
		label.setContentsMargins(0, 10, 0, 30)
		layout.addWidget(label, alignment=Qt.AlignCenter)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_backup_button, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Backup'))

	def setup_local_restore_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h2_layout = QHBoxLayout()

		# noinspection PyArgumentList
		h2_layout.addWidget(QLabel('{}:'.format(self.tr('Location'))))
		h2_layout.setContentsMargins(10, 0, 10, 20)
		if os.path.isfile(self.settings.app_last_restore_path):
			self.restore_file_input.setText(self.settings.app_last_restore_path)

		# noinspection PyArgumentList
		h2_layout.addWidget(self.restore_file_input)

		# noinspection PyArgumentList
		h2_layout.addWidget(self.restore_file_button)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)
		label = QLabel(self.tr('Restore all your calendar notes with backup file'))
		label.setWordWrap(True)
		label.setContentsMargins(0, 10, 0, 30)
		layout.addWidget(label, alignment=Qt.AlignCenter)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_restore_button, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Restore'))

	def get_folder_path(self):
		# noinspection PyArgumentList
		file_name = QFileDialog().getExistingDirectory(
			caption=self.tr('Select Directory'),
			directory=self.backup_file_input.text()
		)
		if len(file_name) > 0:
			self.backup_file_input.setText(str(file_name))

	def get_file_path(self):
		path = self.restore_file_input.text()

		# noinspection PyArgumentList
		file_name = QFileDialog().getOpenFileName(
			caption=self.tr('Open file'),
			directory=path if os.path.isfile(path) else './',
			filter='(*.bak)'
		)
		if len(file_name) > 0:
			self.restore_file_input.setText(file_name[0])

	def launch_restore_local(self):
		path = self.restore_file_input.text()
		self.settings.set_last_restore_path(path)
		self.exec_worker(self.storage.restore, self.launch_restore_local_success, None, *(path,))

	def launch_restore_local_success(self):
		self.calendar.update()
		self.calendar.settings_dialog.refresh_settings_values()
		popup.info(self, self.tr('Data has been restored'))

	def launch_backup_local(self):
		path = self.backup_file_input.text()
		self.settings.set_last_backup_path(path)
		self.exec_worker(self.storage.backup, self.launch_backup_local_success, None, *(
			path, self.settings.include_settings_backup
		))

	def launch_backup_local_success(self):
		popup.info(self, self.tr('Backup has been created'))

	def setup_cloud_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignBottom)

		buttons_layout = QHBoxLayout()

		center_buttons_layout = QHBoxLayout()
		center_buttons_layout.setAlignment(Qt.AlignLeft)
		self.upload_backup_button.setToolTip(self.tr('Upload'))
		self.upload_backup_button.setEnabled(False)
		center_buttons_layout.addWidget(self.upload_backup_button, alignment=Qt.AlignCenter)

		self.download_backup_button.setToolTip(self.tr('Download'))
		self.download_backup_button.setEnabled(False)
		center_buttons_layout.addWidget(self.download_backup_button, alignment=Qt.AlignCenter)
		buttons_layout.addLayout(center_buttons_layout)

		self.delete_backup_button.setEnabled(False)
		self.delete_backup_button.setToolTip(self.tr('Delete'))
		buttons_layout.addWidget(self.delete_backup_button, alignment=Qt.AlignRight)

		layout.addLayout(buttons_layout)

		scroll_view = QScrollArea()

		# noinspection PyUnresolvedReferences
		self.backups_cloud_list_widget.itemSelectionChanged.connect(self.selection_changed)
		scroll_view.setWidget(self.backups_cloud_list_widget)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedHeight(200)
		scroll_view.setFixedWidth(455)
		layout.addWidget(scroll_view, alignment=Qt.AlignLeft)

		tab.setLayout(layout)
		tabs.addTab(tab, self.tr('Cloud'))

	def selection_changed(self):
		if len(self.backups_cloud_list_widget.selectedItems()) > 0:
			self.delete_backup_button.setEnabled(True)
			self.download_backup_button.setEnabled(True)
		else:
			self.delete_backup_button.setEnabled(False)
			self.download_backup_button.setEnabled(False)

	def refresh_backups_cloud(self):
		self.backups_cloud_list_widget.clear()
		self.exec_worker(self.cloud.backups, None, self.refresh_backups_cloud_success)

	def refresh_backups_cloud_success(self, backups):
		self.upload_backup_button.setEnabled(True)
		for backup in backups:
			self.add_backup_widget(backup)

	def add_backup_widget(self, backup_data):
		num_repr = repr(backup_data['events_count'])
		if len(num_repr) > 1 and int(num_repr[-2]) == 1:
			text_label = self.tr('events')
		elif 1 < int(num_repr[-1]) < 5:
			text_label = self.tr('events*')
		else:
			text_label = self.tr('event{}'.format('s' if int(num_repr[-1]) > 1 or backup_data['events_count'] % 2 == 0 else ''))
		backup_widget = BackupWidget(
			flags=self.backups_cloud_list_widget.windowFlags(),
			parent=self.backups_cloud_list_widget,
			palette=self.palette(),
			font=self.font(),
			hash_sum=backup_data['digest'],
			title=datetime.strptime(backup_data['timestamp'], EventModel.TIMESTAMP_FORMAT).strftime(EventModel.DATE_TIME_FORMAT),
			description='{} {} {}, {}'.format(
				backup_data['backup_size'],
				backup_data['events_count'],
				text_label,
				self.tr('full backup') if backup_data['contains_settings'] is True else self.tr('excluded settings')
			)
		)
		list_widget_item = QListWidgetItem(self.backups_cloud_list_widget)
		list_widget_item.setSizeHint(backup_widget.sizeHint())
		self.backups_cloud_list_widget.addItem(list_widget_item)
		self.backups_cloud_list_widget.setItemWidget(list_widget_item, backup_widget)

	def upload_backup_cloud(self):
		self.exec_worker(self.upload_backup_cloud_run, self.upload_backup_cloud_success, None)

	def upload_backup_cloud_run(self):
		user = self.cloud.user()
		timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		backup_data = self.storage.prepare_backup_data(
			self.storage.to_array(), timestamp, self.settings.include_settings_backup, user['username']
		)
		self.cloud.upload_backup(backup_data)

	def upload_backup_cloud_success(self):
		self.refresh_backups_cloud()
		popup.info(self, self.tr('Backup was successfully uploaded to the cloud'))

	def download_backup_cloud(self):
		current = self.get_current_selected()
		if current is not None:
			self.exec_worker(self.download_backup_cloud_run, self.download_backup_cloud_success, None, *(current,))

	def download_backup_cloud_run(self, current):
		self.storage.restore_from_dict(self.cloud.download_backup(current.hash_sum))

	def download_backup_cloud_success(self):
		self.calendar.reset_palette(self.settings.app_theme)
		self.calendar.reset_font(QFont('SansSerif', self.settings.app_font))
		self.calendar.update()
		self.calendar.settings_dialog.refresh_settings_values()
		popup.info(self, self.tr('Backup was successfully downloaded. Restart application to enable all restored settings.'))

	def delete_backup_cloud(self):
		current = self.get_current_selected()
		if current is not None:
			self.exec_worker(self.cloud.delete_backup, self.delete_backup_cloud_success, None, *(current.hash_sum,))

	def delete_backup_cloud_success(self):
		self.refresh_backups_cloud()
		popup.info(self, self.tr('Backup was deleted successfully'))

	def get_current_selected(self):
		selected_items = self.backups_cloud_list_widget.selectedItems()
		if len(selected_items) > 0:
			return self.backups_cloud_list_widget.itemWidget(selected_items[0])
		return None

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
		except AuthRequiredError:
			err_msg = self.tr('Account access failure: authentication is required')
		except UserRetrievingError:
			err_msg = '{} {}'.format(
				self.tr('Reading account failure: unable to retrieve account information, status'), err[1]
			)
		except ReadingBackupsError:
			err_msg = '{} {}'.format(
				self.tr('Reading backups failure: unable to retrieve backups data from the server, status'), err[1]
			)
		except BackupAlreadyExistsError:
			err_msg = self.tr('Upload failure: backup already exists')
		except BackupDownloadingError:
			err_msg = self.tr('Download failure: unable to download backup')
		except BackupDeletingError:
			err_msg = self.tr('Deleting failure: unable to delete backup')
		except (CloudStorageException, RequestException, Exception):
			err_msg = str(err[1])
		popup.error(self, err_msg)
