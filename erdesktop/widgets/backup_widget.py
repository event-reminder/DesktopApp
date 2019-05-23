from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


class BackupWidget(QWidget):

	def __init__(self, parent, flags, **kwargs):
		super().__init__(parent, flags)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.title_label = QLabel()
		self.description_label = QLabel()

		self.description = kwargs.get('description')
		self.title = kwargs.get('title')
		self.hash_sum = kwargs.get('hash_sum')

		self.setup_ui()

	def setup_ui(self):
		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignLeft)
		self.title_label.setText(self.title)
		layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
		self.description_label.setText(self.description)
		self.description_label.setStyleSheet('color: gray')
		layout.addWidget(self.description_label, alignment=Qt.AlignLeft)
		self.setLayout(layout)
