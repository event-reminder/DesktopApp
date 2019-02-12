import peewee

from app.storage import Storage
from app.util import popup, error, logger, log_msg
from app.util.process import BackgroundProcess

from PyQt5.QtCore import pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QMenu, QLabel, QWidget, QVBoxLayout, QMessageBox


# noinspection PyArgumentList
class EventWidget(QWidget):

	def __init__(self, parent, **kwargs):
		super(EventWidget, self).__init__(parent)
		self.titleLabel = QLabel()
		self.timeLabel = QLabel()
		self.parent = parent
		self.setup_content()
		self.menu, self.menu_actions = self.setup_menu()
		self.id = -1
		self.date = None
		self.update_day = kwargs['update_day']
		self.storage = kwargs.get('storage', Storage())

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
		if self.storage.event_exists(self.id):
			ret_action = popup.question(self.parent, 'Deleting an event', 'Do you really want to delete the event?')
			if ret_action == QMessageBox.Yes:
				QThreadPool.globalInstance().start(
					BackgroundProcess(self, self.run_remove_event)
				)
		else:
			popup.info(self.parent, 'Event is already removed!')

	@pyqtSlot()
	def run_remove_event(self):
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

	def process_menu_events(self, action):
		if action == self.menu_actions['delete']:
			self.remove_event()
