import functools

from erdesktop.settings import DEBUG

from requests.exceptions import ConnectionError, RequestException


def failure_wrapper(_func=None, *, method_desc=None):
	"""
	Wraps function which takes a request and simplifies request error message.

	:parameter method_desc - method description which will be raised if an error is generated
	:parameter _func - function to wrap

	ConnectionError -> 'Connection failure: unable to connect to server'
	RequestError -> 'Request failure: unable to retrieve data from server'
	"""

	_err_template = '{} failed: {}'

	def decorator(func):

		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except ConnectionError as exc:
				desc = method_desc if method_desc is not None else 'Connection'
				raise ConnectionError(
					_err_template.format(desc, exc) if DEBUG else _err_template.format(
						desc, 'unable to connect to server'
					)
				)
			except RequestException as exc:
				desc = method_desc if method_desc is not None else 'Request'
				raise RequestException(
					_err_template.format(desc, exc) if DEBUG else _err_template.format(
						desc, 'unable to retrieve data from server'
					)
				)
		return wrapper

	if _func is None:
		return decorator
	return decorator(_func)
