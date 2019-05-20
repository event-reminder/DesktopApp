from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QPoint, QSettings

from erdesktop.settings import type_conv as tc
from erdesktop.settings.default import *
from erdesktop.settings.theme import dark_theme_palette, light_theme_palette


class Settings:
	"""
	Implements methods for application settings storage access.
	"""

	def __init__(self, autocommit=True, settings_file=SETTINGS_FILE):
		self.__settings = QSettings(settings_file, QSettings.IniFormat)
	# 	self.__is_dark_theme = self.__settings.value('app_user/is_dark_theme', tc.bool_to_str(APP_IS_DARK_THEME))
		self.__autocommit = autocommit
		self.__remind_time_multiplier = [1, 60, 1440, 10080]

	def autocommit(self, val: bool):
		self.__autocommit = val

	def commit(self):
		self.__autocommit = True
		self.__settings.sync()

	def _commit(self):
		if self.__autocommit:
			self.__settings.sync()

	@property
	def app_size(self):
		return self.__settings.value('app/size', QSize(APP_WIDTH, APP_HEIGHT))

	@property
	def app_pos(self):
		return self.__settings.value('app/pos', QPoint(APP_POS_X, APP_POS_Y))

	@property
	def app_last_backup_path(self):
		return self.__settings.value('app/last_backup_path', './')

	@property
	def app_last_restore_path(self):
		return self.__settings.value('app/last_restore_path', '')

	# noinspection PyMethodMayBeStatic
	def app_icon(self, is_ico=False, q_icon=True, small=False):
		icon = ''
		if small and is_ico:
			icon = APP_ICON_SMALL_ICO
		elif small and not is_ico:
			icon = APP_ICON_SMALL
		elif not small and is_ico:
			icon = APP_ICON_DEFAULT_ICO
		elif not small and not is_ico:
			icon = APP_ICON_DEFAULT
		if q_icon:
			return QIcon(icon)
		return icon

	@property
	def app_theme(self):
		return dark_theme_palette() if self.is_dark_theme else light_theme_palette()

	@property
	def is_dark_theme(self):
		return tc.s_bool_(self.__settings.value('app_user/is_dark_theme', tc.str_(APP_IS_DARK_THEME)))

	@property
	def app_font(self):
		return int(self.__settings.value('app_user/font', FONT))

	@property
	def app_lang(self):
		return self.__settings.value('app_user/lang', LANG)

	@property
	def app_max_backups(self):
		return int(self.__settings.value('app_user/max_backups', MAX_BACKUPS))

	@property
	def remove_event_after_time_up(self):
		return tc.s_bool_(
			self.__settings.value('app_user/remove_event_after_time_up', tc.str_(REMOVE_EVENT_AFTER_TIME_UP))
		)

	@property
	def start_in_tray(self):
		return tc.s_bool_(self.__settings.value('app_user/start_in_tray', tc.str_(START_IN_TRAY)))

	@property
	def run_with_system_start(self):
		return tc.s_bool_(
			self.__settings.value('app_user/run_with_system_start', tc.str_(RUN_WITH_SYSTEM_START))
		)

	@property
	def notification_duration(self):
		return int(self.__settings.value('event_user/notification_duration', NOTIFICATION_DURATION))

	def remind_time_before_event(self, to_minutes=False):
		remind_time = int(self.__settings.value('event_user/remind_time_before_event', REMIND_TIME))
		return remind_time if not to_minutes else self._remind_time_to_minutes(remind_time, self.remind_time_unit)

	@property
	def remind_time_unit(self):
		return int(self.__settings.value('event_user/remind_time_unit', REMIND_UNIT))

	@property
	def include_settings_backup(self):
		return tc.s_bool_(self.__settings.value('app_user/include_settings_backup', tc.str_(INCLUDE_SETTINGS_BACKUP)))

	def _set_value(self, key, value):
		self.__settings.setValue(key, value)
		self._commit()

	def set_size(self, size: QSize):
		self._set_value('app/size', size)

	def set_pos(self, pos: QPoint):
		self._set_value('app/pos', pos)

	def set_last_backup_path(self, path: str):
		self._set_value('app/last_backup_path', path)

	def set_last_restore_path(self, path: str):
		self._set_value('app/last_restore_path', path)

	def set_theme(self, is_dark: bool):
		self._set_value('app_user/is_dark_theme', tc.str_(is_dark))

	def set_is_always_on_top(self, value: bool):
		self._set_value('app_user/is_always_on_top', tc.str_(value))

	def set_font(self, value: int):
		self._set_value('app_user/font', value)

	def set_lang(self, value: str):
		self._set_value('app_user/lang', value)

	def set_max_backups(self, value: int):
		self._set_value('app_user/max_backups', value)

	def set_remove_event_after_time_up(self, value: bool):
		self._set_value('app_user/remove_event_after_time_up', tc.str_(value))

	def set_start_in_tray(self, value: bool):
		self._set_value('app_user/start_in_tray', tc.str_(value))

	def set_run_with_system_start(self, value: bool):
		self._set_value('app_user/run_with_system_start', tc.str_(value))

	def set_notification_duration(self, value: int):
		self._set_value('event_user/notification_duration', value)

	def set_remind_time_before_event(self, value: int):
		self._set_value('event_user/remind_time_before_event', value)

	def set_remind_time_unit(self, value: int):
		self._set_value('event_user/remind_time_unit', value)

	def set_include_settings_backup(self, value: bool):
		self._set_value('app_user/include_settings_backup', tc.str_(value))

	def to_dict(self):
		return {
			'is_dark_theme': tc.int_(self.is_dark_theme),
			'font': self.app_font,
			'remove_event_after_time_up': tc.int_(self.remove_event_after_time_up),
			'start_in_tray': tc.int_(self.start_in_tray),
			'notification_duration': self.notification_duration,
			'remind_time_before_event': self.remind_time_before_event(),
			'remind_time_unit': self.remind_time_unit,
			'auto_start': tc.int_(self.run_with_system_start),
			'lang': self.app_lang,
			'backup_settings': tc.int_(self.include_settings_backup),
			'max_backups': self.app_max_backups,
		}

	def from_dict(self, data):
		self.set_theme(tc.bool_(
			data.get('is_dark_theme', tc.int_(APP_IS_DARK_THEME)))
		)
		self.set_font(data.get('font', FONT))
		self.set_remove_event_after_time_up(
			tc.bool_(data.get('remove_event_after_time_up', tc.int_(REMOVE_EVENT_AFTER_TIME_UP)))
		)
		self.set_start_in_tray(
			tc.bool_(data.get('start_in_tray', tc.int_(START_IN_TRAY)))
		)
		self.set_notification_duration(data.get('notification_duration', NOTIFICATION_DURATION))
		self.set_remind_time_before_event(data.get('remind_time_before_event', REMIND_TIME))
		self.set_remind_time_unit(data.get('remind_time_unit', REMIND_UNIT))
		self.set_run_with_system_start(
			tc.bool_(data.get('auto_start', tc.int_(RUN_WITH_SYSTEM_START)))
		)
		self.set_lang(self.__normalize_lang(data.get('lang', LANG)))
		self.set_include_settings_backup(
			tc.bool_(data.get('backup_settings', tc.int_(INCLUDE_SETTINGS_BACKUP)))
		)
		self.set_max_backups(data.get('max_backups', MAX_BACKUPS))
		self.commit()

	@staticmethod
	def __normalize_lang(lang):
		if lang == 'en':
			lang = 'en_US'
		elif lang == 'uk':
			lang = 'uk_UA'
		elif lang != 'uk_UA' or lang != 'en_US':
			lang = 'en_US'
		return lang

	def _remind_time_to_minutes(self, remind_time, units):
		return self.__remind_time_multiplier[units] * remind_time
