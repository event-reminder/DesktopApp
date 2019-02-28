from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QPoint, QSettings

from app.settings.default import *
from app.settings.theme import dark_theme_palette, light_theme_palette


class Settings:
	"""
	Implements methods for application settings storage access.
	"""

	def __init__(self, autocommit=True):
		self.__settings = QSettings(SETTINGS_FILE, QSettings.IniFormat)
		self.__is_dark_theme = self.__settings.value('app_user/is_dark_theme', APP_IS_DARK_THEME)
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
	def is_first_launch(self):
		return self.__settings.value('app/first_launch', 'true') == 'true'

	@property
	def app_root(self):
		return self.__settings.value('app/root', APP_ROOT)

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

	def app_icon(self, is_ico=False, q_icon=True, is_dark=False, icon_size='default'):
		icon = ''
		if is_dark and is_ico:
			icon = APP_ICON_DARK_ICO
		if is_dark and not is_ico:
			icon = APP_ICON_DARK_MEDIUM if icon_size == 'medium' else APP_ICON_DARK
		if not is_dark and is_ico:
			icon = APP_ICON_LIGHT_ICO
		if not is_dark and not is_ico:
			icon = APP_ICON_LIGHT_MEDIUM if icon_size == 'medium' else APP_ICON_LIGHT
		if q_icon:
			return QIcon(icon)
		return icon

	@property
	def app_theme(self):
		return dark_theme_palette() if self.is_dark_theme else light_theme_palette()

	@property
	def is_dark_theme(self):
		return self.__settings.value('app_user/is_dark_theme', APP_IS_DARK_THEME) == 'true'

	@property
	def is_always_on_top(self):
		return self.__settings.value('app_user/is_always_on_top', ALWAYS_ON_TOP) == 'true'

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
	def badge_color(self):
		return self.__settings.value('app/badge_color', BADGE_COLOR)

	@property
	def badge_letter_color(self):
		return self.__settings.value('app/badge_letter_color', BADGE_LETTER_COLOR)

	@property
	def remove_event_after_time_up(self):
		return self.__settings.value('event_user/remove_event_after_time_up', REMOVE_EVENT_AFTER_TIME_UP) == 'true'

	@property
	def show_calendar_on_startup(self):
		return self.__settings.value('app_user/show_calendar_on_startup', SHOW_CALENDAR_ON_STARTUP) == 'true'

	@property
	def notification_duration(self):
		return int(self.__settings.value('event_user/notification_duration', NOTIFICATION_DURATION))

	@property
	def remind_time_before_event(self):
		return int(self.__settings.value('event_user/remind_time_before_event', REMIND_TIME))

	@property
	def include_settings_backup(self):
		return self.__settings.value('app_user/include_settings_backup', INCLUDE_SETTINGS_BACKUP) == 'true'

	def set_first_launch(self, value: bool):
		self.__settings.setValue('app/first_launch', 'true' if value else 'false')
		self._commit()

	def set_root(self, root: str):
		self.__settings.setValue('app/root', root)
		self._commit()

	def set_size(self, size: QSize):
		self.__settings.setValue('app/size', size)
		self._commit()

	def set_pos(self, pos: QPoint):
		self.__settings.setValue('app/pos', pos)
		self._commit()

	def set_last_backup_path(self, path: str):
		self.__settings.setValue('app/last_backup_path', path)
		self._commit()

	def set_last_restore_path(self, path: str):
		self.__settings.value('app/last_restore_path', path)
		self._commit()

	def set_theme(self, is_dark: bool):
		self.__settings.setValue('app_user/is_dark_theme', 'true' if is_dark else 'false')
		self._commit()

	def set_is_always_on_top(self, value: bool):
		self.__settings.setValue('app_user/is_always_on_top', 'true' if value else 'false')
		self._commit()

	def set_font(self, value: int):
		self.__settings.setValue('app_user/font', value)
		self._commit()

	def set_lang(self, value: str):
		self.__settings.setValue('app_user/lang', value)
		self._commit()

	def set_max_backups(self, value: int):
		self.__settings.setValue('app_user/max_backups', value)
		self._commit()

	def set_remove_event_after_time_up(self, value: bool):
		self.__settings.setValue('app_user/remove_event_after_time_up', 'true' if value else 'false')
		self._commit()

	def set_show_calendar_on_startup(self, value: bool):
		self.__settings.setValue('app_user/show_calendar_on_startup', 'true' if value else 'false')
		self._commit()

	def set_notification_duration(self, value: int):
		self.__settings.setValue('event_user/notification_duration', value)
		self._commit()

	def set_remind_time_before_event(self, value: int):
		self.__settings.setValue('event_user/remind_time_before_event', value)
		self._commit()

	def set_include_settings_backup(self, value: bool):
		self.__settings.setValue('app_user/include_settings_backup', 'true' if value else 'false')
		self._commit()

	def to_dict(self):
		return {
			'is_dark_theme': self.is_dark_theme,
			'is_always_on_top': self.is_always_on_top,
			'font': self.app_font,
			'remove_event_after_time_up': self.remove_event_after_time_up,
			'show_calendar_on_startup': self.show_calendar_on_startup,
			'notification_duration': self.notification_duration,
			'remind_time_before_event': self.remind_time_before_event
		}

	def from_dict(self, data):
		keys = [
			'is_dark_theme', 'is_always_on_top', 'font',
			'remove_event_after_time_up', 'show_calendar_on_startup',
			'notification_duration', 'remind_time_before_event'
		]
		for key in keys:
			if key not in data:
				raise KeyError('Settings failure: backup is invalid.')
		self.set_theme(data['is_dark_theme'])
		self.set_is_always_on_top(data['is_always_on_top'])
		self.set_font(data['font'])
		self.set_remove_event_after_time_up(data['remove_event_after_time_up'])
		self.set_show_calendar_on_startup(data['show_calendar_on_startup'])
		self.set_notification_duration(data['notification_duration'])
		self.set_remind_time_before_event(data['remind_time_before_event'])
		self.commit()
