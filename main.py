import sys

from PyQt5.QtWidgets import *

from app.ui.window import Window
from app.reminder.service import ReminderService


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ReminderService(app, app).start()
	window = Window()
	window.show()
	sys.exit(app.exec_())
