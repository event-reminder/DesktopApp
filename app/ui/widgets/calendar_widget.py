from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import peewee

from datetime import datetime

from app.reminder.db import storage

from app.ui.utils.popup import error
from app.ui.widgets.ui_models.create_event import CreateEventDialogUI


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, width, height):
		super().__init__()
		self.parent = parent
		self.setGeometry(0, 0, width, height)
		self.setGridVisible(True)
		# noinspection PyUnresolvedReferences
		self.clicked[QDate].connect(self.show_date)
		self.status_bar = None
		self.event_creation_dialog = QDialog(flags=self.windowFlags())
		self.event_creation_dialog.ui = CreateEventDialogUI(
			self.event_creation_dialog, self.save_event_reminder_handler
		)

	def set_status_bar(self, status_bar):
		self.status_bar = status_bar

	def reset_status(self):
		self.status_bar.showMessage('Status: Ok')

	def resize_handler(self):
		self.resize(self.parent.width(), self.parent.height())

	def save_event_reminder_handler(self, title, date, time, description):
		try:
			self.status_bar.showMessage('Status: Saving...')
			storage.connect()
			storage.create_event(title, date, time, description)
			storage.disconnect()
		except peewee.PeeweeException as exc:
			error(self, 'Database error: {}'.format(exc))
		except Exception as exc:
			error(self, 'Error occurred: {}'.format(exc))
		self.reset_status()

	def show_date(self, date):
		if datetime.now().date() <= date:
			self.reset_status()
			self.event_creation_dialog.ui.reset_inputs(date)
			self.event_creation_dialog.exec_()
		else:
			self.status_bar.showMessage('Status: can\'t set reminder to the past')
