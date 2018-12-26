from threading import Thread, Event


class Timer:

	def __init__(self, timeout, func):
		self.__func = func
		self.__timeout = timeout
		self.__thread = None
		self.__event = None

	def __exec(self):
		self.__event.wait(self.__timeout)
		if not self.__event.is_set():
			self.__func()

	def start(self):
		self.__event = Event()
		self.__thread = Thread(target=self.__exec)
		self.__thread.start()

	def is_active(self):
		return self.__thread.isAlive()

	def stop(self):
		self.__event.set()
		self.wait()

	def wait(self):
		self.__thread.join()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.stop()
