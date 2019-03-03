from app.settings import (
	ENTRY_POINT, APP_DESCRIPTION, APP_VERSION, APP_NAME, APP_ICON_LIGHT
)

DESKTOP_ENTRY = """[Desktop Entry]
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
	with open('/home/yuralisovskiy/.config/autostart/{}.desktop'.format(APP_NAME.replace(' ', '').lower()), 'w') as file_write:
		file_write.write(DESKTOP_ENTRY)
