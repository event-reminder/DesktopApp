import sys

from PyQt5.QtWidgets import QApplication

from app import MainWindow
from app.settings import Settings
from app.service import ReminderService


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow(app=app)
	ReminderService(window, window.calendar).start()
	if Settings().show_calendar_on_startup:
		window.show()
	sys.exit(app.exec_())
