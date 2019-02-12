from PyQt5.QtCore import QRunnable, QMetaObject, Qt, Q_ARG


class BackgroundProcess(QRunnable):
	def __init__(self, cls, target, args=None):
		QRunnable.__init__(self)
		if args is None:
			args = []
		self.target = target
		self.cls = cls
		self.args = args

	def run(self):
		args = [Q_ARG(type(arg), arg) for arg in self.args]
		QMetaObject.invokeMethod(self.cls, self.target.__name__, Qt.QueuedConnection, *args)
