import time
import logging

from service import Service

from app.settings.app_settings import APP_LOG_PATH


class ReminderService(Service):

	def __init__(self, *args, **kwargs):
		super(ReminderService, self).__init__(*args, **kwargs)

		self.info_logger = logging.getLogger()
		self.info_logger.setLevel(logging.INFO)
		handler = logging.FileHandler('./result_log.txt')
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s: Event - %(message)s')
		handler.setFormatter(formatter)
		self.info_logger.addHandler(handler)

		self.err_logger = logging.getLogger()
		self.err_logger.setLevel(logging.ERROR)
		handler = logging.FileHandler(APP_LOG_PATH)
		handler.setLevel(logging.ERROR)
		handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
		self.err_logger.addHandler(handler)

	def run(self):
		i = 0
		while i < 5 and not self.got_sigterm():
			try:
				i += 1

				# TODO: send notification
				self.info_logger.info('Service info: {}'.format(i))

				time.sleep(5)
			except Exception as exc:
				self.err_logger.error(exc)
