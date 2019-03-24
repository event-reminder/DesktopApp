import os
import sys
import platform
from win32com.client import Dispatch

from erdesktop import APP_NAME
from erdesktop.settings.default import abs_path
from erdesktop.settings import APP_ICON_DEFAULT_ICO
from erdesktop.util.exceptions import AutoStartIsNotSupportedError


def add_to_auto_start():
	raise AutoStartIsNotSupportedError(platform.system())


def remove_from_auto_start():
	raise AutoStartIsNotSupportedError(platform.system())


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
