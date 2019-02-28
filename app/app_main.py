import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from app.settings import Settings
from app.settings.default import LOCALE
from app import MainWindow, ReminderService


if __name__ == '__main__':
	app = QApplication(sys.argv)

	settings = Settings()

	translator = QTranslator()
	translator.load('{}/{}.qm'.format(LOCALE, settings.app_lang))
	app.installTranslator(translator)

	window = MainWindow(app=app)

	ReminderService(window, window.calendar).start()

	if settings.show_calendar_on_startup:
		window.show()
	sys.exit(app.exec_())
