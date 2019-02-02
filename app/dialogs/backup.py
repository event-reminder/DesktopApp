import getpass

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.utils import (
	logger,
	log_msg,
	create_button
)
from app.utils import popup
from app.settings import Settings


# noinspection PyArgumentList,PyUnresolvedReferences
class BackupDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.calendar = kwargs['calendar']
		self.storage = kwargs['storage']

		self.setFixedSize(500, 300)
		self.setWindowTitle('Backup and Restore')

		self.search_dir = '/home/{}'.format(getpass.getuser())

		self.settings = Settings()

		self.include_settings_backup = QCheckBox()
		self.include_settings_restore = QCheckBox()

		self.backup_file_input = QLineEdit()
		self.restore_file_input = QLineEdit()

		self.backup_file_button = create_button('+', 30, 30, self.get_folder_path)
		self.restore_file_button = create_button('+', 30, 30, self.get_file_path)

		self.launch_restore_button = create_button('Launch', 70, 30, self.launch_restore)
		self.launch_backup_button = create_button('Launch', 70, 30, self.launch_backup)

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()
		tabs_widget = QTabWidget(self)
		tabs_widget.setMinimumWidth(self.width() - 22)
		self.setup_local_backup_ui(tabs_widget)
		self.setup_local_restore_ui(tabs_widget)
		self.setup_cloud_ui(tabs_widget)
		content.addWidget(tabs_widget, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_local_backup_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h1_layout = QHBoxLayout()
		h1_layout.setContentsMargins(10, 10, 10, 20)
		h1_layout.setAlignment(Qt.AlignCenter)
		h1_layout.setSpacing(20)
		h1_layout.addWidget(QLabel('Include settings'))
		self.include_settings_backup.setChecked(True)
		h1_layout.addWidget(self.include_settings_backup)

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
		layout.addLayout(h1_layout)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_backup_button)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Backup')

	def setup_local_restore_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		h1_layout = QHBoxLayout()
		h1_layout.setContentsMargins(10, 10, 10, 20)
		h1_layout.setAlignment(Qt.AlignCenter)
		h1_layout.setSpacing(20)
		h1_layout.addWidget(QLabel('Include settings'))
		self.include_settings_restore.setChecked(True)
		h1_layout.addWidget(self.include_settings_restore)

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
		layout.addLayout(h1_layout)
		layout.addLayout(h2_layout)
		layout.addWidget(self.launch_restore_button)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Restore')

	def setup_cloud_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)

		layout.addWidget(QLabel('Coming soon...'))

		tab.setLayout(layout)
		tabs.addTab(tab, 'Cloud')

	def get_folder_path(self):
		file_name = QFileDialog().getExistingDirectory(caption='Select Directory', directory=self.search_dir)
		if len(file_name) > 0:
			self.backup_file_input.setText(str(file_name))

	def get_file_path(self):
		file_name = QFileDialog().getOpenFileName(caption='Open file', directory=self.search_dir, filter='(*.bak)')
		if len(file_name) > 0:
			self.restore_file_input.setText(file_name[0])

	def launch_restore(self):
		try:
			self.storage.restore(self.restore_file_input.text(), self.include_settings_restore.isChecked())
			self.calendar.update()
		except Exception as exc:
			logger.error(log_msg(exc))
			popup.error(self, 'Can\'t restore backup: {}'.format(exc))

	def launch_backup(self):
		try:
			self.storage.backup(self.backup_file_input.text(), self.include_settings_backup.isChecked())
		except Exception as exc:
			logger.error(log_msg(exc))
			popup.error(self, 'Can\'t backup calendar data: {}'.format(exc))
