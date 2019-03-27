import platform


def name():
	return platform.system()


def is_linux():
	return 'Linux' in name()


def is_windows():
	return 'Windows' in name()
