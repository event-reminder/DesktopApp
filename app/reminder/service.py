import time
import datetime

from PyQt5.QtCore import QThread

from app.reminder.db import storage
from app.settings import custom_settings as settings
from app.reminder.notify.notification import QNotification


class ReminderService(QThread):

	def __init__(self, app, parent=None):
		super().__init__(parent=parent)
		self.app = app

	def __del__(self):
		self.wait()

	def run(self):
		try:
			storage.connect()
			while True:
				try:
					time.sleep(1)
					events = storage.get_events(datetime.date.today())
					for event in events:
						if event.time <= datetime.datetime.now().time().strftime('%H:%M:00'):
							storage.update_event(pk=event.id, is_past=True)
							self.__send_notification(event)
							if settings.REMOVE_EVENT_AFTER_TIME_UP:
								storage.delete_event(event.id)
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
		storage.disconnect()

	def __send_notification(self, event):
		notification = QNotification(
			title=event.title, description=event.description, app=self.app, timeout=5000, flags=None
		)
		notification.exec()
