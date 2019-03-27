from erdesktop.system import system, linux, windows
from erdesktop.util.exceptions import ShortcutIconIsNotSupportedError


def create():
	if system.is_linux():
		linux.create_shortcut()
	elif system.is_windows():
		windows.create_shortcut()
	else:
		raise ShortcutIconIsNotSupportedError(system.name())
