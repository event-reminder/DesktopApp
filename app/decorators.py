import functools

from requests.exceptions import ConnectionError, RequestException

from app.settings import DEBUG


def request_failure(_func=None, *, method_desc=None):
	err_template = '{} failed: {}.'

	def decorator(func):

		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except ConnectionError as exc:
				if method_desc is not None:
					desc = method_desc
				else:
					desc = 'Connection'
				if DEBUG:
					raise ConnectionError(err_template.format(desc, exc))
				else:
					raise ConnectionError(err_template.format(desc, 'unable to connect to server'))
			except RequestException as exc:
				if method_desc is not None:
					desc = method_desc
				else:
					desc = 'Request'
				if DEBUG:
					raise ConnectionError(err_template.format(desc, exc))
				else:
					raise RequestException(err_template.format(desc, 'unable to connect to server'))
		return wrapper

	if _func is None:
		return decorator
	return decorator(_func)
