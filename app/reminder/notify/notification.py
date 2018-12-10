from PyQt5.QtCore import *

from app.ui.utils.popup import error
from app.reminder.notify.notification_widget import NotificationWidget


class QNotification(object):

	def __init__(self, title, description, app, timeout=1000):
		self.app = app
		self.notification = self.__build_notification_widget(title, description)
		self.timer = QTimer()
		self.timer.timeout.connect(self.notification.close)
		self.timeout = timeout

	def __build_notification_widget(self, title, description):
		widget = NotificationWidget(title, description, self.__add_timer, self.__remove_timer)
		try:
			screen_size = self.app.primaryScreen().size()
			widget.resize(300, 70)
			widget.move(screen_size.width() / 2 - 155, 30)
			return widget
		except Exception as exc:
			error(widget, exc)

	def show(self):
		self.notification.show()
		self.__add_timer()

	def __add_timer(self):
		if self.timer is None:
			raise RuntimeError('timer is None')
		self.timer.start(self.timeout)

	def __remove_timer(self):
		if self.timer is None:
			raise RuntimeError('timer is None')
		self.timer.stop()
