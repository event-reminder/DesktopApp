import time

from service import Service


class ReminderService(Service):

	def run(self):
		try:
			i = 0
			while i < 5 and not self.got_sigterm():
				try:
					i += 1

					# TODO: send notification

					with open('./file.txt', 'a') as the_file:
						the_file.write('Service info: {}\n'.format(i))

					time.sleep(5)
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./errors_file.txt', 'a') as the_file:
				the_file.write('Service error: {}\n'.format(exc))
