from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils.popup import error
from app.reminder.notify.notification_ui import NotificationUI


class Notification(QDialog):

	def __init__(self, title, description, app, timeout, flags, *args, **kwargs):
		super().__init__(flags, *args, **kwargs)
		self.__app = app
		self.__width = 400
		self.__height = 130
		self.ui = self.__build_ui(title, description)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

		self.timer = QTimer()
		self.timer.timeout.connect(self.__close_dialog)
		self.timeout = timeout
		self.timer.start(self.timeout)

	def __build_ui(self, title, description):
		ui = NotificationUI(title=title, description=description, parent=self, close_event=self.__close_dialog)
		try:
			screen_size = self.__app.primaryScreen().size()
			self.resize(self.__width, self.__height)
			self.move(screen_size.width() - self.__width - 20, screen_size.height() - self.__height - 30)
			return ui
		except Exception as exc:
			error(self, exc)

	def __close_dialog(self):
		self.hide()     # TODO: need to close instead of hide() because of overflowing

	def enterEvent(self, event):
		super().enterEvent(event)
		self.timer.stop()   # TODO: not working

	def leaveEvent(self, event):
		super().leaveEvent(event)
		self.timer.start(self.timeout)   # TODO: not working
