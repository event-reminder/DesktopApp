import os
import sys

from erdesktop.settings.default import abs_path
from erdesktop import APP_DESCRIPTION, APP_VERSION, APP_NAME
from erdesktop.settings import APP_ICON_LIGHT, LINUX_AUTO_START_FILE

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
	APP_ICON_LIGHT,
	APP_NAME.replace(' ', '')
)


def add_to_auto_start():
	with open(LINUX_AUTO_START_FILE, 'w') as file_write:
		file_write.write(DESKTOP_ENTRY_SCRIPT)


def remove_from_auto_start():
	if os.path.isfile(LINUX_AUTO_START_FILE):
		os.remove(LINUX_AUTO_START_FILE)
