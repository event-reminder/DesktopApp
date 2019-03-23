import os
from os.path import expanduser

from PyQt5.QtCore import QLocale

# noinspection PyUnresolvedReferences
from erdesktop.resources import images


APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abs_path(init_path):
	return '{}/{}'.format(APP_ROOT, init_path.lstrip('/'))


def img_path(init_path):
	return ':/img/images/{}'.format(init_path)


APP_DATA_PATH = abs_path('tmp/')


APP_WIDTH = 1024
APP_HEIGHT = 768

APP_POS_X = 200
APP_POS_Y = 100

APP_NAME = 'Event Reminder'
APP_ORGANIZATION = 'YuriyLisovskiy'
APP_VERSION = '2019.0.2-alpha'
APP_RELEASE_DATE = 'February 2, 2019'

APP_DESCRIPTION = 'Cross-platform desktop application which helps to finish all tasks in time'

BACKUP_FILE_NAME = '{} Backup'.format(APP_NAME)

SETTINGS_FILE = '{}settings.ini'.format(APP_DATA_PATH)

LOCALE = abs_path('locale')

APP_ICON_DARK = img_path('png/app-icon-dark.png')
APP_ICON_DARK_MEDIUM = img_path('png/app-icon-dark-70x70.png')

APP_ICON_LIGHT = img_path('png/app-icon-light.png')
APP_ICON_LIGHT_MEDIUM = img_path('png/app-icon-light-70x70.png')

APP_ICON_DARK_ICO = img_path('ico/app-icon-light.ico')
APP_ICON_LIGHT_ICO = img_path('ico/app-icon-light.ico')

APP_LOG_FILE = '{}application.log'.format(APP_DATA_PATH)

APP_DB_PATH = APP_DATA_PATH
APP_DB_FILE = '{}storage.db'.format(APP_DATA_PATH)

ENTRY_POINT = abs_path('app_main.py')

LINUX_AUTO_START_FILE = '{}/.config/autostart/{}.desktop'.format(
	expanduser('~'), APP_NAME.replace(' ', '').lower()
)

PY_PACKAGE_NAME = APP_ROOT.split('/')[-1]


AVAILABLE_LANGUAGES_IDX = {
	'en_US': 0,
	'uk_UA': 1
}

AVAILABLE_LANGUAGES = {
	'English': 'en_US',
	'Українська': 'uk_UA'
}

AVAILABLE_LOCALES = {
	'en_US': QLocale.English,
	'uk_UA': QLocale.Ukrainian
}

LANG = 'en_US'

MAX_BACKUPS = 5

APP_IS_DARK_THEME = 'false'

ALWAYS_ON_TOP = 'false'

FONT_SMALL = 10
FONT_NORMAL = 11
FONT_LARGE = 12

FONT = FONT_NORMAL

BADGE_COLOR = '#ff0000'

BADGE_LETTER_COLOR = '#fff'

REMOVE_EVENT_AFTER_TIME_UP = 'true'

START_IN_TRAY = 'false'

RUN_WITH_SYSTEM_START = 'false'

NOTIFICATION_DURATION = 5   # in seconds

REMIND_TIME = 1             # in minutes

INCLUDE_SETTINGS_BACKUP = 'true'
