import qtawesome as qta

from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
	QAction, QMainWindow, qApp, QMenu, QSystemTrayIcon, QHBoxLayout, QScrollArea, QWidget, QVBoxLayout
)
from PyQt5.QtCore import Qt, QLocale

from erdesktop.util import logger, log_msg
from erdesktop.widgets import CalendarWidget
from erdesktop.system import system, shortcut_icon
from erdesktop.widgets.util import error, info, PushButton
from erdesktop.widgets.event_list_widget import EventListWidget
from erdesktop.util.exceptions import ShortcutIconIsNotSupportedError
from erdesktop.settings import Settings, APP_NAME, AVAILABLE_LOCALES, APP_MIN_WIDTH, APP_MIN_HEIGHT


class MainWindow(QMainWindow):

	def __init__(self, **kwargs):
		self.settings = Settings()
		super().__init__(None, Qt.WindowFlags())

		self.window().setWindowTitle(APP_NAME)
		self.resize(self.settings.app_size)
		self.move(self.settings.app_pos)
		self.setWindowIcon(self.settings.app_icon())
		self.setMinimumWidth(APP_MIN_WIDTH)
		self.setMinimumHeight(APP_MIN_HEIGHT)

		self.events_list = EventListWidget(**{
			'parent': self,
		})

		# noinspection PyUnresolvedReferences
		self.events_list.itemSelectionChanged.connect(self.events_list_selection_changed)

		self.calendar = self.init_calendar()

		self.btn_new_event = PushButton(self.tr('New'), 90, 30, self.calendar.open_details_event)
		self.btn_edit = PushButton(self.tr('Details'), 90, 30, self.calendar.edit_event_click)
		self.btn_delete = PushButton(self.tr('Delete'), 90, 30, self.calendar.delete_event_click)
		events_widget = self.init_events_widget()

		main_layout = QHBoxLayout()

		# noinspection PyArgumentList
		main_layout.addWidget(self.calendar)
		main_layout.addWidget(events_widget, alignment=Qt.AlignRight)

		central_widget = QWidget(flags=self.windowFlags())
		central_widget.setLayout(main_layout)

		self.setCentralWidget(central_widget)

		# noinspection PyUnresolvedReferences
		self.calendar.selectionChanged.connect(self.date_selection_changed)

		self.setup_navigation_menu()
		self.setFont(QFont('SansSerif', self.settings.app_font))

		self.open_action = QAction('{} {}'.format(self.tr('Open'), APP_NAME), self)
		self.hide_action = QAction(self.tr('Minimize To Tray'), self)
		if self.settings.start_in_tray:
			self.hide_action.setEnabled(False)
		self.close_action = QAction('{} {}'.format(self.tr('Quit'), APP_NAME), self)

		self.tray_icon = self.init_tray(kwargs.get('app'))
		self.tray_icon.show()

		self.setPalette(self.settings.app_theme)

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def date_selection_changed(self):
		if self.calendar.selectedDate().toPyDate() < datetime.today().date():
			self.btn_new_event.setEnabled(False)
		else:
			self.btn_new_event.setEnabled(True)

	def save_state(self):
		self.settings.autocommit(False)
		self.settings.set_pos(self.pos())
		self.settings.set_size(self.size())
		self.settings.commit()

	def quit_app(self):
		self.save_state()
		qApp.quit()

	def init_tray(self, app):
		actions = {
			self.open_action: self.show,
			self.hide_action: self.hide,
			self.close_action: self.quit_app
		}
		tray_menu = QMenu()
		for key, value in actions.items():

			# noinspection PyUnresolvedReferences
			key.triggered.connect(value)
			tray_menu.addAction(key)
		tray_icon = QSystemTrayIcon(self.settings.app_icon(), app)
		tray_icon.setContextMenu(tray_menu)
		return tray_icon

	def init_calendar(self):
		calendar = CalendarWidget(
			self,
			width=self.width() - 400,
			height=self.height(),
			events_list=self.events_list
		)
		calendar.setLocale(QLocale(AVAILABLE_LOCALES[self.settings.app_lang]))
		calendar.setFirstDayOfWeek(Qt.Monday)
		calendar.setSelectedDate(datetime.now())
		return calendar

	def init_events_widget(self):
		scroll_view = QScrollArea()
		scroll_view.setWidget(self.events_list)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedWidth(400)

		layout = QVBoxLayout()

		# noinspection PyArgumentList
		layout.addWidget(scroll_view)

		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)

		buttons.addWidget(self.btn_new_event, 0, Qt.AlignLeft)

		self.btn_edit.setEnabled(False)
		buttons.addWidget(self.btn_edit, 0, Qt.AlignCenter)

		self.btn_delete.setEnabled(False)
		buttons.addWidget(self.btn_delete, 0, Qt.AlignRight)

		layout.addLayout(buttons)

		widget = QWidget(flags=self.windowFlags())
		widget.setLayout(layout)
		return widget

	def events_list_selection_changed(self):
		if self.events_list.selected_item is not None:
			if len(self.events_list.selected_ids()) == 1:
				self.btn_edit.setEnabled(True)
			else:
				self.btn_edit.setEnabled(False)
			self.btn_delete.setEnabled(True)
		else:
			self.btn_edit.setEnabled(False)
			self.btn_delete.setEnabled(False)

	def hide(self):
		self.hide_action.setEnabled(False)
		self.open_action.setEnabled(True)
		super(MainWindow, self).hide()

	def show(self):
		self.hide_action.setEnabled(True)
		self.open_action.setEnabled(False)
		super(MainWindow, self).show()

	def setup_navigation_menu(self):
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu)
		self.setup_help_menu(main_menu)

	@staticmethod
	def create_action(target, title, fn, shortcut=None, tip=None, icon=None):
		action = QAction(title, target)
		if shortcut:
			action.setShortcut(shortcut)
		if tip:
			action.setStatusTip(tip)
		if icon:
			action.setIcon(icon)

		# noinspection PyUnresolvedReferences
		action.triggered.connect(fn)
		return action

	def create_shortcut(self):
		try:
			shortcut_icon.create()
			info(self, self.tr('Shortcut icon has been created'))
		except ShortcutIconIsNotSupportedError:
			error(self, self.tr('Shortcut icon is not supported on {} by application').format(system.name()))
		except Exception as exc:
			logger.error(log_msg('Unable to create shortcut icon: {}'.format(exc)))
			error(self, self.tr('Unable to create shortcut icon'))

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&{}'.format(self.tr('File')))
		file_menu.addAction(
			self.create_action(
				self,
				'{}...'.format(self.tr('New Event')),
				self.calendar.open_details_event,
				'Ctrl+N'
			)
		)
		file_menu.addAction(
			self.create_action(
				self,
				'{}...'.format(self.tr('Se{}ttings').format('&')),
				self.calendar.open_settings,
				'Ctrl+Alt+S',
				icon=qta.icon('mdi.settings')
			)
		)
		file_menu.addAction(self.create_action(
			self,
			'&{}'.format(self.tr('Create shortcut icon...')),
			self.create_shortcut,
			icon=qta.icon('mdi.desktop-mac')
		))
		file_menu.addAction(
			self.create_action(
				self, '{}...'.format(self.tr('Backup and Restore')),
				self.calendar.open_backup_and_restore,
				'Ctrl+Alt+B',
				icon=qta.icon('mdi.backup-restore')
			)
		)

	def setup_help_menu(self, main_menu):
		help_menu = main_menu.addMenu('&{}'.format(self.tr('Help')))
		help_menu.addAction(self.create_action(
			self, '&{}...'.format(self.tr('Account')),
			self.calendar.open_account_info,
			icon=qta.icon('mdi.account-circle')
		))
		help_menu.addAction(self.create_action(
			self, '&{}'.format(self.tr('About')), self.calendar.open_about, icon=qta.icon('mdi.information-outline')
		))
