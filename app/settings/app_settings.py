from PyQt5.QtGui import *
from PyQt5.QtCore import *

from app.settings import app as s
from app.settings.theme import dark_theme_palette, light_theme_palette


class AppSettings:

	def __init__(self, autocommit=True):
		self.__settings = QSettings(s.APP_ORGANIZATION, s.APP_NAME)
		self.__is_dark_theme = self.__settings.value('app/is_dark_theme', s.APP_IS_DARK_THEME)
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
	def name(self):
		return s.APP_NAME

	@property
	def first_launch(self):
		return self.__settings.value('app/first_launch', True)

	@property
	def root(self):
		return self.__settings.value('app/root', s.APP_ROOT)

	@property
	def size(self):
		return self.__settings.value('app/size', QSize(s.APP_WIDTH, s.APP_HEIGHT))

	@property
	def pos(self):
		return self.__settings.value('app/pos', QPoint(s.APP_POS_X, s.APP_POS_Y))

	def icon(self, is_ico=False, q_icon=True):
		icon = ''
		if self.__is_dark_theme and is_ico:
			icon = s.APP_ICON_DARK_ICO
		if self.__is_dark_theme and not is_ico:
			icon = s.APP_ICON_DARK
		if not self.__is_dark_theme and is_ico:
			icon = s.APP_ICON_LIGHT_ICO
		if not self.__is_dark_theme and not is_ico:
			icon = s.APP_ICON_LIGHT
		if q_icon:
			return QIcon(icon)
		return icon

	@property
	def theme(self):
		return dark_theme_palette() if self.__is_dark_theme else light_theme_palette()

	@property
	def db_path(self):
		return s.APP_DB_PATH

	@property
	def db_file(self):
		return s.APP_DB_FILE

	@property
	def log_path(self):
		return s.APP_LOG_PATH

	@property
	def log_file(self):
		return s.APP_LOG_FILE

	def set_first_launch(self):
		self.__settings.setValue('app/first_launch', False)
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

	def set_theme(self, is_dark: bool):
		self.__settings.setValue('app/is_dark_theme', is_dark)
		self._commit()
