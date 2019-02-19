from app.storage import Storage
from app.widgets.util import popup
from app.util import logger, log_msg, Worker
from app.widgets.waiting_spinner import WaitingSpinner

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMenu, QLabel, QWidget, QVBoxLayout, QMessageBox


# noinspection PyArgumentList
class EventWidget(QWidget):

	def __init__(self, parent, **kwargs):
		super(EventWidget, self).__init__(parent)
		self.titleLabel = QLabel()
		self.timeLabel = QLabel()
		self.parent = parent
		self.menu, self.menu_actions = self.setup_menu()
		self.id = -1
		self.date = None
		self.update_day = kwargs['update_day']
		self.storage = kwargs.get('storage', Storage())
		self.thread_pool = QThreadPool()
		self.spinner = WaitingSpinner()
		self.setup_ui()
		self.layout().addWidget(self.spinner)

	def setup_ui(self):
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
				worker = Worker(self.run_remove_event)
				worker.signals.success.connect(self.remove_event_success)
				worker.signals.error.connect(self.error)
				worker.signals.finished.connect(self.stop_spinner)
				self.thread_pool.start(worker)
		else:
			popup.info(self.parent, 'Event is already removed!')

	def remove_event_success(self):
		self.parent.takeItem(self.parent.currentRow())
		self.update_day(self.parent.count() < 1)

	def run_remove_event(self):
		if self.storage.event_exists(self.id):
			self.storage.delete_event(self.id)

	def process_menu_events(self, action):
		if action == self.menu_actions['delete']:
			self.remove_event()

	def stop_spinner(self):
		self.spinner.stop()

	def error(self, err):
		logger.error(log_msg('{}'.format(err[2])))
		popup.error(self, 'Error: {}'.format(err[1]))
