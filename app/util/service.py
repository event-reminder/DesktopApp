import time
import platform

from PyQt5.QtCore import QThread

from pynotifier import Notification

from app.storage import Storage
from app.util import logger, log_msg
from app.settings import Settings, APP_NAME

from datetime import date, datetime, timedelta


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
			try:
				self.__process_events(today=date.today())
			except Exception as exc:
				logger.error(log_msg('Service error, can not process non-today events: {}'.format(exc)))
			while True:
				try:
					time.sleep(1)
					self.__process_events(today=date.today(), date_filter=date.today())
				except Exception as exc:
					logger.error(log_msg('Processing event error: {}'.format(exc)))
		except Exception as exc:
			logger.error(log_msg('Service error: {}'.format(exc), 8))
		finally:
			self.storage.disconnect()

	def __process_events(self, today, date_filter=None):
		events = self.__storage.get_events(date_filter)
		need_to_update = False
		for event in events:
			now = datetime.now()
			now_plus_delta = (now + timedelta(minutes=self.__settings.remind_time_before_event)).strftime('%H:%M:00')
			if event.is_past is False and event.time <= now_plus_delta and event.date <= now.date():
				self.__send_notification(event)
				if event.repeat_weekly is True:
					new_date = event.date
					while new_date <= today:
						new_date += timedelta(days=7)
					self.__storage.update_event(pk=event.id, e_date=new_date)
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
			title=APP_NAME,
			icon_path=self.__settings.app_icon('Linux' not in platform.system(), q_icon=False, icon_size='medium'),
			description='{}\n\n{}'.format(event.title, event.description),
			duration=self.__settings.notification_duration,
			urgency=Notification.URGENCY_CRITICAL
		).send()
