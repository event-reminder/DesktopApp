from PyQt5.QtGui import *
from PyQt5.QtCore import *

from app.settings import app as a
from app.settings import user as u


class UserSettings:

	def __init__(self, autocommit=True):
		self.__settings = QSettings(a.APP_ORGANIZATION, a.APP_NAME)
		self.__is_dark_theme = self.__settings.value('app/is_dark_theme', a.APP_IS_DARK_THEME)
		self.__autocommit = autocommit

	def autocommit(self, val: bool):
		self.__autocommit = val

	def commit(self):
		self.__autocommit = True
		self.__settings.sync()

	def _commit(self):
		if self.__autocommit:
			self.__settings.sync()

	@property
	def mouse_enter_opacity(self):
		return self.__settings.value('user/mouse_enter_opacity', u.MOUSE_ENTER_OPACITY)

	@property
	def mouse_leave_opacity(self):
		return self.__settings.value('user/mouse_leave_opacity', u.MOUSE_LEAVE_OPACITY)

	@property
	def is_always_on_top(self):
		return self.__settings.value('user/is_always_on_top', u.ALWAYS_ON_TOP) == 'true'

	@property
	def font(self):
		return self.__settings.value('user/font', u.FONT)

	@property
	def badge_color(self):
		return self.__settings.value('user/badge_color', u.BADGE_COLOR_DARK if self.__is_dark_theme else u.BADGE_COLOR_LIGHT)

	@property
	def badge_letter_color(self):
		return self.__settings.value('user/badge_letter_color', u.BADGE_LETTER_COLOR)

	@property
	def remove_event_after_time_up(self):
		return self.__settings.value('user/remove_event_after_time_up', u.REMOVE_EVENT_AFTER_TIME_UP)

	@property
	def show_calendar_on_startup(self):
		return self.__settings.value('user/show_calendar_on_startup', u.SHOW_CALENDAR_ON_STARTUP) == 'true'

	@property
	def notification_duration(self):
		return self.__settings.value('user/notification_duration', u.NOTIFICATION_DURATION)

	@property
	def remind_time_before_event(self):
		return self.__settings.value('user/remind_time_before_event', u.REMIND_TIME)

	def set_mouse_enter_opacity(self, value: float):
		self.__settings.setValue('user/mouse_enter_opacity', value)
		if self.__autocommit:
			self.__settings.sync()

	def set_mouse_leave_opacity(self, value: float):
		self.__settings.setValue('user/mouse_leave_opacity', value)
		self._commit()

	def set_is_always_on_top(self, value: bool):
		self.__settings.setValue('user/is_always_on_top', value)
		self._commit()

	def set_font(self, value: int):
		self.__settings.setValue('user/font', value)
		self._commit()

	def set_remove_event_after_time_up(self, value: bool):  # TODO: add to settings ui
		self.__settings.setValue('user/remove_event_after_time_up', value)
		self._commit()

	def set_show_calendar_on_startup(self, value: bool):
		self.__settings.setValue('user/show_calendar_on_startup', value)
		self._commit()

	def set_notification_duration(self, value: int):  # TODO: add to settings ui
		self.__settings.setValue('user/notification_duration', value)
		self._commit()

	def set_remind_time_before_event(self, value: int):  # TODO: add to settings ui
		self.__settings.setValue('user/remind_time_before_event', value)
		self._commit()
