import sys
import time
import datetime

from threading import Thread

from PyQt5.QtWidgets import *

from app.reminder.db import storage

from app.reminder.daemon_service import Service
from app.reminder.notify.notification import QNotification


class ReminderService(Service):

	def run(self):
		try:
			storage.connect()
			while not self.got_sigterm():
				try:
					time.sleep(1)
					events = storage.get_events(datetime.date.today())
					for event in events:
						if event.time <= datetime.datetime.now().time().strftime('%H:%M:00'):
							self.send_notification(event)
							storage.delete_event(event.id)
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
		storage.disconnect()

	@staticmethod
	def send_notification(event):
		app = QApplication(sys.argv)
		notification = QNotification(title=event.title, description=event.description, app=app, timeout=5000)
		notification.show()
		if app.exec_() != 0:
			raise RuntimeError('notification is finished with non-zero exit code')
