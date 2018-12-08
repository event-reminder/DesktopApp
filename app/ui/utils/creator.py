from PyQt5.QtWidgets import *


def new_action(target, title, shortcut, tip, fn):
	action = QAction(title, target)
	action.setShortcut(shortcut)
	action.setStatusTip(tip)
	action.triggered.connect(fn)
	return action


def new_button(name, w, h, fn):
	btn = QPushButton(name)
	btn.resize(w, h)
	btn.clicked.connect(fn)
	return btn
