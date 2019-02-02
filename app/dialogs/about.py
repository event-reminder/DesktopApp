import getpass

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import Settings


# noinspection PyArgumentList,PyUnresolvedReferences
class AboutDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))

		self.calendar = kwargs['calendar']
		self.storage = kwargs['storage']

		self.setFixedSize(600, 400)
		self.setWindowTitle('About')

		self.settings = Settings()

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()

		name_label = QLabel(self.settings.app_name)
		name_label.setFont(QFont('SansSerif', 18))

		content.addWidget(name_label)

		content.addWidget(QLabel('{} {}'.format(self.settings.app_name, self.settings.app_version)))
		content.addWidget(QLabel('Build #{}, built on {}'.format(
			self.settings.app_build_number, self.settings.app_build_date))
		)

		self.setLayout(content)
