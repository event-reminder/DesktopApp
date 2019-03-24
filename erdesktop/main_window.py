from datetime import datetime

import qtawesome as qta

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import QAction, QMainWindow, qApp, QMenu, QSystemTrayIcon

from erdesktop.widgets import CalendarWidget
from erdesktop.system import system, shortcut_icon
from erdesktop.widgets.util import error, info
from erdesktop.util import logger, log_msg
from erdesktop.util.exceptions import ShortcutIconIsNotSupportedError
from erdesktop.settings import Settings, APP_NAME, AVAILABLE_LOCALES


class MainWindow(QMainWindow):

	def __init__(self, **kwargs):
		self.settings = Settings()
		super().__init__(None, Qt.WindowStaysOnTopHint if self.settings.is_always_on_top else Qt.WindowFlags())

		self.window().setWindowTitle(APP_NAME)
		self.resize(self.settings.app_size)
		self.move(self.settings.app_pos)
		self.setWindowIcon(self.settings.app_icon(
			icon_size='medium',
			is_dark=system.is_windows()
		))
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
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
		tray_icon = QSystemTrayIcon(self.settings.app_icon(is_dark=system.is_windows()), app)
		tray_icon.setContextMenu(tray_menu)
		return tray_icon

	def init_calendar(self):
		calendar = CalendarWidget(self, width=self.width(), height=self.height())
		calendar.setLocale(QLocale(AVAILABLE_LOCALES[self.settings.app_lang]))
		calendar.setFirstDayOfWeek(Qt.Monday)
		calendar.setSelectedDate(datetime.now())
		return calendar

	def hide(self):
		self.hide_action.setEnabled(False)
		self.open_action.setEnabled(True)
		super(MainWindow, self).hide()

	def show(self):
		self.hide_action.setEnabled(True)
		self.open_action.setEnabled(False)
		super(MainWindow, self).show()

	def resizeEvent(self, event):
		self.calendar.resize_handler()
		QMainWindow.resizeEvent(self, event)
		super(MainWindow, self).resizeEvent(event)

	def setup_navigation_menu(self):
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu)
		self.setup_help_menu(main_menu)

	@staticmethod
	def new_action(target, title, fn, shortcut=None, tip=None, icon=None):
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
			error(self, self.tr('Shortcut icon is not supported on {} by application').format(system.get()))
		except Exception as exc:
			logger.error(log_msg('Unable to create shortcut icon: {}'.format(exc)))
			error(self, self.tr('Unable to create shortcut icon'))

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&{}'.format(self.tr('File')))
		file_menu.addAction(
			self.new_action(
				self,
				'{}...'.format(self.tr('New Event')),
				self.calendar.open_create_event,
				'Ctrl+N'
			)
		)
		file_menu.addAction(
			self.new_action(
				self,
				'{}...'.format(self.tr('Se{}ttings').format('&')),
				self.calendar.open_settings,
				'Ctrl+Alt+S',
				icon=qta.icon('mdi.settings')
			)
		)
		file_menu.addAction(self.new_action(
			self,
			'&{}'.format(self.tr('Create shortcut icon...')),
			self.create_shortcut,
			icon=qta.icon('mdi.desktop-mac')
		))
		file_menu.addAction(
			self.new_action(
				self, '{}...'.format(self.tr('Backup and Restore')),
				self.calendar.open_backup_and_restore,
				'Ctrl+Alt+B',
				icon=qta.icon('mdi.backup-restore')
			)
		)

	def setup_help_menu(self, main_menu):
		help_menu = main_menu.addMenu('&{}'.format(self.tr('Help')))
		help_menu.addAction(self.new_action(
			self, '&{}...'.format(self.tr('Account')),
			self.calendar.open_account_info,
			icon=qta.icon('mdi.account-circle')
		))
		help_menu.addAction(self.new_action(
			self, '&{}'.format(self.tr('About')), self.calendar.open_about, icon=qta.icon('mdi.information-outline')
		))
