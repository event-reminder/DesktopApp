import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from erdesktop.settings import Settings

# noinspection PyUnresolvedReferences
from erdesktop.resources import languages
from erdesktop.main_window import MainWindow
from erdesktop.util.service import ReminderService


def main():
	app = QApplication(sys.argv)

	app.setStyle('Fusion')

	settings = Settings()

	translator = QTranslator()
	translator.load(':/lang/{}.qm'.format(settings.app_lang))
	app.installTranslator(translator)

	window = MainWindow(app=app)

	ReminderService(window, window.calendar).start()

	if not settings.start_in_tray:
		window.show()

	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
