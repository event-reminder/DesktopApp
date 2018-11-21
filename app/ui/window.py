from PyQt5.QtWidgets import *

from app.ui.utils import creator, popup


class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		self.window().setWindowTitle("Reminder Desktop")
		self.setFixedSize(1024, 768)
#		self.setWindowIcon(QIcon('python.png'))
	#	self.main_widget = Main()
#		self.setCentralWidget(self.main)

		self.setup_navigation_menu()

	def setup_navigation_menu(self):
		self.statusBar()
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu=main_menu)

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&File')
		file_menu.addAction(creator.new_action(self, '&Open', 'Ctrl+O', 'Open file', self.hello_world))

	def hello_world(self):
		popup.question(self, 'Would you like to say \"Hello, World!\"?', 'Hello, World!')
