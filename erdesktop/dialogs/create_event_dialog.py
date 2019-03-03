from datetime import datetime, timedelta

from erdesktop.util import Worker
from erdesktop.storage import Storage
from erdesktop.widgets.util import PushButton, popup
from erdesktop.widgets.waiting_spinner import WaitingSpinner

from PyQt5.QtCore import Qt, QDate, QTime, QThreadPool
from PyQt5.QtWidgets import (
	QLabel, QDialog, QLineEdit, QDateEdit, QTimeEdit, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QMessageBox
)


# noinspection PyArgumentList
class CreateEventDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		self.setFixedSize(500, 400)
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))
		self.setWindowTitle(self.tr('New Event'))

		self.thread_pool = QThreadPool()
		self.spinner = WaitingSpinner()

		self.calendar = kwargs.get('calendar', None)

		if self.calendar is None:
			raise RuntimeError('CreateEventDialog: calendar is not set')

		self.storage = kwargs.get('storage', Storage(try_to_reconnect=True))
		self.storage.try_to_reconnect = True

		self.title_input = QLineEdit(self)
		self.description_input = QTextEdit(self)
		self.date_input = QDateEdit(self)
		self.time_input = QTimeEdit(self)
		self.repeat_weekly_input = QCheckBox(self.tr('Repeat weekly'), self)

		self.event_id = None
		self.del_btn = None

		self.setup_ui()

		self.layout().addWidget(self.spinner)

	def showEvent(self, event):
		self.move(
			self.calendar.window().frameGeometry().topLeft() +
			self.calendar.window().rect().center() - self.rect().center()
		)
		super(CreateEventDialog, self).showEvent(event)

	def setup_ui(self):
		content = QVBoxLayout()
		content.addWidget(QLabel('{}:'.format(self.tr('Title'))), alignment=Qt.AlignLeft)
		content.addWidget(self.title_input)
		content.addWidget(QLabel('{}:'.format(self.tr('Description (optional)'))), alignment=Qt.AlignLeft)
		content.addWidget(self.description_input)
		content.addWidget(QLabel('{}:'.format(self.tr('Date'))), alignment=Qt.AlignLeft)
		content.addWidget(self.date_input)
		content.addWidget(QLabel('{}:'.format(self.tr('Time'))), alignment=Qt.AlignLeft)
		content.addWidget(self.time_input)
		self.repeat_weekly_input.setChecked(False)
		content.addWidget(self.repeat_weekly_input)

		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		buttons.addWidget(PushButton(self.tr('Save'), 90, 30, self.save_event_click), 0, Qt.AlignRight)
		self.del_btn = PushButton(self.tr('Delete'), 90, 30, self.delete_event_click)
		buttons.addWidget(self.del_btn)
		buttons.addWidget(PushButton(self.tr('Cancel'), 90, 30, self.close), 0, Qt.AlignRight)
		content.addLayout(buttons)

		self.setLayout(content)

	def reset_inputs(self, date=None, event_data=None):
		self.del_btn.setEnabled(False)
		if date is not None:
			self.event_id = None
			self.date_input.setDate(QDate(date))
			curr_time = (datetime.now() + timedelta(minutes=3)).time().replace(second=0, microsecond=0)
			self.time_input.setTime(QTime(curr_time))
			self.title_input.setText('')
			self.description_input.setText('')
		elif event_data is not None:
			self.event_id = event_data.id
			self.setWindowTitle(self.tr('Update Event'))
			self.title_input.setText(event_data.title)
			self.description_input.setText(event_data.description)
			self.date_input.setDate(event_data.date)
			self.time_input.setTime(QTime.fromString(event_data.time, '%H:%M:00'))
			self.repeat_weekly_input.setChecked(event_data.repeat_weekly)
			self.del_btn.setEnabled(True)

	def delete_event_click(self):
		if self.storage.event_exists(self.event_id):
			ret_action = popup.question(
				self,
				self.tr('Deleting an event'),
				'{}?'.format(self.tr('Do you really want to delete the event'))
			)
			if ret_action == QMessageBox.Yes:
				self.exec_worker(
					self.delete_event,
					self.close_and_update,
					'{}',
					*(self.event_id,)
				)
		else:
			popup.info(self.parent, '{}!'.format(self.tr('Event is already removed')))

	def delete_event(self, event_id):
		self.storage.connect()
		self.storage.delete_event(event_id)

	def validate_inputs(self):
		if len(self.title_input.text()) < 1:
			popup.warning(self, '{}!'.format(self.tr('Provide title for the event')))
			return False
		if self.event_id is None:
			if self.date_input.date().toPyDate() < datetime.now().date():
				popup.warning(self, self.tr('Unable to set past event, check date input'))
				return False
			if self.time_input.time().toPyTime() < datetime.now().time() and \
				self.date_input.date().toPyDate() == datetime.now().date():
				popup.warning(self, self.tr('Unable to set past event, check time input'))
				return False
		return True

	def save_event_click(self):
		if self.validate_inputs():
			data = {
				'title': self.title_input.text(),
				'e_date': self.date_input.date().toPyDate(),
				'e_time': self.time_input.time().toPyTime(),
				'description': self.description_input.toPlainText(),
				'repeat_weekly': self.repeat_weekly_input.isChecked()
			}
			err_format = '{}'.format(self.tr('Saving event to database failed')) + ': {}'
			fn = self.storage.create_event
			if self.event_id is not None:
				data['pk'] = self.event_id
				fn = self.storage.update_event
			self.exec_worker(fn, self.save_event_success, err_format, **data)

	def save_event_success(self):
		popup.info(self, self.tr('Saved successfully'))
		self.close_and_update()

	def close_and_update(self):
		self.close()
		self.calendar.update()

	def exec_worker(self, fn, fn_success, err_format, *args, **kwargs):
		self.spinner.start()
		worker = Worker(fn, *args, **kwargs)
		if fn_success is not None:
			worker.signals.success.connect(fn_success)
		worker.err_format = err_format
		worker.signals.error.connect(self.popup_error)
		worker.signals.finished.connect(self.spinner.stop)
		self.thread_pool.start(worker)

	def popup_error(self, err):
		popup.error(self, '{}'.format(err[1]))
