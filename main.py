import sys

from PyQt5.QtWidgets import *

from app.ui.window import Window
from app.reminder.runner import start_reminder_service


if __name__ == '__main__':
	start_reminder_service()
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())
