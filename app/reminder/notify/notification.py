from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from app.utils.timer import Timer
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

		self.timer = Timer(timeout, self.__close_dialog)
		self.timer.start()
		# self.timeout = timeout

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
		self.hide()

	def enterEvent(self, event):
		super().enterEvent(event)
		self.timer.stop()

	def leaveEvent(self, event):
		super().leaveEvent(event)
		self.timer.start()
