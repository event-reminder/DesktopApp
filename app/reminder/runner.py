from app.reminder.services import ReminderService

from app.settings.app_settings import APP_SERVICE_NAME, APP_PID_DIR


def start_reminder_service():
	service = ReminderService(APP_SERVICE_NAME, pid_dir=APP_PID_DIR)
	if not service.is_running():
		service.start()

	# import time
	# time.sleep(.5)
	# print(service.get_pid())
	# time.sleep(1)
	# print(service.get_pid())


if __name__ == '__main__':
	start_reminder_service()
