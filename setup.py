#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import setup, find_packages

from erdesktop.settings.default import (
	APP_VERSION,
	PY_PACKAGE_NAME,
	APP_DESCRIPTION
)

URL = 'https://github.com/YuriyLisovskiy/EventReminder'
EMAIL = 'yuralisovskiy98@gmail.com'
AUTHOR = 'Yuriy Lisovskiy'
REQUIRES_PYTHON = '>=3.6.0'

REQUIRED = open('requirements.txt', 'r').read().split('\n')

try:
	with io.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')) as f:
		long_description = '\n' + f.read()
except FileNotFoundError:
	long_description = APP_DESCRIPTION

setup(
	name=PY_PACKAGE_NAME,
	version=APP_VERSION,
	description=APP_DESCRIPTION,
	entry_points={
		'console_scripts': ['{} = {}.{}:main'.format(
			PY_PACKAGE_NAME, PY_PACKAGE_NAME, 'app_main'
		)]
	},
	long_description=long_description,
	long_description_content_type='text/markdown',
	author=AUTHOR,
	author_email=EMAIL,
	python_requires=REQUIRES_PYTHON,
	url=URL,
	packages=find_packages(exclude=('tests',)),
	install_requires=REQUIRED,
	include_package_data=True,
	license='GPLv3',
	classifiers=[
		# Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3.6',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft :: Windows'
	]
)
