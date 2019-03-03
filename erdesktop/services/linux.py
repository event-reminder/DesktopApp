from erdesktop.settings import (
	ENTRY_POINT, APP_DESCRIPTION, APP_VERSION, APP_NAME, APP_ICON_LIGHT, LINUX_AUTO_START_FILE
)

DESKTOP_ENTRY_SCRIPT = """[Desktop Entry]
Version={}
Name={}
Comment={}
Exec=/usr/bin/python3 {} -- %u
Icon={}
Terminal=false
StartupWMClass={}
Type=Application
Categories=Calendar;Reminder;Events;PyQt5;
""".format(
	APP_VERSION, APP_NAME, APP_DESCRIPTION, ENTRY_POINT, APP_ICON_LIGHT, APP_NAME.replace(' ', '')
)


def setup_service():
	with open(LINUX_AUTO_START_FILE, 'w') as file_write:
		file_write.write(DESKTOP_ENTRY_SCRIPT)
