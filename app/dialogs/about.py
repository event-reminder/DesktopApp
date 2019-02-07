import platform

from app.settings import Settings

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QHBoxLayout


class AboutDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)
		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		self.setFixedSize(500, 250)
		self.setWindowTitle('About')
		self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

		self.settings = Settings()
		self.setup_ui()

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
		name_label = QLabel(self.settings.app_name)
		name_label.setFont(QFont('SansSerif', 26))
		title_section.addWidget(name_label, alignment=Qt.AlignVCenter)

		bold_font = QFont('SansSerif', 11)
		bold_font.setBold(True)

		data_section = QVBoxLayout()
		data_section.setSpacing(0)
		version_label = QLabel('{} {}'.format(self.settings.app_name, self.settings.app_version))
		version_label.setFont(bold_font)
		data_section.addWidget(version_label, alignment=Qt.AlignTop)
		data_section.addWidget(
			QLabel('Built on {}'.format(self.settings.app_build_date)),
			alignment=Qt.AlignTop
		)
		data_section.addWidget(
			QLabel('Copy of this software is distributed to {}.'.format(platform.node())),
			alignment=Qt.AlignTop
		)

		content.addLayout(title_section)
		content.addLayout(data_section)
		content.addWidget(
			QLabel('Copyright (c) 2019 {}'.format(self.settings.app_organization)),
			alignment=Qt.AlignBottom
		)

		self.setLayout(content)
