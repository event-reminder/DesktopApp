try:
	import os
	import sys
	import winshell

	from erdesktop import APP_NAME
	from erdesktop.settings.default import abs_path
	from erdesktop.settings import APP_ICON_DEFAULT_ICO

	WINDOWS_AUTO_START_FILE = '{}\\{}'.format(winshell.startup(), '{}.bat'.format(APP_NAME.replace(' ', '').lower()))

	def add_to_auto_start():
		print(WINDOWS_AUTO_START_FILE)

		with open(WINDOWS_AUTO_START_FILE, 'w') as bat_file:
			bat_file.write('{} {}'.format(sys.executable, abs_path('app_main.py')))


	def remove_from_auto_start():
		if os.path.exists(WINDOWS_AUTO_START_FILE):
			os.remove(WINDOWS_AUTO_START_FILE)


	def create_shortcut():
		print(winshell.desktop())

		winshell.CreateShortcut(
			Path='{}/{}.lnk'.format(winshell.desktop(), APP_NAME),
			Target='{}'.format(sys.executable),
			Arguments='{}'.format(abs_path('app_main.py')),
			Icon=(APP_ICON_DEFAULT_ICO, 0),
			Description=APP_NAME
		)

except ImportError as exc:
	def add_to_auto_start():
		pass


	def remove_from_auto_start():
		pass


	def create_shortcut():
		pass
