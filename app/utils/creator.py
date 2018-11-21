from PyQt5.QtWidgets import *


def new_action(target, title, shortcut, tip, fn):
	action = QAction(title, target)
	action.setShortcut(shortcut)
	action.setStatusTip(tip)
	action.triggered.connect(fn)
	return action
