import peewee

from datetime import datetime, timedelta

from app.utils import popup, logger, log_msg, button

from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtWidgets import QLabel, QDialog, QLineEdit, QDateEdit, QTimeEdit, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout


# noinspection PyArgumentList
class CreateEventDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		self.setFixedSize(500, 400)
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs['calendar']
		self.storage = kwargs['storage']

		self.title_input = QLineEdit(self)
		self.description_input = QTextEdit(self)
		self.date_input = QDateEdit(self)
		self.time_input = QTimeEdit(self)
		self.repeat_weekly_input = QCheckBox('Repeat weekly', self)

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
		btn_save = button('Save', 90, 30, self.save_btn_click)
		buttons.addWidget(btn_save, 0, Qt.AlignRight)
		btn_close = button('Cancel', 90, 30, self.close)
		buttons.addWidget(btn_close, 0, Qt.AlignRight)
		content.addLayout(buttons)
		self.setLayout(content)

	def reset_inputs(self, date):
		self.setWindowTitle('New Event')
		self.date_input.setDate(QDate(date))
		curr_time = (datetime.now() + timedelta(minutes=3)).time().replace(second=0, microsecond=0)
		self.time_input.setTime(QTime(curr_time))
		self.title_input.setText('')
		self.description_input.setText('')

	def validate_inputs(self):
		if len(self.title_input.text()) < 1:
			popup.warning(self, 'Provide title for the event!')
			return False
		if self.date_input.date().toPyDate() < datetime.now().date():
			popup.warning(self, 'Can\'t set past event, check date input')
			return False
		if self.time_input.time().toPyTime() < datetime.now().time() and \
			self.date_input.date().toPyDate() == datetime.now().date():
			popup.warning(self, 'Can\'t set past event, check time input')
			return False
		return True

	def save_btn_click(self):
		if self.validate_inputs():
			try:
				self.calendar.status_bar.showMessage('Status: Saving...')
				self.storage.connect()
				self.storage.create_event(
					self.title_input.text(),
					self.date_input.date().toPyDate(),
					self.time_input.time().toPyTime(),
					self.description_input.toPlainText(),
					self.repeat_weekly_input.isChecked()
				)
			except peewee.PeeweeException as exc:
				logger.error(log_msg('database error: {}'.format(exc)))
				popup.error(self, 'Database error: {}'.format(exc))
			except Exception as exc:
				logger.error(log_msg('unknown error: {}'.format(exc)))
				popup.error(self, 'Error occurred: {}'.format(exc))
			finally:
				self.storage.disconnect()
				self.calendar.reset_status()
				popup.info(self, 'Save successfully!')
				self.close()
				self.calendar.update()
