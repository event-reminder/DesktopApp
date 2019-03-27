from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


class EventWidget(QWidget):

	def __init__(self, parent, event_data):
		super(EventWidget, self).__init__(parent, flags=parent.windowFlags())

		self.parent = parent
		self.event_data = event_data

		self.setMaximumWidth(parent.width())

		self.setContentsMargins(0, 0, 0, 0)

		self.setup_ui()

	def setup_ui(self):
		layout = QVBoxLayout()

		title_label = QLabel()
		title_label.setWordWrap(True)
		title_label.setText('{} | {}'.format(self.event_data.time.strftime('%H:%M'), self.event_data.title))

		# noinspection PyArgumentList
		layout.addWidget(title_label)

		if self.event_data.description is not None and len(self.event_data.description) != 0:
			description_label = QLabel()
			description_label.setWordWrap(True)
			description_label.setText(self.event_data.description)

			# noinspection PyArgumentList
			layout.addWidget(QLabel(''))

			# noinspection PyArgumentList
			layout.addWidget(description_label)

		self.setLayout(layout)
