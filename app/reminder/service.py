import time
import platform
from datetime import (
	date,
	datetime,
	timedelta
)

from PyQt5.QtCore import QThread

from pynotifier import Notification

from app.db import Storage
from app.settings import Settings


class ReminderService(QThread):

	def __init__(self, parent, calendar):
		super().__init__(parent=parent)
		self.__calendar = calendar
		self.__settings = Settings()
		self.__storage = Storage()

	def __del__(self):
		self.wait()

	def run(self):
		try:
			self.__storage.connect()
			while True:
				try:
					time.sleep(1)
					self.__process_events()
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
					print('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
			print('Service error: {}\n'.format(exc))
		self.storage.disconnect()

	def __process_events(self):
		events = self.__storage.get_events(date.today())
		need_to_update = False
		for event in events:
			now = datetime.now()
			if event.is_past is not True and event.time <= now.time().strftime('%H:%M:00') and event.date <= now.date():
				self.__send_notification(event)
				if event.repeat_weekly is True:
					self.__storage.update_event(pk=event.id, e_date=event.date + timedelta(days=7))
				else:
					if self.__settings.remove_event_after_time_up is True:
						self.__storage.delete_event(event.id)
					else:
						self.__storage.update_event(pk=event.id, is_past=True)
				need_to_update = True
		if need_to_update:
			self.__calendar.update()

	def __send_notification(self, event):
		Notification(
			title=self.__settings.name,
			icon_path=self.__settings.icon('Linux' not in platform.system(), q_icon=False),
			description='{}\n\n{}'.format(event.title, event.description),
			duration=self.__settings.notification_duration,
			urgency=Notification.URGENCY_CRITICAL
		).send()
