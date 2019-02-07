from PyQt5.QtWidgets import QPushButton


def button(title, width, height, function):
	btn = QPushButton(title)
	btn.resize(width, height)
	btn.clicked.connect(function)
	return btn
