import peewee

from datetime import datetime

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.reminder.db import storage
from app.ui.utils.popup import error, info
from app.ui.widgets.forms.events_list import EventsListForm
from app.ui.widgets.forms.create_event import CreateEventForm
from app.settings.custom_settings import MARKED_DATE_COLOR, MARKED_DATE_LETTER_COLOR


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
		self.event_retrieving_dialog.ui = EventsListForm(self.event_retrieving_dialog)
		self.event_creation_dialog = QDialog(flags=self.windowFlags())
		self.event_creation_dialog.ui = CreateEventForm(
			self.event_creation_dialog, self.save_event_reminder_handler
		)
		self.marked_dates = []
		self.update()

	@staticmethod
	def events_to_dates(events):
		return [event.date for event in events]

	def update(self, *__args):
		super().update()
		try:
			storage.connect()
			self.marked_dates = self.events_to_dates(storage.get_events())
		except peewee.PeeweeException:
			info(self, 'Can\'t find related database, it will be created automatically')
		except Exception as exc:
			error(self, 'Error occurred: {}'.format(exc))

	def closeEvent(self, event):
		super(CalendarWidget, self).closeEvent(event)
		storage.disconnect()

	def contextMenuEvent(self, event):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			menu = QMenu(self)
			create_action = menu.addAction('Create new event')
			action = menu.exec_(self.mapToGlobal(event.pos()))
			if action == create_action:
				self.create_event()

	def paintCell(self, painter, rect, date, **kwargs):
		QCalendarWidget.paintCell(self, painter, rect, date)
		if date.toPyDate() in self.marked_dates:
			self.paint_date(date, painter, rect, self.marked_dates.count(date.toPyDate()))

	def paint_date(self, date, painter, rect, num):
		ellipse_rect = QRect(rect.x() + 3, rect.y() + 3, 20, 20)
		text_rect = QRect(ellipse_rect.x() - 3.1, ellipse_rect.y() + 7, 20, 20)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(MARKED_DATE_COLOR))
		else:
			painter.setBrush(QColor(196, 196, 196))
		painter.setPen(Qt.NoPen)
		painter.drawEllipse(ellipse_rect)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(MARKED_DATE_LETTER_COLOR))
		else:
			painter.setBrush(QColor(255, 255, 255))
		painter.setPen(QPen(QColor(255, 255, 255)))
		painter.drawText(text_rect.center(), str(num))
		self.cell_is_painted = True

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

	def show_events(self, date):
		py_date = date.toPyDate()
		if datetime.now().date() <= py_date:
			try:
				events = storage.get_events(py_date)
				if len(events) > 0:
					self.reset_status()
					self.event_retrieving_dialog.ui.set_data(events, py_date)
					self.event_retrieving_dialog.ui.set_calendar_widget(self)
					self.event_retrieving_dialog.exec_()
					return True
			except peewee.PeeweeException as exc:
				error(self, 'Database error: {}'.format(exc))
		self.set_status('there is not any events for {}'.format(py_date))

	def create_event(self):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			self.reset_status()
			self.event_creation_dialog.ui.reset_inputs(date)
			self.event_creation_dialog.ui.set_calendar_widget(self)
			self.event_creation_dialog.exec_()
		else:
			self.set_status('can\'t set reminder to the past')
