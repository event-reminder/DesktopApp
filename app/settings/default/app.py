APP_ROOT = './'


def abs_path(init_path):
	return '{}{}'.format(APP_ROOT, init_path.lstrip('/'))


APP_WIDTH = 1024
APP_HEIGHT = 768

APP_POS_X = 200
APP_POS_Y = 100

APP_NAME = 'Event Reminder'
APP_ORGANIZATION = 'YuriyLisovskiy'

APP_IS_DARK_THEME = False

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
