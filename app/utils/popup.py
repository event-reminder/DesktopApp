from PyQt5.QtWidgets import QMessageBox


# noinspection PyArgumentList
def warning(target, msg):
	return QMessageBox.warning(target, 'Warning', msg, QMessageBox.Ok)


# noinspection PyArgumentList
def info(target, msg):
	return QMessageBox.information(target, 'Info', msg, QMessageBox.Ok)


# noinspection PyArgumentList
def error(target, msg):
	return QMessageBox.warning(target, 'Error', msg, QMessageBox.Ok)


# noinspection PyArgumentList
def question(target, title, msg):
	return QMessageBox.information(target, title, msg, QMessageBox.Yes | QMessageBox.Cancel)
