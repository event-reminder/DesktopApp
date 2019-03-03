import os
from os.path import expanduser

from PyQt5.QtCore import QLocale


APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abs_path(init_path):
	return '{}/{}'.format(APP_ROOT, init_path.lstrip('/'))


def resources(init_path):
	return abs_path('resources/{}'.format(init_path))


APP_DATA_PATH = abs_path('tmp/')


APP_WIDTH = 1024
APP_HEIGHT = 768

APP_POS_X = 200
APP_POS_Y = 100

APP_NAME = 'Event Reminder'
APP_ORGANIZATION = 'YuriyLisovskiy'
APP_VERSION = '2019.0.1'
APP_RELEASE_DATE = 'February 2, 2019'

# TODO: add application description
APP_DESCRIPTION = 'Some description'

BACKUP_FILE_NAME = '{} Backup'.format(APP_NAME)

SETTINGS_FILE = '{}settings.ini'.format(APP_DATA_PATH)

LOCALE = abs_path('locale')

APP_ICON_DARK = resources('app-icon-dark.png')
APP_ICON_DARK_MEDIUM = resources('app-icon-dark-70x70.png')

APP_ICON_LIGHT = resources('app-icon-light.png')
APP_ICON_LIGHT_MEDIUM = resources('app-icon-light-70x70.png')

APP_ICON_DARK_ICO = resources('app-icon-light.ico')
APP_ICON_LIGHT_ICO = resources('app-icon-light.ico')


# path to files created by application: db, log, etc.

APP_LOG_FILE = '{}application.log'.format(APP_DATA_PATH)

APP_DB_PATH = APP_DATA_PATH
APP_DB_FILE = '{}storage.db'.format(APP_DATA_PATH)

ENTRY_POINT = abs_path('app_main.py')

LINUX_AUTO_START_FILE = '{}/.config/autostart/{}.desktop'.format(
	expanduser('~'), APP_NAME.replace(' ', '').lower()
)


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
FONT_LARGE = 14

FONT = FONT_NORMAL

BADGE_COLOR = '#ff0000'

BADGE_LETTER_COLOR = '#fff'

REMOVE_EVENT_AFTER_TIME_UP = 'true'

SHOW_CALENDAR_ON_STARTUP = 'true'

NOTIFICATION_DURATION = 5   # in seconds

REMIND_TIME = 1             # in minutes

INCLUDE_SETTINGS_BACKUP = 'true'
