try:
	import os
	import sys

	# noinspection PyUnresolvedReferences
	from win32com.client import Dispatch

	from erdesktop import APP_NAME
	from erdesktop.settings.default import abs_path
	from erdesktop.settings import APP_ICON_DEFAULT_ICO, WINDOWS_AUTO_START_FILE


	def add_to_auto_start():
		with open(WINDOWS_AUTO_START_FILE, 'w') as bat_file:
			bat_file.write('{} {}'.format(sys.executable, abs_path('app_main.py')))


	def remove_from_auto_start():
		if os.path.exists(WINDOWS_AUTO_START_FILE):
			os.remove(WINDOWS_AUTO_START_FILE)


	def create_shortcut():
		shell = Dispatch('WScript.Shell')
		shortcut = shell.CreateShortCut(
			'{}/{}.lnk'.format(os.path.normpath(os.path.expanduser('~/Desktop')), APP_NAME)
		)
		shortcut.Targetpath = '{}'.format(sys.executable)
		shortcut.Arguments = '{}'.format(abs_path('app_main.py'))
		shortcut.WorkingDirectory = abs_path('')
		shortcut.IconLocation = APP_ICON_DEFAULT_ICO
		shortcut.save()
except ImportError as exc:
	def add_to_auto_start():
		pass


	def remove_from_auto_start():
		pass


	def create_shortcut():
		pass
