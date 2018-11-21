import sys

from PyQt5.QtWidgets import *

from app.window import Window


if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = Window()
	w.show()
	sys.exit(app.exec_())
