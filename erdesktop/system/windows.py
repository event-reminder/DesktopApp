try:
	import os
	import sys
	import winshell

	from erdesktop import APP_NAME
	from erdesktop.settings.default import abs_path
	from erdesktop.settings import APP_ICON_DEFAULT_ICO

	AUTO_START_ICON_PATH = '{}/{}.lnk'.format(winshell.startup(), APP_NAME)

	def add_to_auto_start():
		_create_shortcut_icon(AUTO_START_ICON_PATH)


	def remove_from_auto_start():
		if os.path.exists(AUTO_START_ICON_PATH):
			os.remove(AUTO_START_ICON_PATH)


	def create_shortcut():
		_create_shortcut_icon('{}/{}.lnk'.format(winshell.desktop(), APP_NAME))

	def _create_shortcut_icon(path):
		winshell.CreateShortcut(
			Path=path,
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
