from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout

from app.ui.utils.creator import new_button
from app.settings.custom_settings import IS_DARK_THEME
from app.settings.app_settings import APP_ICON_LIGHT, APP_ICON_DARK


class NotificationUI:

	def __init__(self, title, description, parent, close_event):
		self.parent = parent
		self.close_event = close_event
		self.setup_ui(title, description)

	def setup_ui(self, title, description):
		main_layout = QHBoxLayout()

		app_icon = QLabel(self.parent)
		pix_map = QPixmap(APP_ICON_LIGHT if IS_DARK_THEME else APP_ICON_DARK)
		pix_map = pix_map.scaledToWidth(50)
		pix_map = pix_map.scaledToHeight(50)
		app_icon.setPixmap(pix_map)
		app_icon.setMargin(10)

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

		right_layout.addWidget(new_button('Close', 100, 50, self.close_event), alignment=Qt.AlignRight | Qt.AlignBottom)

		main_layout.addLayout(right_layout)
		self.parent.setLayout(main_layout)
