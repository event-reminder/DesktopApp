from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils.creator import new_button
from app.settings.app_settings import APP_ICON


class NotificationWidget(QWidget):

	def __init__(self, title, description):
		super().__init__(flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setup_ui(title, description)

	def setup_ui(self, title, description):
		main_layout = QHBoxLayout()

		app_icon = QLabel(self)
		pix_map = QPixmap(APP_ICON)
		pix_map = pix_map.scaledToWidth(50)
		pix_map = pix_map.scaledToHeight(50)
		app_icon.setPixmap(pix_map)

		main_layout.addWidget(app_icon)
		right_layout = QVBoxLayout()

		title_label = QLabel(title)
		font_bold = QFont()
		font_bold.setBold(True)
		title_label.setFont(font_bold)

		right_layout.addWidget(title_label)

		description_label = QLabel(description)
		description_label.setWordWrap(True)

		right_layout.addWidget(description_label)

		right_layout.addWidget(new_button('Close', 100, 50, self.hide), alignment=Qt.AlignRight | Qt.AlignBottom)

		main_layout.addLayout(right_layout)
		self.setLayout(main_layout)

	def enterEvent(self, event):
		super().enterEvent(event)

		# TODO: stop timer

	def leaveEvent(self, event):
		super().leaveEvent(event)

		# TODO: start timer
