import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from erdesktop.settings import Settings
from erdesktop.settings.default import LOCALE
from erdesktop import MainWindow, ReminderService


def main():
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


if __name__ == '__main__':
	main()