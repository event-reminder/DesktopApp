from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QPushButton


def create_action(target, title, fn, shortcut=None, tip=None, icon=None):
	action = QAction(title, target)
	if shortcut:
		action.setShortcut(shortcut)
	if tip:
		action.setStatusTip(tip)
	if icon:
		action.setIcon(QIcon().fromTheme(icon))
	action.triggered.connect(fn)
	return action


def create_button(name, w, h, fn):
	btn = QPushButton(name)
	btn.resize(w, h)
	btn.clicked.connect(fn)
	return btn
