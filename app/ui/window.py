from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui import utils
from app.settings import Settings
from app.ui.widgets.calendar_widget import CalendarWidget


class Window(QMainWindow):

	def __init__(self):
		self.settings = Settings()
		if self.settings.user.is_always_on_top:
			super().__init__(None, Qt.WindowStaysOnTopHint)
		else:
			super().__init__()
		self.window().setWindowTitle(self.settings.app.name)
		self.resize(self.settings.app.size)
		self.move(self.settings.app.pos)
		self.setWindowIcon(self.settings.app.icon())
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')

		self.open_action = QAction('Open {}'.format(self.settings.app.name), self)
		self.hide_action = QAction('Minimize To Tray', self)
		self.close_action = QAction('Quit {}'.format(self.settings.app.name), self)

		self.tray_icon = self.init_tray_icon()

		self.setPalette(self.settings.app.theme)

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def quit_app(self):
		self.settings.app.autocommit(False)
		self.settings.app.set_pos(self.pos())
		self.settings.app.set_size(self.size())
		self.settings.app.commit()
		qApp.quit()

	def init_tray_icon(self):
		tray_icon = QSystemTrayIcon(self)
		tray_icon.setIcon(self.settings.app.icon())
		actions = {
			self.open_action: self.show,
			self.hide_action: self.hide,
			self.close_action: self.quit_app
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
		calendar.setFont(self.settings.user.font)
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
			utils.create_action(self, 'New Event', 'Ctrl+N', 'Create event', self.calendar.create_event)
		)
		file_menu.addAction(
			utils.create_action(self, 'Settings...', 'Ctrl+Alt+S', 'Settings', self.calendar.open_settings)
		)

	def enterEvent(self, event):
		super().enterEvent(event)
		self.setWindowOpacity(self.settings.user.mouse_enter_opacity)

	def leaveEvent(self, event):
		super().leaveEvent(event)
		self.setWindowOpacity(self.settings.user.mouse_leave_opacity)
