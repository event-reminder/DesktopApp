import sys
import traceback

from erdesktop.settings import DEBUG
from erdesktop.util.logger import logger, log_msg

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable


class WorkerSignals(QObject):
	success = pyqtSignal()
	param_success = pyqtSignal(object)
	finished = pyqtSignal()
	error = pyqtSignal(tuple)


class Worker(QRunnable):

	def __init__(self, fn, *args, **kwargs):
		super(Worker, self).__init__()
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()
		self.err_format = '{}'

	# noinspection PyArgumentList
	@pyqtSlot()
	def run(self):

		# noinspection PyBroadException
		try:
			result = self.fn(*self.args, **self.kwargs)
		except Exception:
			if DEBUG:
				traceback.print_exc()
			exc_type, value = sys.exc_info()[:2]
			logger.error(log_msg(self.err_format.format(value)))
			self.signals.error.emit((exc_type, self.err_format.format(value), traceback.format_exc()))
		else:
			self.signals.success.emit()
			self.signals.param_success.emit(result)
		finally:
			self.signals.finished.emit()
