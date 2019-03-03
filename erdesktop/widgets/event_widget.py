from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


# noinspection PyArgumentList
class EventWidget(QWidget):

	def __init__(self, parent, event_data):
		super(EventWidget, self).__init__(parent)

		self.titleLabel = QLabel()

		self.parent = parent
		self.event_data = event_data

		self.setup_ui()

	def setup_ui(self):
		layout = QVBoxLayout()

		self.titleLabel.setText('{} | {}'.format(self.event_data.time[:5], self.event_data.title))
		layout.addWidget(self.titleLabel)

		self.setLayout(layout)
