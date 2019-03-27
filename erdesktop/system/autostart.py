from erdesktop.system import system, windows, linux
from erdesktop.util.exceptions import AutoStartIsNotSupportedError


def _run(_linux, _windows):
	if system.is_linux():
		_linux()
	elif system.is_windows():
		_windows()
	else:
		raise AutoStartIsNotSupportedError(system.name())


def add():
	_run(linux.add_to_auto_start, windows.add_to_auto_start)


def remove():
	_run(linux.remove_from_auto_start, windows.remove_from_auto_start)
