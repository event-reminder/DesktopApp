from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import peewee

from datetime import datetime

from app.reminder.db import storage

from app.ui.utils.popup import error
from app.ui.widgets.ui_models.create_event import CreateEventDialogUI
from app.ui.widgets.ui_models.retrieve_events import RetrieveEventsDialogUI


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, width, height):
		super().__init__()
		self.parent = parent
		self.setGeometry(0, 0, width, height)
		self.setGridVisible(True)
		# noinspection PyUnresolvedReferences
		self.clicked[QDate].connect(self.show_events)
		self.status_bar = None
		self.event_retrieving_dialog = QDialog(flags=self.windowFlags())
		self.event_retrieving_dialog.ui = RetrieveEventsDialogUI(
			self.event_retrieving_dialog, self.delete_event_reminder_handler
		)
		self.event_creation_dialog = QDialog(flags=self.windowFlags())
		self.event_creation_dialog.ui = CreateEventDialogUI(
			self.event_creation_dialog, self.save_event_reminder_handler
		)

	def contextMenuEvent(self, event):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			menu = QMenu(self)
			create_action = menu.addAction('Create new event')
			action = menu.exec_(self.mapToGlobal(event.pos()))
			if action == create_action:
				self.create_event()

	def set_status_bar(self, status_bar):
		self.status_bar = status_bar

	def resize_handler(self):
		self.resize(self.parent.width(), self.parent.height() - 20)

	def reset_status(self):
		self.set_status('Ok')

	def set_status(self, msg):
		self.status_bar.showMessage('Status: {}'.format(msg))

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

	def delete_event_reminder_handler(self, pk):
		try:
			storage.delete_event(pk)
		except peewee.PeeweeException as exc:
			error(self, 'Database error: {}'.format(exc))
		except Exception as exc:
			error(self, 'Error occurred: {}'.format(exc))

	def show_events(self, date):
		py_date = date.toPyDate()
		if datetime.now().date() <= py_date:
			events = storage.get_events(py_date)
			if len(events) > 0:
				self.reset_status()
				self.event_retrieving_dialog.ui.set_data(events, py_date)
				self.event_retrieving_dialog.exec_()
				return True
		self.set_status('there is not any events for {}'.format(py_date))

	def create_event(self):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			self.reset_status()
			self.event_creation_dialog.ui.reset_inputs(date)
			self.event_creation_dialog.exec_()
		else:
			self.set_status('can\'t set reminder to the past')
