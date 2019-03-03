import platform

from erdesktop.autostart import linux, windows
from erdesktop.util.exceptions import AutoStartIsNotSupportedError

LINUX = 'Linux'
WINDOWS = 'Windows'


def add_to_auto_start():
	system = platform.system()
	if LINUX in system:
		linux.add_to_auto_start()
	elif WINDOWS in system:
		windows.add_to_auto_start()
	else:
		raise AutoStartIsNotSupportedError(system)


def remove_from_auto_start():
	system = platform.system()
	if LINUX in system:
		linux.remove_from_auto_start()
	elif WINDOWS in system:
		windows.remove_from_auto_start()
	else:
		AutoStartIsNotSupportedError(system)
