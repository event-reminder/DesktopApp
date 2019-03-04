import platform


def is_linux():
	return 'Linux' in platform.system()


def is_windows():
	return 'Windows' in platform.system()


def get():
	return platform.system()
