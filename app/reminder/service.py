import time
import datetime
import platform

from PyQt5.QtCore import QThread

from pynotifier import Notification

from app.reminder.db import storage
from app.settings import custom_settings as settings
from app.settings.custom_settings import NOTIFICATION_DURATION
from app.settings.app_settings import (
	APP_NAME,
	APP_ICON_LIGHT,
	APP_ICON_LIGHT_ICO
)


class ReminderService(QThread):

	def __init__(self, parent, calendar):
		super().__init__(parent=parent)
		self.calendar = calendar

	def __del__(self):
		self.wait()

	def run(self):
		try:
			storage.connect()
			while True:
				try:
					time.sleep(1)
					self.process_events()
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
		storage.disconnect()

	def process_events(self):
		events = storage.get_events(datetime.date.today())
		for event in events:
			if event.time <= datetime.datetime.now().time().strftime('%H:%M:00'):
				storage.update_event(pk=event.id, is_past=True)
				self.__send_notification(event)
				if settings.REMOVE_EVENT_AFTER_TIME_UP:
					storage.delete_event(event.id)
					self.calendar.update()

	@staticmethod
	def __send_notification(event):
		Notification(
			title=APP_NAME,
			icon_path=APP_ICON_LIGHT if 'Linux' in platform.system() else APP_ICON_LIGHT_ICO,
			description='{}\n\n{}'.format(event.title, event.description),
			duration=NOTIFICATION_DURATION,
			urgency=Notification.URGENCY_CRITICAL
		).send()
