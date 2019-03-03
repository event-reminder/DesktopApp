from datetime import datetime

from PyQt5.QtCore import Qt, QRect, QDate
from PyQt5.QtGui import QFont, QColor, QPen
from PyQt5.QtWidgets import QCalendarWidget, QMenu

from erdesktop.storage import Storage
from erdesktop.settings import Settings
from erdesktop.cloud import CloudStorage
from erdesktop.util import logger, log_msg
from erdesktop.widgets.util import info, error
from erdesktop.util.exceptions import DatabaseException
from erdesktop.settings import FONT_LARGE, FONT_NORMAL
from erdesktop.dialogs import AboutDialog, BackupDialog, AccountDialog, SettingsDialog, EventsListDialog, CreateEventDialog


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, **kwargs):
		super().__init__(parent=parent)
		self.parent = parent

		self.setGeometry(0, 0, kwargs['width'], kwargs['height'])
		self.setGridVisible(True)

		# noinspection PyUnresolvedReferences
		self.clicked[QDate].connect(self.open_events)

		self.settings = Settings()
		font = QFont('SansSerif', self.settings.app_font)
		self.setFont(font)
		self.setPalette(self.settings.app_theme)

		self.storage = Storage()
		self.cloud_storage = CloudStorage()

		params = {
			'font': font,
			'calendar': self,
			'flags': self.parent.windowFlags(),
			'palette': self.settings.app_theme
		}

		self.event_creation_dialog = CreateEventDialog(storage=self.storage, **params)
		self.event_retrieving_dialog = EventsListDialog(**params)
		self.settings_dialog = SettingsDialog(cloud_storage=self.cloud_storage, **params)
		self.backup_dialog = BackupDialog(storage=self.storage, cloud_storage=self.cloud_storage, **params)

		self.dialogs = [
			self.event_retrieving_dialog,
			self.event_creation_dialog,
			self.settings_dialog,
			self.backup_dialog
		]

		self.marked_dates = []
		self.update()

	@staticmethod
	def events_to_dates(events):
		return [event.date for event in events]

	def update(self, *__args):
		try:
			self.marked_dates = self.events_to_dates(self.storage.get_events())
		except DatabaseException:
			info(self, self.tr('Unable to find related database, it will be created automatically'))
		except Exception as exc:
			logger.error(log_msg('Unknown error: {}'.format(exc)))
			error(self, '{}: {}'.format(self.tr('Error occurred'), exc))
		super(CalendarWidget, self).update(*__args)

	def closeEvent(self, event):
		self.storage.disconnect()
		super(CalendarWidget, self).closeEvent(event)

	def contextMenuEvent(self, event):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			menu = QMenu(self)
			create_action = menu.addAction(self.tr('Create new event'))
			action = menu.exec_(self.mapToGlobal(event.pos()))
			if action == create_action:
				self.open_create_event()
		super(CalendarWidget, self).contextMenuEvent(event)

	def paintCell(self, painter, rect, date, **kwargs):
		QCalendarWidget.paintCell(self, painter, rect, date)
		if date.toPyDate() in self.marked_dates:
			self.paint_date(date, painter, rect, self.marked_dates.count(date.toPyDate()))

	def reset_font(self, font):
		self.setFont(font)
		self.parent.setFont(font)
		for dialog in self.dialogs:
			dialog.setFont(font)

	def reset_palette(self, palette):
		self.setPalette(palette)
		self.parent.setPalette(palette)
		for dialog in self.dialogs:
			dialog.setPalette(palette)

	@staticmethod
	def get_badge_width(num, font_size=FONT_NORMAL):
		minimum = 10
		if font_size == FONT_NORMAL:
			minimum = 20
		elif font_size == FONT_LARGE:
			minimum = 35
		if num > 9:
			minimum += (9 if font_size != FONT_LARGE else 15)
		return minimum + (55 if num > 1 else 50)

	def paint_date(self, date, painter, rect, num):
		font_not_large = self.settings.app_font != FONT_LARGE
		ellipse_rect = QRect(
			rect.x() + 3, rect.y() + 3, self.get_badge_width(num, self.settings.app_font), 20 if font_not_large else 25
		)
		text_rect = QRect(ellipse_rect.x() - 3.1, ellipse_rect.y() + (7 if font_not_large else 10), 20, 20)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(self.settings.badge_color))
		else:
			painter.setBrush(QColor(196, 196, 196))
		painter.setPen(Qt.NoPen)
		painter.drawRect(ellipse_rect)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(self.settings.badge_letter_color))
		else:
			painter.setBrush(QColor(255, 255, 255))
		painter.setPen(QPen(QColor(255, 255, 255)))
		painter.drawText(text_rect.center(), '{} event{}'.format(num, 's' if num > 1 else ''))

	def resize_handler(self):
		self.resize(self.parent.width(), self.parent.height() - 20)

	def open_events(self, date):
		py_date = date.toPyDate()
		if datetime.now().date() <= py_date:
			try:
				events = self.storage.get_events(py_date)
				if len(events) > 0:
					self.event_retrieving_dialog.set_data(events, py_date)
					self.event_retrieving_dialog.exec_()
					return True
			except DatabaseException as exc:
				logger.error(log_msg('database error: {}'.format(exc), 7))
				error(self, '{}\n{}'.format(self.tr('Database error'), exc))

	def open_create_event(self):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			self.event_creation_dialog.reset_inputs(date=date)
			self.event_creation_dialog.exec_()
		else:
			info(self, self.tr('Can not set reminder to the past'))

	def open_settings(self):
		self.settings_dialog.exec_()

	def open_backup_and_restore(self):
		self.backup_dialog.exec_()

	def open_account_info(self):
		AccountDialog(
			flags=self.parent.windowFlags(),
			palette=self.settings.app_theme,
			calendar=self,
			cloud_storage=self.cloud_storage,
			font=QFont('SansSerif', self.settings.app_font)
		).exec_()

	def open_about(self):
		AboutDialog(
			flags=self.parent.windowFlags(),
			calendar=self,
			palette=self.settings.app_theme
		).exec_()
