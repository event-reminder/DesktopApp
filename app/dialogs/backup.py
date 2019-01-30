from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import Settings
from app.utils import create_button


# noinspection PyArgumentList,PyUnresolvedReferences
class BackupDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs['calendar']
		self.storage = kwargs['storage']

		self.setFixedSize(450, 270)
		self.setWindowTitle('Backup and Restore')

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
		self.setup_local_backup(tabs_widget)
		self.setup_local_restore(tabs_widget)
		self.setup_cloud(tabs_widget)
		content.addWidget(tabs_widget, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_local_backup(self, tabs):
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
		h2_layout.addWidget(self.backup_file_input)
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

	def setup_local_restore(self, tabs):
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

	def setup_cloud(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)

		layout.addWidget(QLabel('Coming soon...'))

		tab.setLayout(layout)
		tabs.addTab(tab, 'Cloud')

	def get_folder_path(self):
		dialog = QFileDialog()
		file_name = dialog.getExistingDirectory(caption='Select Directory')
		self.backup_file_input.setText(str(file_name))

	def get_file_path(self):
		dialog = QFileDialog()
		file_name = dialog.getOpenFileName(caption='Open file', directory='/home', filter='(*.bak)')
		if len(file_name) > 0:
			self.restore_file_input.setText(file_name[0])

	def launch_restore(self):
		self.storage.restore(self.restore_file_input.text(), self.include_settings_restore.isChecked())
		self.calendar.update()

	def launch_backup(self):
		self.storage.backup(self.backup_file_input.text(), self.include_settings_backup.isChecked())
