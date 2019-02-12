from PyQt5.QtGui import *
from PyQt5.QtCore import *


def _theme_palette(window, window_text, base, alternate_base, tool_tip_base,
				   tool_tip_text, text, button, button_text, bright_text, link,
				   highlight, highlighted_text):
	palette = QPalette()
	palette.setColor(QPalette.Window, window)
	palette.setColor(QPalette.WindowText, window_text)
	palette.setColor(QPalette.Base, base)
	palette.setColor(QPalette.AlternateBase, alternate_base)
	palette.setColor(QPalette.ToolTipBase, tool_tip_base)
	palette.setColor(QPalette.ToolTipText, tool_tip_text)
	palette.setColor(QPalette.Text, text)
	palette.setColor(QPalette.Button, button)
	palette.setColor(QPalette.ButtonText, button_text)
	palette.setColor(QPalette.BrightText, bright_text)
	palette.setColor(QPalette.Link, link)
	palette.setColor(QPalette.Highlight, highlight)
	palette.setColor(QPalette.HighlightedText, highlighted_text)
	return palette


def dark_theme_palette():
	return _theme_palette(
		QColor(53, 53, 53),
		Qt.white,
		QColor(25, 25, 25),
		QColor(53, 53, 53),
		Qt.white,
		Qt.white,
		Qt.white,
		QColor(53, 53, 53),
		Qt.white,
		Qt.red,
		QColor(42, 130, 218),
		QColor(42, 130, 218),
		Qt.black
	)


def light_theme_palette():
	return QPalette()
