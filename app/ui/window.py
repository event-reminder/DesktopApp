from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.ui import settings
from app.ui.utils import creator, popup
from app.ui.widgets.calendar_widget import CalendarWidget


class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.window().setWindowTitle(settings.APP_NAME)
		self.resize(settings.APP_WIDTH, settings.APP_HEIGHT)
		self.setWindowIcon(QIcon(settings.APP_ICON))
		self.calendar = CalendarWidget(self, self.width(), self.height())
		self.calendar.set_status_bar(self.statusBar())
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')

	def resizeEvent(self, event):
		self.calendar.resize_handler()
		QMainWindow.resizeEvent(self, event)

	def setup_navigation_menu(self):
		self.statusBar()
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu=main_menu)

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&File')
		file_menu.addAction(creator.new_action(self, '&Open', 'Ctrl+O', 'Open file', self.hello_world))

	def hello_world(self):
		popup.question(self, 'Would you like to say \"Hello, World!\"?', 'Hello, World!')
