from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils import creator
from app.settings.app_settings import (
	APP_NAME,
	APP_ICON,
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
		self.setWindowIcon(QIcon(APP_ICON))
		self.calendar = CalendarWidget(self, self.width(), self.height())
		self.calendar.setLocale(QLocale(QLocale.English))
		self.calendar.setFont(QFont(APP_FONT))
		self.calendar.set_status_bar(self.statusBar())
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')

		self.tray_icon = self.init_tray_icon()

	def closeEvent(self, event):
		event.ignore()
		self.hide()

		self.tray_icon.showMessage(
			APP_NAME,
			'Application was minimized to Tray',
			QSystemTrayIcon.Information,
			3000
		)

	def init_tray_icon(self):
		tray_icon = QSystemTrayIcon(self)
		tray_icon.setIcon(QIcon(APP_ICON))
		actions = {
			QAction('Open {}'.format(APP_NAME), self): self.show,
			QAction('Minimize To Tray', self): self.hide,
			QAction('Close {}'.format(APP_NAME), self): qApp.quit,
		}
		tray_menu = QMenu()
		for action, func in actions.items():
			action.triggered.connect(func)
			tray_menu.addAction(action)
		tray_icon.setContextMenu(tray_menu)
		tray_icon.show()
		return tray_icon

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
		self.setWindowOpacity(MOUSE_ENTER_OPACITY)

	def leaveEvent(self, event):
		self.setWindowOpacity(MOUSE_LEAVE_OPACITY)
