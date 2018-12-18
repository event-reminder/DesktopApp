import os

import portalocker as locker


class PidFile(object):
	
	def __init__(self, path):
		self.path = path
		self.pidfile = open(self.path, 'a+')
		
	def __enter__(self):
		self.create()

	def create(self):
		try:
			locker.lock(self.pidfile, locker.LOCK_EX | locker.LOCK_NB)
		except IOError:
			raise SystemExit('Already running according to {}'.format(self.path))
		self.pidfile.seek(0)
		self.pidfile.truncate()
		self.pidfile.write(str(os.getpid()))
		self.pidfile.flush()
		self.pidfile.seek(0)
		return self.pidfile
	
	def close(self):
		try:
			self.pidfile.close()
		except IOError as err:
			if err.errno != 9:
				raise

	def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
		self.close()
		os.remove(self.path)


if __name__ == '__main__':
	with PidFile('./t.pid') as pf:
		import time
		time.sleep(60)
