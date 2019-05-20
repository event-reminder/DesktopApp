from os.path import expanduser

from PyQt5.QtCore import QLocale

from erdesktop import APP_ROOT, APP_NAME


def abs_path(init_path):
	return '{}/{}'.format(APP_ROOT, init_path.lstrip('/'))


APP_DATA_PATH = abs_path('tmp/')


APP_WIDTH = 1024
APP_HEIGHT = 768

APP_MIN_WIDTH = 1175
APP_MIN_HEIGHT = 580

APP_POS_X = 200
APP_POS_Y = 100

BACKUP_FILE_NAME = '{} Backup'.format(APP_NAME)

SETTINGS_FILE = '{}settings.ini'.format(APP_DATA_PATH)

LOCALE = abs_path('locale')

APP_ICON_DEFAULT = abs_path('resources/images/png/app-icon-default.png')
APP_ICON_SMALL = abs_path('png/app-icon-small.png')

APP_ICON_DEFAULT_ICO = abs_path('resources/images/ico/app-icon-default.ico')
APP_ICON_SMALL_ICO = abs_path('png/app-icon-small.ico')

APP_LOG_FILE = '{}application.log'.format(APP_DATA_PATH)

APP_DB_PATH = APP_DATA_PATH
APP_DB_FILE = '{}storage.db'.format(APP_DATA_PATH)

ENTRY_POINT = abs_path('app_main.py')

LINUX_AUTO_START_FILE = '{}/.config/autostart/{}.desktop'.format(
	expanduser('~'), APP_NAME.replace(' ', '').lower()
)

LINUX_DESKTOP_ENTRY_FILE = '{}/.local/share/applications/{}.desktop'.format(
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

APP_IS_DARK_THEME = False

FONT_SMALL = 10
FONT_NORMAL = 11
FONT_LARGE = 12

FONT = FONT_NORMAL

BADGE_COLOR = '#ff0000'

BADGE_LETTER_COLOR = '#fff'

REMOVE_EVENT_AFTER_TIME_UP = True

START_IN_TRAY = False

RUN_WITH_SYSTEM_START = False

# in seconds
NOTIFICATION_DURATION = 5

# in minutes
REMIND_TIME = 1

UNIT_MINUTES = 'Minutes'
UNIT_HOURS = 'Hours'
UNIT_DAYS = 'Days'
UNIT_WEEKS = 'Weeks'

# 0 - Minutes, 1 - Hours, 2 - Days, 3 - Weeks
REMIND_UNIT = 0

INCLUDE_SETTINGS_BACKUP = True
