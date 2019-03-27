import os
import logging
from inspect import getframeinfo, stack

from erdesktop.settings import APP_NAME, APP_LOG_FILE, APP_DATA_PATH

if not os.path.exists(APP_DATA_PATH):
	os.makedirs(APP_DATA_PATH)


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(APP_LOG_FILE)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s [%(name)s | %(levelname)s]:\n\t%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def log_msg(message, shift=2):
	caller = getframeinfo(stack()[1][0])
	return '{}:{} - {}\n'.format(caller.filename, caller.lineno - shift, message)
