from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils import creator
from app.settings.app_settings import (
	APP_NAME,
	APP_ICON_LIGHT,
	APP_WIDTH,
	APP_HEIGHT
)
from app.settings.custom_settings import (
	APP_FONT,
	ALWAYS_ON_TOP,
	MOUSE_LEAVE_OPACITY,
	MOUSE_ENTER_OPACITY
)
from app.ui.widgets.calendar_widget import CalendarWidget


class Window(QMainWindow):

	def __init__(self):
		if ALWAYS_ON_TOP:
			super().__init__(None, Qt.WindowStaysOnTopHint)
		else:
			super().__init__()
		self.window().setWindowTitle(APP_NAME)
		self.resize(APP_WIDTH, APP_HEIGHT)
		self.setWindowIcon(QIcon(APP_ICON_LIGHT))
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')
		self.open_action = QAction('Open {}'.format(APP_NAME), self)
		self.hide_action = QAction('Minimize To Tray', self)
		self.close_action = QAction('Quit {}'.format(APP_NAME), self)
		self.tray_icon = self.init_tray_icon()

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def init_tray_icon(self):
		tray_icon = QSystemTrayIcon(self)
		tray_icon.setIcon(QIcon(APP_ICON_LIGHT))
		actions = {
			self.open_action: self.show,
			self.hide_action: self.hide,
			self.close_action: qApp.quit
		}
		tray_menu = QMenu()
		for key, value in actions.items():
			key.triggered.connect(value)
			tray_menu.addAction(key)
		tray_icon.setContextMenu(tray_menu)
		tray_icon.show()
		return tray_icon

	def init_calendar(self):
		calendar = CalendarWidget(self, self.width(), self.height())
		calendar.setLocale(QLocale(QLocale.English))
		calendar.setFont(QFont(APP_FONT))
		calendar.set_status_bar(self.statusBar())
		return calendar

	def hide(self):
		super().hide()
		self.hide_action.setEnabled(False)
		self.open_action.setEnabled(True)

	def show(self):
		super().show()
		self.hide_action.setEnabled(True)
		self.open_action.setEnabled(False)

	def resizeEvent(self, event):
		self.calendar.resize_handler()
		QMainWindow.resizeEvent(self, event)

	def setup_navigation_menu(self):
		self.statusBar()
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu=main_menu)

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&File')
		file_menu.addAction(
			creator.new_action(self, '&New Event', 'Ctrl+N', 'Create event', self.calendar.create_event)
		)

	def enterEvent(self, event):
		super().enterEvent(event)
		self.setWindowOpacity(MOUSE_ENTER_OPACITY)

	def leaveEvent(self, event):
		super().leaveEvent(event)
		self.setWindowOpacity(MOUSE_LEAVE_OPACITY)
