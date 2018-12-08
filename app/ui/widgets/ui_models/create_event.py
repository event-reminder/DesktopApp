from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from datetime import datetime, timedelta

from app.ui.utils import popup
from app.ui.utils.creator import new_button


class CreateEventDialogUI:

	def __init__(self, parent, save_event_handler):
		self.save_event_handler = save_event_handler
		self.parent = parent
		self.parent.setFixedSize(500, 400)

		self.title_input = QLineEdit(self.parent)
		self.description_input = QTextEdit(self.parent)
		self.date_input = QDateEdit(self.parent)
		self.date_input.setEnabled(False)
		self.time_input = QTimeEdit(self.parent)

		self.parent.setLayout(self.get_content())

	def get_content(self):
		content = QVBoxLayout()
		content.addWidget(QLabel('Title:'), alignment=Qt.AlignLeft)
		content.addWidget(self.title_input)
		content.addWidget(QLabel('Description (optional):'), alignment=Qt.AlignLeft)
		content.addWidget(self.description_input)
		content.addWidget(QLabel('Date:'), alignment=Qt.AlignLeft)
		content.addWidget(self.date_input)
		content.addWidget(QLabel('Time:'), alignment=Qt.AlignLeft)
		content.addWidget(self.time_input)
		btn_save = new_button('Save', 100, 50, self.save_btn_click)
		content.addWidget(btn_save, 0, Qt.AlignRight)
		return content

	def reset_inputs(self, date):
		self.parent.setWindowTitle('New Event | {}'.format(date.toPyDate().strftime('%Y-%m-%d')))
		self.date_input.setDate(QDate(date))
		curr_time = (datetime.now() + timedelta(minutes=3)).time().replace(second=0, microsecond=0)
		self.time_input.setTime(QTime(curr_time))
		self.title_input.setText('')
		self.description_input.setText('')

	def validate_inputs(self):
		if len(self.title_input.text()) < 1:
			popup.warning(self.parent, 'Provide title for the event!')
			return False
		if self.date_input.date().toPyDate() < datetime.now().date():
			popup.warning(self.parent, 'Can\'t set past event, check date input')
			return False
		if self.time_input.time().toPyTime() < datetime.now().time() and \
			self.date_input.date().toPyDate() == datetime.now().date():
			popup.warning(self.parent, 'Can\'t set past event, check time input')
			return False
		return True

	def save_btn_click(self):
		if self.validate_inputs():
			self.save_event_handler(
				self.title_input.text(),
				self.date_input.date().toPyDate(),
				self.time_input.time().toPyTime(),
				self.description_input.toPlainText()
			)
			popup.info(self.parent, 'Save successfully!')
			self.parent.close()