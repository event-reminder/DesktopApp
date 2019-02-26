import sys
import traceback

from app.settings import DEBUG
from app.util.logger import logger, log_msg

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
		self.err_format = '{}'

	@pyqtSlot()
	def run(self):
		try:
			print(self.fn(*self.args, **self.kwargs))
		except Exception as _:
			if DEBUG:
				traceback.print_exc()
			exc_type, value = sys.exc_info()[:2]
			logger.error(log_msg(self.err_format.format(value)))
			self.signals.error.emit((exc_type, self.err_format.format(value), traceback.format_exc()))
		else:
			self.signals.success.emit()
		finally:
			self.signals.finished.emit()
