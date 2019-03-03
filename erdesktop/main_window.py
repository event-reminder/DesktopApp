from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QAction, QMainWindow, qApp, QMenu, QSystemTrayIcon

from erdesktop.widgets import CalendarWidget
from erdesktop.settings import Settings, APP_NAME, AVAILABLE_LOCALES


class MainWindow(QMainWindow):

	def __init__(self, **kwargs):
		self.settings = Settings()
		super().__init__(None, Qt.WindowStaysOnTopHint if self.settings.is_always_on_top else Qt.WindowFlags())

		self.window().setWindowTitle(APP_NAME)
		self.resize(self.settings.app_size)
		self.move(self.settings.app_pos)
		self.setWindowIcon(self.settings.app_icon(icon_size='medium'))
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.setFont(QFont('SansSerif', self.settings.app_font))

		self.open_action = QAction('{} {}'.format(self.tr('Open'), APP_NAME), self)
		self.hide_action = QAction(self.tr('Minimize To Tray'), self)
		if not self.settings.start_in_tray:
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
		calendar.setLocale(QLocale(AVAILABLE_LOCALES[self.settings.app_lang]))
		calendar.setFirstDayOfWeek(Qt.Monday)
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

	# noinspection PyUnresolvedReferences
	@staticmethod
	def new_action(target, title, fn, shortcut=None, tip=None, icon=None):
		action = QAction(title, target)
		if shortcut:
			action.setShortcut(shortcut)
		if tip:
			action.setStatusTip(tip)
		if icon:
			action.setIcon(QIcon().fromTheme(icon))
		action.triggered.connect(fn)
		return action

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
				icon='emblem-system'
			)
		)
		file_menu.addAction(
			self.new_action(
				self, '{}...'.format(self.tr('Backup and Restore')),
				self.calendar.open_backup_and_restore,
				'Ctrl+Alt+B',
			)
		)

	def setup_help_menu(self, main_menu):
		help_menu = main_menu.addMenu('&{}'.format(self.tr('Help')))
		help_menu.addAction(
			self.new_action(self, '&{}...'.format(self.tr('Account')), self.calendar.open_account_info)
		)
		help_menu.addAction(
			self.new_action(self, '&{}'.format(self.tr('About')), self.calendar.open_about, icon='dialog-information')
		)
