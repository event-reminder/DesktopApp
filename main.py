import sys

from PyQt5.QtWidgets import QApplication

from app.ui.window import Window
from app.settings import UserSettings
from app.reminder.service import ReminderService


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	ReminderService(window, window.calendar).start()
	if UserSettings().show_calendar_on_startup:
		window.show()
	sys.exit(app.exec_())
