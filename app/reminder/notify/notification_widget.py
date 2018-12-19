from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils.creator import new_button
from app.settings.app_settings import APP_ICON


class NotificationWidget(QWidget):

	def __init__(self, title, description, timeout):
		super().__init__(flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setup_ui(title, description)
		self.timer = QTimer()
		self.timer.timeout.connect(self.close)  # TODO: check if only notification widget is closed
		self.timeout = timeout
		self.__add_timer()

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

		right_layout.addWidget(new_button('Close', 100, 50, self.close), alignment=Qt.AlignRight | Qt.AlignBottom)

		main_layout.addLayout(right_layout)
		self.setLayout(main_layout)

	def enterEvent(self, event):
		super().enterEvent(event)

		self.__rm_timer()
		# TODO: stop timer

	def leaveEvent(self, event):
		super().leaveEvent(event)

		self.__add_timer()
		# TODO: start timer

	def __add_timer(self):
		self.timer.start(self.timeout)

	def __rm_timer(self):
		self.timer.stop()
