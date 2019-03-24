import os
import sys

from erdesktop.settings.default import abs_path
from erdesktop import APP_DESCRIPTION, APP_VERSION, APP_NAME
from erdesktop.settings import APP_ICON_DEFAULT, LINUX_AUTO_START_FILE, LINUX_DESKTOP_ENTRY_FILE

DESKTOP_ENTRY_SCRIPT = """[Desktop Entry]
Version={}
Name={}
Comment={}
Exec={}
Icon={}
Terminal=false
StartupWMClass={}
Type=Application
Categories=Calendar;Reminder;Events;PyQt5;
""".format(
	APP_VERSION,
	APP_NAME,
	APP_DESCRIPTION,
	'{} {}'.format(sys.executable, abs_path('app_main.py')),
	APP_ICON_DEFAULT,
	APP_NAME.replace(' ', '')
)


def _write_desktop_entry_script(path):
	with open(path, 'w') as file_write:
		file_write.write(DESKTOP_ENTRY_SCRIPT)


def add_to_auto_start():
	_write_desktop_entry_script(LINUX_AUTO_START_FILE)


def remove_from_auto_start():
	if os.path.isfile(LINUX_AUTO_START_FILE):
		os.remove(LINUX_AUTO_START_FILE)


def create_shortcut():
	_write_desktop_entry_script(LINUX_DESKTOP_ENTRY_FILE)
