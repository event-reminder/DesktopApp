import platform


class Notification:

	URGENCY_LOW = 'low'
	URGENCY_NORMAL = 'normal'
	URGENCY_CRITICAL = 'critical'

	def __init__(self, title, description, duration=5, urgency=URGENCY_LOW, icon_path=None):
		if urgency not in [self.URGENCY_LOW, self.URGENCY_NORMAL, self.URGENCY_CRITICAL]:
			raise ValueError('invalid urgency was given: {}'.format(urgency))
		self.__WINDOWS = 'Windows'
		self.__LINUX = 'Linux'
		self.__title = title
		self.__description = description
		self.__duration = duration
		self.__urgency = urgency
		self.__icon_path = icon_path
		self.__is_windows = False

	# sends notification depending on system
	def send(self):
		system = platform.system()
		if self.__LINUX in system:
			self.__send_linux()
		elif self.__WINDOWS in system:
			self.__send_windows()
		else:
			raise SystemError('notifications are not supported for {} system'.format(system))

	# sends notification if running on Linux system
	def __send_linux(self):
		import subprocess
		command = [
			'notify-send', '"{}"'.format(self.__title),
			'"{}"'.format(self.__description),
			'-u', self.__urgency,
			'-t', '{}'.format(self.__duration * 1000)
		]
		if self.__icon_path is not None:
			command += ['-i', self.__icon_path]
		subprocess.call(command)

	# sends notification if running on Windows system
	def __send_windows(self):
		try:
			import win10toast
			win10toast.ToastNotifier().show_toast(
				threaded=True,
				title=self.__title,
				msg=self.__description,
				duration=self.__duration,
				icon_path=self.__icon_path
			)
		except ImportError:
			raise ImportError('notifications are not supported, can\'t import necessary library')
