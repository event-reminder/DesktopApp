import getpass
import requests
from datetime import datetime

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import Settings
from app.cloud import CloudStorage
from app.widgets.backup_widget import BackupWidget
from app.util import popup, logger, log_msg, button, Worker
from app.widgets.waiting_spinner import WaitingSpinner


# noinspection PyArgumentList,PyUnresolvedReferences
class BackupDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.spinner = WaitingSpinner()

		self.thread_pool = QThreadPool()

		self.calendar = kwargs['calendar']
		self.storage = kwargs['storage']
		self.cloud = kwargs.get('cloud_storage', CloudStorage())

		self.setFixedSize(500, 320)
		self.setWindowTitle('Backup and Restore')

		self.search_dir = '/home/{}'.format(getpass.getuser())

		self.settings = Settings()

		self.backup_file_input = QLineEdit()
		self.restore_file_input = QLineEdit()

		self.backup_file_button = button('+', 40, 30, self.get_folder_path)
		self.restore_file_button = button('+', 40, 30, self.get_file_path)

		self.launch_restore_button = button('Start', 100, 35, self.launch_restore_local)
		self.launch_backup_button = button('Start', 100, 35, self.launch_backup_local)

		self.backups_cloud_list_widget = QListWidget()

		self.upload_backup_button = button('Upload', 80, 35, self.upload_backup_cloud)
		self.download_backup_button = button('Download', 110, 35, self.download_backup_cloud)
		self.delete_backup_button = button('Delete', 80, 35, self.delete_backup_cloud)

		self.setup_ui()

		self.layout().addWidget(self.spinner)

	def showEvent(self, event):
		self.refresh_backups_cloud()
		super().showEvent(event)

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

		tabs.addTab(local_backup_tab, 'Local')

	def setup_local_backup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h2_layout = QHBoxLayout()
		h2_layout.addWidget(QLabel('Location:'))
		h2_layout.setContentsMargins(10, 0, 10, 20)
		self.backup_file_input.setText(self.search_dir)
		h2_layout.addWidget(self.backup_file_input)
		self.backup_file_button.setIcon(QIcon().fromTheme('folder'))
		h2_layout.addWidget(self.backup_file_button)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)
		label = QLabel('Create full backup of your calendar notes')
		label.setContentsMargins(0, 10, 0, 30)
		layout.addWidget(label, alignment=Qt.AlignCenter)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_backup_button, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Backup')

	def setup_local_restore_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h2_layout = QHBoxLayout()
		h2_layout.addWidget(QLabel('Location:'))
		h2_layout.setContentsMargins(10, 0, 10, 20)
		h2_layout.addWidget(self.restore_file_input)
		self.restore_file_button.setIcon(QIcon().fromTheme('document-open'))
		h2_layout.addWidget(self.restore_file_button)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)
		label = QLabel('Restore all your calendar notes with backup file')
		label.setContentsMargins(0, 10, 0, 30)
		layout.addWidget(label, alignment=Qt.AlignCenter)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_restore_button, alignment=Qt.AlignCenter)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Restore')

	def get_folder_path(self):
		file_name = QFileDialog().getExistingDirectory(caption='Select Directory', directory=self.search_dir)
		if len(file_name) > 0:
			self.backup_file_input.setText(str(file_name))

	def get_file_path(self):
		file_name = QFileDialog().getOpenFileName(caption='Open file', directory=self.search_dir, filter='(*.bak)')
		if len(file_name) > 0:
			self.restore_file_input.setText(file_name[0])

	def launch_restore_local(self):
		self.spinner.start()
		worker = Worker(self.storage.restore, *(self.restore_file_input.text(),))
		worker.err_format = 'Can\'t restore backup: {}'
		worker.signals.success.connect(self.launch_restore_local_success)
		worker.signals.error.connect(self.popup_error)
		worker.signals.finished.connect(self.stop_spinner)
		self.thread_pool.start(worker)

	def launch_restore_local_success(self):
		self.calendar.update()
		self.calendar.settings_dialog.refresh_settings_values()

	def launch_backup_local(self):
		self.spinner.start()
		worker = Worker(self.storage.backup, *(self.backup_file_input.text(), self.settings.include_settings_backup))
		worker.err_format = 'Can\'t backup calendar data: {}'
		worker.signals.error.connect(self.popup_error)
		worker.signals.finished.connect(self.stop_spinner)
		self.thread_pool.start(worker)

	def setup_cloud_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignBottom)

		buttons_layout = QHBoxLayout()

		center_buttons_layout = QHBoxLayout()
		center_buttons_layout.setAlignment(Qt.AlignLeft)
		self.upload_backup_button.setToolTip('Upload')
		self.upload_backup_button.setEnabled(False)
		center_buttons_layout.addWidget(self.upload_backup_button, alignment=Qt.AlignCenter)
		self.download_backup_button.setToolTip('Download')
		self.download_backup_button.setEnabled(False)
		center_buttons_layout.addWidget(self.download_backup_button, alignment=Qt.AlignCenter)
		buttons_layout.addLayout(center_buttons_layout)

		self.delete_backup_button.setEnabled(False)
		self.delete_backup_button.setToolTip('Delete')
		buttons_layout.addWidget(self.delete_backup_button, alignment=Qt.AlignRight)

		layout.addLayout(buttons_layout)

		scroll_view = QScrollArea()
		self.backups_cloud_list_widget.itemSelectionChanged.connect(self.selection_changed)
		scroll_view.setWidget(self.backups_cloud_list_widget)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedHeight(200)
		scroll_view.setFixedWidth(455)
		layout.addWidget(scroll_view, alignment=Qt.AlignLeft)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Cloud')

	def selection_changed(self):
		if self.backups_cloud_list_widget.currentItem() is not None:
			self.delete_backup_button.setEnabled(True)
			self.download_backup_button.setEnabled(True)
		else:
			self.delete_backup_button.setEnabled(False)
			self.download_backup_button.setEnabled(False)

	def refresh_backups_cloud(self):
		self.backups_cloud_list_widget.clear()
		worker = Worker(self.cloud.validate_token)
		worker.signals.success.connect(self.refresh_backups_cloud_success)
		worker.signals.error.connect(self.popup_error)
		self.thread_pool.start(worker)

	def refresh_backups_cloud_success(self):
		self.upload_backup_button.setEnabled(True)
		backups = self.cloud.backups()
		for backup in backups:
			self.add_backup_widget(backup)

	def add_backup_widget(self, backup_data):
		backup_widget = BackupWidget(
			flags=self.backups_cloud_list_widget.windowFlags(),
			parent=self.backups_cloud_list_widget,
			palette=self.palette(),
			font=self.font(),
			hash_sum=backup_data['digest'],
			title=backup_data['timestamp']
		)
		list_widget_item = QListWidgetItem(self.backups_cloud_list_widget)
		list_widget_item.setSizeHint(backup_widget.sizeHint())
		self.backups_cloud_list_widget.addItem(list_widget_item)
		self.backups_cloud_list_widget.setItemWidget(list_widget_item, backup_widget)

	def upload_backup_cloud(self):
		worker = Worker(self.upload_backup_cloud_run)
		worker.signals.error.connect(self.popup_error)
		worker.signals.success.connect(self.upload_backup_cloud_success)
		worker.signals.finished.connect(self.stop_spinner)
		self.thread_pool.start(worker)

	def upload_backup_cloud_run(self):
		self.spinner.start()
		timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		self.storage.connect()
		backup_data = self.storage.prepare_backup_data(
			self.storage.to_array(), timestamp, self.settings.include_settings_backup
		)
		self.cloud.upload_backup(backup_data)

	def upload_backup_cloud_success(self):
		self.refresh_backups_cloud()
		self.stop_spinner()
		popup.info(self, 'Backup was successfully uploaded to the cloud.')

	def download_backup_cloud(self):
		current = self.get_current_selected()
		if current is not None:
			self.spinner.start()
			worker = Worker(self.download_backup_cloud_run, *(current,))
			worker.signals.success.connect(self.download_backup_cloud_success)
			worker.signals.finished.connect(self.stop_spinner)
			worker.signals.error.connect(self.popup_error)
			self.thread_pool.start(worker)

	def download_backup_cloud_run(self, current):
		self.storage.restore_from_dict(
			self.cloud.download_backup(current.hash_sum)
		)

	def download_backup_cloud_success(self):
		self.calendar.reset_palette(self.settings.app_theme)
		self.calendar.reset_font(QFont('SansSerif', self.settings.app_font))
		self.calendar.update()
		self.calendar.settings_dialog.refresh_settings_values()
		popup.info(self, 'Backup was successfully downloaded.')

	def delete_backup_cloud(self):
		current = self.get_current_selected()
		if current is not None:
			self.spinner.start()
			worker = Worker(self.cloud.delete_backup, *(current.hash_sum,))
			worker.signals.success.connect(self.delete_backup_cloud_success)
			worker.signals.finished.connect(self.stop_spinner)
			worker.signals.error.connect(self.popup_error)
			self.thread_pool.start(worker)

	def delete_backup_cloud_success(self):
		self.refresh_backups_cloud()
		popup.info(self, 'Backup was deleted successfully.')

	def get_current_selected(self):
		current = self.backups_cloud_list_widget.currentItem()
		if current is not None:
			return self.backups_cloud_list_widget.itemWidget(current)
		return None

	def stop_spinner(self):
		self.spinner.stop()

	def popup_error(self, err):
		popup.error(self, '{}'.format(err[1]))
