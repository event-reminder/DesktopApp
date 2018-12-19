from app.ui.utils.popup import error
from app.reminder.notify.notification_widget import NotificationWidget


class QNotification(object):

	def __init__(self, title, description, app):
		self.app = app
		self.notification = self.__build_notification_widget(title, description)

	def __build_notification_widget(self, title, description):
		widget = NotificationWidget(
			title=title, description=description
		)
		try:
			screen_size = self.app.primaryScreen().size()
			widget.resize(300, 70)
			widget.move(screen_size.width() / 2 - 155, 30)
			return widget
		except Exception as exc:
			error(widget, exc)

	def show(self):
		self.notification.show()

		# TODO: need to wait with some timeout
