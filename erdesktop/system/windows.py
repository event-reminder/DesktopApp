import platform

from erdesktop.util.exceptions import AutoStartIsNotSupportedError


def add_to_auto_start():
	raise AutoStartIsNotSupportedError(platform.system())


def remove_from_auto_start():
	raise AutoStartIsNotSupportedError(platform.system())
