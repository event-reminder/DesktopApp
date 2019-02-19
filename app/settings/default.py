import os

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

BACKUP_FILE_NAME = '{} Backup'.format(APP_NAME)

SETTINGS_FILE = '{}settings.ini'.format(APP_DATA_PATH)


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
