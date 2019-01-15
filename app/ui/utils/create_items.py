from PyQt5.QtWidgets import QAction, QPushButton


def create_action(target, title, shortcut, tip, fn):
	action = QAction(title, target)
	action.setShortcut(shortcut)
	action.setStatusTip(tip)
	action.triggered.connect(fn)
	return action


def create_button(name, w, h, fn):
	btn = QPushButton(name)
	btn.resize(w, h)
	btn.clicked.connect(fn)
	return btn
