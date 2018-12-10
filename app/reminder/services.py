import time

from app.reminder.daemon_service import Service

import sys
from PyQt5.QtWidgets import QApplication, QWidget


def notification(msg):
	w = QWidget()
	w.resize(250, 150)
	w.move(300, 300)
	w.setWindowTitle(msg)
	return w


class ReminderService(Service):

	def run(self):
		try:
			while not self.got_sigterm():
				try:
					time.sleep(5)

					app = QApplication(sys.argv)
					n = notification('Hello World!')
					n.show()
					sys.exit(app.exec_())

					# TODO: send notification

				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
