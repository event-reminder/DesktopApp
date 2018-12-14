import peewee
from PyQt5.QtWidgets import *

from app.reminder.db import storage
from app.ui.utils import popup
from app.ui.utils.popup import error


class EventWidget(QWidget):
	def __init__(self, parent: QListWidget, reset_date_handler):
		super(EventWidget, self).__init__(parent)
		self.titleLabel = QLabel()
		self.timeLabel = QLabel()
		self.parent = parent
		self.setup_content()
		self.menu, self.menu_actions = self.setup_menu()
		self.id = -1
		self.date = None
		self.reset_date_handler = reset_date_handler

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
		if storage.exists(self.id):
			ret_action = popup.question(self.parent, 'Deleting an event', 'Do you really want to delete the event?')
			if ret_action == QMessageBox.Yes:
				try:
					if storage.exists(self.id):
						storage.delete_event(self.id)
				except peewee.PeeweeException as exc:
					error(self, 'Database error: {}'.format(exc))
				except Exception as exc:
					error(self, 'Error occurred: {}'.format(exc))
				self.parent.takeItem(self.parent.currentRow())
				if self.parent.count() < 1:
					self.reset_date_handler(self.date)
		else:
			popup.info(self.parent, 'Event is already removed!')

	def process_menu_events(self, action):
		if action == self.menu_actions['delete']:
			self.remove_event()
