from service import Service

import time


class ReminderService(Service):

	def run(self):
		i = 0
		while i < 5:
			print('Hello {}'.format(i))
			i += 1
			time.sleep(5)
