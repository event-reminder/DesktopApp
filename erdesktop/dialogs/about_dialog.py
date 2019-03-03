from erdesktop.cloud import CloudStorage
from erdesktop.settings import Settings, APP_ORGANIZATION, APP_NAME, APP_VERSION, APP_RELEASE_DATE

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QHBoxLayout


class AboutDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)
		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		self.setFixedSize(500, 250)
		self.setWindowTitle('Legal Information')
		self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('AboutDialog: calendar is not set')

		self.settings = Settings()
		self.setup_ui()

	def showEvent(self, event):
		self.move(
			self.calendar.window().frameGeometry().topLeft() +
			self.calendar.window().rect().center() - self.rect().center()
		)
		super(AboutDialog, self).showEvent(event)

	def setup_ui(self):
		content = QVBoxLayout()

		title_section = QHBoxLayout()
		title_section.setContentsMargins(0, 0, 0, 30)
		title_section.setSpacing(20)
		logo_image = QLabel()
		logo_image.setPixmap(QPixmap(self.settings.app_icon(
			is_dark=not self.settings.is_dark_theme, q_icon=False, icon_size='medium'))
		)
		logo_image.setFixedSize(QSize(70, 70))
		# noinspection PyArgumentList
		title_section.addWidget(logo_image)
		name_label = QLabel(APP_NAME)
		name_label.setFont(QFont('SansSerif', 26))
		title_section.addWidget(name_label, alignment=Qt.AlignVCenter)

		bold_font = QFont('SansSerif', 11)
		bold_font.setBold(True)

		data_section = QVBoxLayout()
		data_section.setSpacing(0)
		version_label = QLabel('{} {}'.format(APP_NAME, APP_VERSION))
		version_label.setFont(bold_font)
		data_section.addWidget(version_label, alignment=Qt.AlignTop)
		data_section.addWidget(
			QLabel('Released on {}'.format(APP_RELEASE_DATE)),
			alignment=Qt.AlignTop
		)

		try:
			user = CloudStorage().user()
			data_section.addWidget(
				QLabel('Copy of this software is distributed to {}.'.format(user.get('username'))),
				alignment=Qt.AlignTop
			)
		except Exception as exc:
			print(exc)

		content.addLayout(title_section)
		content.addLayout(data_section)
		content.addWidget(
			QLabel('Copyright (c) 2019 {}'.format(APP_ORGANIZATION)),
			alignment=Qt.AlignBottom
		)

		self.setLayout(content)
