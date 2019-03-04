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
		self.hash_sum_label = QLabel()

		self.hash_sum = kwargs.get('hash_sum')
		self.title = kwargs.get('title')

		self.setup_ui()

	def setup_ui(self):
		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignLeft)
		self.title_label.setText(self.title)
		layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
		self.hash_sum_label.setText(self.hash_sum)
		self.hash_sum_label.setStyleSheet('color: gray')
		layout.addWidget(self.hash_sum_label, alignment=Qt.AlignLeft)
		self.setLayout(layout)
