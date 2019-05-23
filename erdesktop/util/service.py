import time

from PyQt5.QtCore import QThread

from datetime import date, datetime, timedelta

from erdesktop.system import system
from erdesktop.storage import Storage
from erdesktop.util import logger, log_msg
from erdesktop.settings import Settings, APP_NAME
from erdesktop.util.notification import Notification


class ReminderService(QThread):

	def __init__(self, parent, calendar):
		super().__init__(parent=parent)
		self.__calendar = calendar
		self.__settings = Settings()
		self.__storage = Storage()

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
		remind_time = self.__settings.remind_time_before_event(True)
		events = self.__storage.get_events(date_filter, delta=remind_time)
		need_to_update = False
		for event in events:
			now = datetime.now()
			now_plus_delta = (
				now + timedelta(minutes=remind_time if remind_time >= 1 else 0)
			).replace(microsecond=0)
			if event.is_past is False and ((event.date == now.date() and event.time <= now_plus_delta.time()) or event.date < now_plus_delta.date()):
				if event.expired(now):
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
							self.__storage.update_event(pk=event.id, is_past=True, is_notified=1)
					need_to_update = True
				else:
					if event.is_notified == 0:
						self.__send_notification(event)
						self.__storage.update_event(pk=event.id, is_notified=1)
		if need_to_update:
			self.__calendar.update()

	def __send_notification(self, event):
		Notification(
			title=APP_NAME,
			icon_path=self.__settings.app_icon(not system.is_linux(), q_icon=False, small=True),
			description='{}\n\n{}'.format(event.title, event.description),
			duration=self.__settings.notification_duration,
			urgency=Notification.URGENCY_CRITICAL
		).send()
