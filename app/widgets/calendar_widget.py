import peewee

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from datetime import datetime

from app.utils import (
	info,
	error
)
from app.db import Storage
from app.dialogs import (
	SettingsDialog,
	EventsListDialog,
	CreateEventDialog
)
from app.settings import Settings


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, **kwargs):
		super().__init__(parent=parent)
		self.parent = parent

		self.setGeometry(0, 0, kwargs['width'], kwargs['height'])
		self.setGridVisible(True)

		# noinspection PyUnresolvedReferences
		self.clicked[QDate].connect(self.show_events)
		self.status_bar = None

		settings = Settings()

		self.storage = Storage(connect=False)

		font = QFont('SansSerif', settings.font)

		self.event_retrieving_dialog = EventsListDialog(
			flags=self.parent.windowFlags(),
			calendar=self,
			palette=settings.theme,
			font=font
		)

		self.event_creation_dialog = CreateEventDialog(
			flags=self.parent.windowFlags(),
			calendar=self,
			storage=self.storage,
			palette=settings.theme,
			font=font
		)

		self.settings_dialog = SettingsDialog(
			flags=self.parent.windowFlags(),
			calendar=self,
			palette=settings.theme,
			font=font
		)
		self.setFont(font)
		self.setPalette(settings.theme)

		self.marked_dates = []
		self.update()

	@staticmethod
	def events_to_dates(events):
		return [event.date for event in events]

	def update(self, *__args):
		super().update()
		try:
			self.storage.connect()
			self.marked_dates = self.events_to_dates(self.storage.get_events())
		except peewee.PeeweeException:
			info(self, 'Can\'t find related database, it will be created automatically')
		except Exception as exc:
			error(self, 'Error occurred: {}'.format(exc))

	def closeEvent(self, event):
		super(CalendarWidget, self).closeEvent(event)
		self.storage.disconnect()

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

	@staticmethod
	def get_badge_width(num):
		minimum = 20
		if num > 9:
			minimum += 9
		return minimum + (55 if num > 1 else 50)

	def paint_date(self, date, painter, rect, num):
		settings = Settings()
		ellipse_rect = QRect(rect.x() + 3, rect.y() + 3, self.get_badge_width(num), 20)
		text_rect = QRect(ellipse_rect.x() - 3.1, ellipse_rect.y() + 7, 20, 20)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(settings.badge_color))
		else:
			painter.setBrush(QColor(196, 196, 196))
		painter.setPen(Qt.NoPen)
		painter.drawRect(ellipse_rect)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(settings.badge_letter_color))
		else:
			painter.setBrush(QColor(255, 255, 255))
		painter.setPen(QPen(QColor(255, 255, 255)))
		painter.drawText(text_rect.center(), '{} event{}'.format(num, 's' if num > 1 else ''))

	def set_status_bar(self, status_bar):
		self.status_bar = status_bar

	def resize_handler(self):
		self.resize(self.parent.width(), self.parent.height() - 20)

	def reset_status(self):
		self.set_status('Ok')

	def set_status(self, msg):
		self.status_bar.showMessage('Status: {}'.format(msg))

	def show_events(self, date):
		py_date = date.toPyDate()
		if datetime.now().date() <= py_date:
			try:
				events = self.storage.get_events(py_date)
				if len(events) > 0:
					self.reset_status()
					self.event_retrieving_dialog.set_data(events, py_date)
					self.event_retrieving_dialog.exec_()
					return True
			except peewee.PeeweeException as exc:
				error(self, 'Database error: {}'.format(exc))
		self.set_status('there is not any events for {}'.format(py_date))

	def create_event(self):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			self.reset_status()
			self.event_creation_dialog.reset_inputs(date)
			self.event_creation_dialog.exec_()
		else:
			self.set_status('can\'t set reminder to the past')

	def open_settings(self):
		self.settings_dialog.exec_()

	def open_backup_and_restore(self):
		print('backup and restore')
