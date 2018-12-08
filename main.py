import sys

from PyQt5.QtWidgets import *

from app.ui.window import Window
from app.reminder.services import ReminderService
from app.settings.app_settings import APP_SERVICE_NAME, APP_PID_DIR


if __name__ == '__main__':
	service = ReminderService(APP_SERVICE_NAME, pid_dir=APP_PID_DIR)
	if not service.is_running():
		service.start()
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())
