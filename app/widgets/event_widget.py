import peewee

from PyQt5.QtWidgets import (
	QMenu,
	QLabel,
	QWidget,
	QListWidget,
	QVBoxLayout,
	QMessageBox
)

from app.utils import (
	popup,
	error,
	logger,
	log_msg
)
from app.db import Storage


# noinspection PyArgumentList
class EventWidget(QWidget):

	def __init__(self, parent: QListWidget, **kwargs):
		super(EventWidget, self).__init__(parent)
		self.titleLabel = QLabel()
		self.timeLabel = QLabel()
		self.parent = parent
		self.setup_content()
		self.menu, self.menu_actions = self.setup_menu()
		self.id = -1
		self.date = None
		self.update_day = kwargs['update_day']
		self.storage = Storage(connect=False)

	def setup_content(self):
		layout = QVBoxLayout()
		layout.addWidget(self.timeLabel)
		layout.addWidget(self.titleLabel)
		self.setLayout(layout)

	def setup_menu(self):
		menu = QMenu(self)
		actions = {
			'delete': menu.addAction('Delete')
		}
		return menu, actions

	def set_data(self, pk, title, time, date):
		self.timeLabel.setText('Event #{} at {}'.format(pk, time[:5]))
		self.titleLabel.setText(title)
		self.id = pk
		self.date = date

	def contextMenuEvent(self, event):
		self.process_menu_events(self.menu.exec_(self.mapToGlobal(event.pos())))

	def remove_event(self):
		self.storage.connect()
		if self.storage.event_exists(self.id):
			ret_action = popup.question(self.parent, 'Deleting an event', 'Do you really want to delete the event?')
			if ret_action == QMessageBox.Yes:
				try:
					if self.storage.event_exists(self.id):
						self.storage.delete_event(self.id)
				except peewee.PeeweeException as exc:
					logger.error(log_msg('database error: {}'.format(exc)))
					error(self, 'Database error: {}'.format(exc))
				except Exception as exc:
					logger.error(log_msg('unknown error: {}'.format(exc), 0))
					error(self, 'Error occurred: {}'.format(exc))
				self.parent.takeItem(self.parent.currentRow())
				self.update_day(self.parent.count() < 1)
		else:
			popup.info(self.parent, 'Event is already removed!')

	def process_menu_events(self, action):
		if action == self.menu_actions['delete']:
			self.remove_event()
