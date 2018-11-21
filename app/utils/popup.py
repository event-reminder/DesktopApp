from PyQt5.QtWidgets import *


def warning(target, msg):
	return QMessageBox.warning(target, 'Warning', msg, QMessageBox.Ok)


def info(target, msg):
	return QMessageBox.information(target, 'Info', msg, QMessageBox.Ok)


def fatal(target, msg):
	return QMessageBox.information(target, 'Fatal', msg, QMessageBox.Ok)


def question(target, title, msg):
	return QMessageBox.information(target, title, msg, QMessageBox.Yes | QMessageBox.Cancel)
