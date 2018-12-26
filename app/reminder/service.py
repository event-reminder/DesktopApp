import time
import datetime

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QColor, QBrush

from app.reminder.db import storage
from app.settings import custom_settings as settings
from app.reminder.notify.notification import Notification
from app.settings.custom_settings import DEFAULT_DATE_COLOR, DEFAULT_MARKED_DATE_LETTER_COLOR, NOTIFICATION_TIMEOUT


class ReminderService(QThread):

	def __init__(self, app, parent=None, calendar=None):
		super().__init__(parent=parent)
		self.app = app
		self.calendar = calendar

	def __del__(self):
		self.wait()

	def run(self):
		try:
			storage.connect()
			while True:
				try:
					time.sleep(1)
					today = datetime.date.today()
					events = storage.get_events(today)
					for event in events:
						if event.time <= datetime.datetime.now().time().strftime('%H:%M:00'):
							storage.update_event(pk=event.id, is_past=True)
							self.__send_notification(event)
							if settings.REMOVE_EVENT_AFTER_TIME_UP:
								storage.delete_event(event.id)
								if len(storage.get_events(today)) < 1:
									self.__reset_date(today)
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
		storage.disconnect()

	def __send_notification(self, event):
		notification = Notification(
			flags=None,
			app=self.app,
			title=event.title,
			description=event.description,
			timeout=NOTIFICATION_TIMEOUT * 1000
		)
		notification.exec()

	def __reset_date(self, date):
		brush = QBrush(QColor(DEFAULT_DATE_COLOR))
		day = self.calendar.dateTextFormat(date)
		day.setBackground(brush)
		day.setForeground(QBrush(QColor(DEFAULT_MARKED_DATE_LETTER_COLOR)))
		self.calendar.setDateTextFormat(date, day)
