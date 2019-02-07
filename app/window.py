from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app import utils
from app.settings import Settings
from app.widgets import CalendarWidget


class MainWindow(QMainWindow):

	def __init__(self, **kwargs):
		self.settings = Settings()
		if self.settings.is_always_on_top:
			super().__init__(None, Qt.WindowStaysOnTopHint)
		else:
			super().__init__()
		self.window().setWindowTitle(self.settings.app_name)
		self.resize(self.settings.app_size)
		self.move(self.settings.app_pos)
		self.setWindowIcon(self.settings.app_icon(icon_size='medium'))
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')
		self.setFont(QFont('SansSerif', self.settings.app_font))

		self.open_action = QAction('Open {}'.format(self.settings.app_name), self)
		self.hide_action = QAction('Minimize To Tray', self)
		if not self.settings.show_calendar_on_startup:
			self.hide_action.setEnabled(False)
		self.close_action = QAction('Quit {}'.format(self.settings.app_name), self)

		self.tray_icon = self.init_tray(kwargs.get('app'))
		self.tray_icon.show()

		self.setPalette(self.settings.app_theme)

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def quit_app(self):
		self.settings.autocommit(False)
		self.settings.set_pos(self.pos())
		self.settings.set_size(self.size())
		self.settings.commit()
		qApp.quit()

	# noinspection PyUnresolvedReferences
	def init_tray(self, app):
		actions = {
			self.open_action: self.show,
			self.hide_action: self.hide,
			self.close_action: self.quit_app
		}
		tray_menu = QMenu()
		for key, value in actions.items():
			key.triggered.connect(value)
			tray_menu.addAction(key)
		tray_icon = QSystemTrayIcon(self.settings.app_icon(), app)
		tray_icon.setContextMenu(tray_menu)
		return tray_icon

	def init_calendar(self):
		calendar = CalendarWidget(self, width=self.width(), height=self.height())
		calendar.setLocale(QLocale(QLocale.English))
		calendar.set_status_bar(self.statusBar())
		return calendar

	def hide(self):
		self.hide_action.setEnabled(False)
		self.open_action.setEnabled(True)
		super().hide()

	def show(self):
		self.hide_action.setEnabled(True)
		self.open_action.setEnabled(False)
		super().show()

	def resizeEvent(self, event):
		self.calendar.resize_handler()
		QMainWindow.resizeEvent(self, event)

	def setup_navigation_menu(self):
		self.statusBar()
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu)
		self.setup_help_menu(main_menu)

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&File')
		file_menu.addAction(
			utils.create_action(self, 'New Event...', self.calendar.open_create_event, 'Ctrl+N', 'Create event')
		)
		file_menu.addAction(
			utils.create_action(
				self, 'Se&ttings...', self.calendar.open_settings, 'Ctrl+Alt+S', 'Settings', 'emblem-system'
			)
		)
		file_menu.addAction(
			utils.create_action(
				self, 'Backup...', self.calendar.open_backup_and_restore, 'Ctrl+Alt+B', 'Backup and restore'
			)
		)

	def setup_help_menu(self, main_menu):
		help_menu = main_menu.addMenu('&Help')
		help_menu.addAction(
			utils.create_action(self, '&Account...', self.calendar.open_account_info)
		)
		help_menu.addAction(
			utils.create_action(
				self, '&Check for updates...', self.calendar.open_check_for_updates, icon='system-software-update'
			)
		)
		help_menu.addAction(
			utils.create_action(self, '&About', self.calendar.open_about, icon='dialog-information')
		)

	def enterEvent(self, event):
		self.setWindowOpacity(float(self.settings.mouse_enter_opacity))
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.setWindowOpacity(float(self.settings.mouse_leave_opacity))
		super().leaveEvent(event)
