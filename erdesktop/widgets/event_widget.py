from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


class EventWidget(QWidget):

	def __init__(self, parent, event_data):
		super(EventWidget, self).__init__(parent, flags=parent.windowFlags())

		self.titleLabel = QLabel()

		self.parent = parent
		self.event_data = event_data

		self.setup_ui()

	def setup_ui(self):
		layout = QVBoxLayout()

		self.titleLabel.setText('{} | {}'.format(self.event_data.time[:5], self.event_data.title))

		# noinspection PyArgumentList
		layout.addWidget(self.titleLabel)

		self.setLayout(layout)
