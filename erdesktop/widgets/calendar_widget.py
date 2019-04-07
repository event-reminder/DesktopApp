from datetime import datetime

from PyQt5.QtGui import QFont, QColor, QPen
from PyQt5.QtCore import Qt, QRect, QDate, QThreadPool
from PyQt5.QtWidgets import QCalendarWidget, QMenu, QMessageBox

from erdesktop.storage import Storage
from erdesktop.settings import Settings
from erdesktop.cloud import CloudStorage
from erdesktop.util import logger, log_msg, Worker
from erdesktop.widgets.util import info, error, popup
from erdesktop.settings import FONT_LARGE, FONT_NORMAL
from erdesktop.dialogs.about_dialog import AboutDialog
from erdesktop.util.exceptions import DatabaseException
from erdesktop.dialogs.backup_dialog import BackupDialog
from erdesktop.dialogs.account_dialog import AccountDialog
from erdesktop.dialogs.settings_dialog import SettingsDialog
from erdesktop.dialogs.event_details_dialog import EventDetailsDialog
from erdesktop.settings.default import BADGE_COLOR, BADGE_LETTER_COLOR


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, **kwargs):
		super().__init__(parent=parent)
		self.parent = parent

		self.setGeometry(0, 0, kwargs['width'], kwargs['height'])
		self.setGridVisible(True)

		# noinspection PyUnresolvedReferences
		self.clicked[QDate].connect(self.load_events)

		self.setContentsMargins(0, 0, 0, 0)

		self.events_list = kwargs.get('events_list', None)
		if self.events_list is None:
			raise RuntimeError('CalendarWidget: events list is not set')

		self.storage = Storage()

		self.thread_pool = QThreadPool()

		self.settings = Settings()
		font = QFont('SansSerif', self.settings.app_font)
		self.setFont(font)
		self.setPalette(self.settings.app_theme)

		self.cloud_storage = CloudStorage()

		params = {
			'font': font,
			'calendar': self,
			'flags': self.parent.windowFlags(),
			'palette': self.settings.app_theme,
			'parent': self
		}

		self.event_details_dialog = EventDetailsDialog(storage=self.storage, **params)
		self.settings_dialog = SettingsDialog(cloud_storage=self.cloud_storage, **params)
		self.backup_dialog = BackupDialog(storage=self.storage, cloud_storage=self.cloud_storage, **params)

		self.dialogs = [
			self.event_details_dialog,
			self.settings_dialog,
			self.backup_dialog
		]

		self.marked_dates = []
		self.past_events = []

		self.update()

	@staticmethod
	def events_to_dates(events):
		events_dates = []
		past_events = []
		for event in events:
			events_dates.append(event.date)
			if event.is_past:
				past_events.append(event.date)
		return events_dates, past_events

	def showEvent(self, event):
		super().showEvent(event)
		self.load_events(self.selectedDate())

	def update(self, *__args):
		try:
			self.marked_dates, self.past_events = self.events_to_dates(self.storage.get_events())
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
				self.open_details_event()
		super(CalendarWidget, self).contextMenuEvent(event)

	def paintCell(self, painter, rect, date, **kwargs):
		QCalendarWidget.paintCell(self, painter, rect, date)
		if date.toPyDate() in self.marked_dates:
			self.paint_date(
				date, painter, rect, self.marked_dates.count(date.toPyDate()), date.toPyDate() in self.past_events
			)

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

	def paint_date(self, date, painter, rect, num, is_past):
		font_not_large = self.settings.app_font != FONT_LARGE
		ellipse_rect = QRect(
			rect.x() + 3, rect.y() + 3, self.get_badge_width(num, self.settings.app_font), 20 if font_not_large else 25
		)
		text_rect = QRect(ellipse_rect.x() - 3.1, ellipse_rect.y() + (7 if font_not_large else 10), 20, 20)
		if self.monthShown() == date.month():
			if is_past:
				painter.setBrush(QColor(0, 0, 0))
			else:
				painter.setBrush(QColor(BADGE_COLOR))
		else:
			painter.setBrush(QColor(196, 196, 196))
		painter.setPen(Qt.NoPen)
		painter.drawRect(ellipse_rect)
		if self.monthShown() == date.month():
			painter.setBrush(QColor(BADGE_LETTER_COLOR))
		else:
			painter.setBrush(QColor(255, 255, 255))
		painter.setPen(QPen(QColor(255, 255, 255)))
		num_repr = repr(num)
		if len(num_repr) > 1 and int(num_repr[-2]) == 1:
			text = self.tr('events')
		elif 1 < int(num_repr[-1]) < 5:
			text = self.tr('events*')
		else:
			text = self.tr('event{}'.format('s' if int(num_repr[-1]) > 1 or num % 2 == 0 else ''))
		painter.drawText(text_rect.center(), '{} {}'.format(num, text))

	def edit_event_click(self):
		self.event_details_dialog.reset_inputs(
			event_data=self.events_list.selected_item
		)
		self.event_details_dialog.exec_()

	def perform_deleting(self, title, description, fn, *args, **kwargs):
		if popup.question(self, self.tr(title), '{}?'.format(self.tr(description))) == QMessageBox.Yes:
			worker = Worker(fn, *args, **kwargs)
			worker.signals.success.connect(self.perform_deleting_success)
			worker.err_format = '{}'
			worker.signals.error.connect(self.popup_error)
			self.thread_pool.start(worker)

	def perform_deleting_success(self):
		self.load_events(self.selectedDate())
		self.update()

	def delete_event_click(self):
		if len(self.events_list.selected_ids()) > 1:
			self.perform_deleting(
				self.tr('Deleting events'),
				self.tr('Do you really want to delete events'),
				self.delete_events,
				*(self.events_list.selected_ids(),)
			)
		else:
			if self.storage.event_exists(self.events_list.selected_item.id):
				self.perform_deleting(
					self.tr('Deleting an event'),
					'{}?'.format(self.tr('Do you really want to delete the event')),
					self.storage.delete_event,
					*(self.events_list.selected_item.id,)
				)

	def delete_events(self, events_ids):
		for pk in events_ids:
			if self.storage.event_exists(pk):
				self.storage.delete_event(pk)

	def load_events(self, date):
		py_date = date.toPyDate()
		try:
			events = self.storage.get_events(py_date)
			if len(events) > 0:
				self.events_list.set_data(events)
			else:
				self.events_list.set_empty()
			return True
		except DatabaseException as exc:
			logger.error(log_msg('database error: {}'.format(exc), 7))
			error(self, '{}\n{}'.format(self.tr('Database error'), exc))

	def open_details_event(self):
		date = self.selectedDate().toPyDate()
		if datetime.now().date() <= date:
			self.event_details_dialog.reset_inputs(date=date)
			self.event_details_dialog.exec_()
		else:
			info(self, self.tr('Can not set reminder to the past'))

	def open_settings(self):
		self.settings_dialog.exec_()

	def open_backup_and_restore(self):
		self.backup_dialog.exec_()

	def open_account_info(self):
		dialog = AccountDialog(
			flags=self.parent.windowFlags(),
			palette=self.settings.app_theme,
			calendar=self,
			parent=self,
			cloud_storage=self.cloud_storage,
			font=QFont('SansSerif', self.settings.app_font)
		)
		dialog.setAttribute(Qt.WA_DeleteOnClose, True)
		dialog.exec_()

	def open_about(self):
		dialog = AboutDialog(
			flags=self.parent.windowFlags(),
			calendar=self,
			palette=self.settings.app_theme
		)
		dialog.setAttribute(Qt.WA_DeleteOnClose, True)
		dialog.exec_()

	def popup_error(self, err):
		popup.error(self, '{}'.format(err[1]))
