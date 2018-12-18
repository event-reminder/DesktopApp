#!/usr/bin/env python

# Copyright (c) 2014-2018 Florian Brucker (www.florianbrucker.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import time
import errno
import signal
import logging
import os.path
import threading
import setproctitle

from app.reminder.pidfile import PidFile


__version__ = '0.5.1'

__all__ = ['find_syslog', 'Service']


SERVICE_DEBUG = logging.DEBUG - 1


def _detach_process():
	pid = os.fork()
	if pid > 0:
		os.waitpid(pid, 0)
		return True
	os.setsid()
	pid = os.fork()
	if pid > 0:
		os._exit(0)
	return False


class _PIDFile(object):
	def __init__(self, path):
		self._path = path
		self._lock = None

	def _make_lock(self):
		return PidFile(self._path)

	def acquire(self):
		self._make_lock().create()

	def release(self):
		self._make_lock().close()
		try:
			os.remove(self._path)
		except OSError as e:
			if e.errno != errno.ENOENT:
				raise

	def read_pid(self):
		try:
			with open(self._path, 'r') as f:
				s = f.read().strip()
				if not s:
					return None
				return int(s)
		except IOError as e:
			if e.errno == errno.ENOENT:
				return None
			raise


def find_syslog():
	for path in ['/dev/log', '/var/run/syslog']:
		if os.path.exists(path):
			return path
	return '127.0.0.1', 514


def _block(predicate, timeout):
	if timeout:
		if timeout is True:
			timeout = float('Inf')
		timeout = time.time() + timeout
		while not predicate() and time.time() < timeout:
			time.sleep(0.1)
	return predicate()


class Service(object):
	
	def __init__(self, name, pid_dir='/var/run'):
		self.name = name
		self.pid_file = _PIDFile(os.path.join(pid_dir, name + '.pid'))
		self._got_sigterm = threading.Event()
		self.logger = logging.getLogger(name)
		if not self.logger.handlers:
			self.logger.addHandler(logging.NullHandler())
		self.files_preserve = []

	def _debug(self, msg):
		self.logger.log(SERVICE_DEBUG, msg)

	def _get_logger_file_handles(self):
		handles = []
		for handler in self.logger.handlers:
			for attr in ['sock', 'socket', 'stream']:
				try:
					handle = getattr(handler, attr)
					if handle:
						handles.append(handle)
					break
				except AttributeError:
					continue
		return handles

	def is_running(self):
		pid = self.get_pid()
		if pid is None:
			return False
		try:
			os.kill(pid, 0)
		except OSError as e:
			if e.errno == errno.ESRCH:
				self.pid_file.release()
				return False
		return True

	def get_pid(self):
		return self.pid_file.read_pid()

	def got_sigterm(self):
		return self._got_sigterm.is_set()

	def wait_for_sigterm(self, timeout=None):
		return self._got_sigterm.wait(timeout)

	def stop(self, block=False):
		pid = self.get_pid()
		if not pid:
			raise ValueError('Daemon is not running.')
		os.kill(pid, signal.SIGTERM)
		return _block(lambda: not self.is_running(), block)

	def kill(self, block=False):
		pid = self.get_pid()
		if not pid:
			raise ValueError('Daemon is not running.')
		try:
			os.kill(pid, signal.SIGKILL)
			return _block(lambda: not self.is_running(), block)
		except OSError as e:
			if e.errno == errno.ESRCH:
				raise ValueError('Daemon is not running.')
			raise
		finally:
			self.pid_file.release()

	def start(self, block=False):
		pid = self.get_pid()
		if pid:
			raise ValueError('Daemon is already running at PID %d.' % pid)
		try:
			self.pid_file.acquire()
		finally:
			self.pid_file.release()
		self._got_sigterm.clear()
		if _detach_process():
			return _block(lambda: self.is_running(), block)
		self._debug('Daemon has detached')
	
		def on_sigterm(signum, frame):
			self._debug('Received SIGTERM signal')
			self._got_sigterm.set()

		def runner():
			try:
				self.pid_file.acquire()
				self._debug('PID file has been acquired')
				self._debug('Calling `run`')
				self.run()
				self._debug('`run` returned without exception')
			except Exception as e:
				self.logger.exception(e)
			except SystemExit:
				self._debug('`run` called `sys.exit`')
			try:
				self.pid_file.release()
				self._debug('PID file has been released')
			except Exception as e:
				self.logger.exception(e)
			os._exit(0)  # FIXME: This seems redundant

		try:
			setproctitle.setproctitle(self.name)
			self._debug('Process title has been set')
			self._debug('Daemon context has been established')

			thread = threading.Thread(target=runner)
			thread.start()
			while thread.is_alive():
				time.sleep(1)
		except Exception as e:
			self.logger.exception(e)

		os._exit(0)

	def run(self):
		pass
