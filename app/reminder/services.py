import time

from service import Service

import logging


class ReminderService(Service):

	def run(self):
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)

		# create a file handler
		handler = logging.FileHandler('./log.txt')
		handler.setLevel(logging.INFO)

		# create a logging format
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)

		# add the handlers to the logger
		logger.addHandler(handler)

		i = 0
		while i < 5:
			i += 1

			# TODO: send notification
			logger.info('Service info: {}'.format(i))

			time.sleep(2)
