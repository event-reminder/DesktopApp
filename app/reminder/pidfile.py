# {{{ http://code.activestate.com/recipes/577911/ (r2)
import os

import portalocker as locker


class PidFile(object):
	"""Context manager that locks a pid file.  Implemented as class
	not generator because daemon.py is calling .__exit__() with no parameters
	instead of the None, None, None specified by PEP-343."""
	# pylint: disable=R0903

	def __init__(self, path):
		self.path = path
		self.pidfile = open(self.path, 'a+')

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
			# ok if file was just closed elsewhere
			if err.errno != 9:
				raise

	def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
		self.close()
		os.remove(self.path)


if __name__ == '__main__':
	with PidFile('./t.pid') as pf:
		import time
		time.sleep(60)
