import os


def abs_path(init_path):
	return os.path.abspath(init_path)


APP_WIDTH = 1024    # minimum is 336
APP_HEIGHT = 768    # minimum is 201

APP_NAME = 'Event Reminder'

APP_ICON_DARK = abs_path('./app/resources/app-icon-dark.png')
APP_ICON_LIGHT = abs_path('./app/resources/app-icon-light.png')

APP_ICON_DARK_ICO = abs_path('./app/resources/app-icon-light.ico')
APP_ICON_LIGHT_ICO = abs_path('./app/resources/app-icon-light.ico')

# change to '/var/event_reminder.log' in production
APP_LOG_FILE = 'event_reminder_log.txt'
APP_LOG_PATH = abs_path('./event-reminder-tmp/')
