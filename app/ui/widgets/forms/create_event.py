from PyQt5.QtCore import (
	Qt,
	QDate,
	QTime
)
from PyQt5.QtWidgets import (
	QLabel,
	QLineEdit,
	QDateEdit,
	QTimeEdit,
	QTextEdit,
	QCheckBox,
	QVBoxLayout,
	QHBoxLayout
)

from datetime import datetime, timedelta

from app.ui.utils import popup
from app.ui.utils import create_button


class CreateEventForm:

	def __init__(self, parent, save_event_handler):
		self.save_event_handler = save_event_handler
		self.parent = parent
		self.parent.setFixedSize(500, 400)
		self.calendar = None

		self.title_input = QLineEdit(self.parent)
		self.description_input = QTextEdit(self.parent)
		self.date_input = QDateEdit(self.parent)
		self.time_input = QTimeEdit(self.parent)
		self.repeat_weekly_input = QCheckBox('Repeat weekly', self.parent)

		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()
		content.addWidget(QLabel('Title:'), alignment=Qt.AlignLeft)
		content.addWidget(self.title_input)
		content.addWidget(QLabel('Description (optional):'), alignment=Qt.AlignLeft)
		content.addWidget(self.description_input)
		content.addWidget(QLabel('Date:'), alignment=Qt.AlignLeft)
		content.addWidget(self.date_input)
		content.addWidget(QLabel('Time:'), alignment=Qt.AlignLeft)
		content.addWidget(self.time_input)
		self.repeat_weekly_input.setChecked(False)
		content.addWidget(self.repeat_weekly_input)
		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		btn_close = create_button('Close', 100, 50, self.parent.close)
		buttons.addWidget(btn_close, 0, Qt.AlignRight)
		btn_save = create_button('Save', 100, 50, self.save_btn_click)
		buttons.addWidget(btn_save, 0, Qt.AlignRight)
		content.addLayout(buttons)
		self.parent.setLayout(content)

	def set_calendar_widget(self, calendar):
		self.calendar = calendar

	def reset_inputs(self, date):
		self.parent.setWindowTitle('New Event | {}'.format(date.strftime('%Y-%m-%d')))
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
				self.description_input.toPlainText(),
				self.repeat_weekly_input.isChecked()
			)
			popup.info(self.parent, 'Save successfully!')
			self.parent.close()
			self.calendar.update()
