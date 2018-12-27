import os


APP_WIDTH = 1024    # minimum is 336
APP_HEIGHT = 768    # minimum is 201

APP_NAME = 'Event Reminder'

APP_ICON_DARK = os.path.abspath('./app/resources/app-icon-dark.png')
APP_ICON_LIGHT = os.path.abspath('./app/resources/app-icon-light.png')

# change to '/var/event_reminder.log' in production
APP_LOG_FILE = 'event_reminder_log.txt'
APP_LOG_PATH = os.path.abspath('./event-reminder-tmp/')
