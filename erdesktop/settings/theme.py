from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


def dark_theme_palette():
	palette = QPalette()
	palette.setColor(QPalette.Window, QColor(55, 55, 55))
	palette.setColor(QPalette.WindowText, Qt.white)

	palette.setColor(QPalette.Base, QColor(53, 53, 53))
	palette.setColor(QPalette.Disabled, QPalette.Base, QColor(73, 73, 73))

	palette.setColor(QPalette.AlternateBase, QColor(63, 63, 63))
	palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
	palette.setColor(QPalette.ToolTipText, Qt.white)

	palette.setColor(QPalette.Text, Qt.white)
	palette.setColor(QPalette.Disabled, QPalette.Text, Qt.gray)

	palette.setColor(QPalette.Button, QColor(53, 53, 53))
	palette.setColor(QPalette.Disabled, QPalette.Button, QColor(73, 73, 73))
	palette.setColor(QPalette.ButtonText, Qt.white)
	palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.gray)

	palette.setColor(QPalette.BrightText, Qt.red)
	palette.setColor(QPalette.Link, QColor(42, 130, 218))
	palette.setColor(QPalette.Highlight, QColor(45, 45, 45))
	palette.setColor(QPalette.HighlightedText, Qt.white)
	return palette


def light_theme_palette():
	return QPalette()
