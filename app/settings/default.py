APP_ROOT = './'


def abs_path(init_path):
	return '{}{}'.format(APP_ROOT, init_path.lstrip('/'))


APP_WIDTH = 1024
APP_HEIGHT = 768

APP_POS_X = 200
APP_POS_Y = 100

APP_NAME = 'Event Reminder'
APP_ORGANIZATION = 'YuriyLisovskiy'

APP_IS_DARK_THEME = 'false'

APP_ICON_DARK = abs_path('app/resources/app-icon-dark.png')
APP_ICON_LIGHT = abs_path('app/resources/app-icon-light.png')

APP_ICON_DARK_ICO = abs_path('app/resources/app-icon-light.ico')
APP_ICON_LIGHT_ICO = abs_path('app/resources/app-icon-light.ico')


# path to files created by application, etc db, log
APP_PATH = abs_path('event-reminder-tmp/')

APP_LOG_PATH = APP_PATH
APP_LOG_FILE = '{}event_reminder_log.txt'.format(APP_PATH)

APP_DB_PATH = APP_PATH
APP_DB_FILE = '{}event_reminder.db'.format(APP_PATH)


MOUSE_ENTER_OPACITY = 1
MOUSE_LEAVE_OPACITY = 1

ALWAYS_ON_TOP = 'false'

FONT_SMALL = 10
FONT_NORMAL = 11
FONT_LARGE = 14

FONT = FONT_NORMAL

BADGE_COLOR_LIGHT = '#ff0000'
BADGE_COLOR_DARK = '#ff0000'

BADGE_LETTER_COLOR = '#fff'

REMOVE_EVENT_AFTER_TIME_UP = 'true'

SHOW_CALENDAR_ON_STARTUP = 'true'

NOTIFICATION_DURATION = 5   # in seconds

REMIND_TIME = 1             # in minutes
