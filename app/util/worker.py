import sys
import traceback

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable


class WorkerSignals(QObject):
	success = pyqtSignal()
	finished = pyqtSignal()
	error = pyqtSignal(tuple)


# noinspection PyArgumentList,PyBroadException
class Worker(QRunnable):

	def __init__(self, fn, *args, **kwargs):
		super(Worker, self).__init__()
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()
		self.success_kwargs = None
		self.finished_kwargs = None

	@pyqtSlot()
	def run(self):
		try:
			self.fn(*self.args, **self.kwargs)
		except Exception as _:
			traceback.print_exc()
			exc_type, value = sys.exc_info()[:2]
			self.signals.error.emit((exc_type, value, traceback.format_exc()))
		else:
			self.signals.success.emit()
		finally:
			self.signals.finished.emit()
