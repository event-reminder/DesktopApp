from requests import ConnectionError


def connection_failed(func, err_wrapper='Connection failed: {}.'):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except ConnectionError:
			raise ConnectionError(err_wrapper.format('unable to connect to server...'))
	return wrapper
