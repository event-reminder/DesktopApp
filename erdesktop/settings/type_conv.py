
def int_(_bool):
	assert isinstance(_bool, bool)
	return 1 if _bool is True else 0


def bool_(_int):
	assert isinstance(_int, int)
	return _int != 0


def str_(_bool):
	assert isinstance(_bool, bool)
	return 'true' if _bool is True else 'false'


def s_bool_(_bool_str):
	assert isinstance(_bool_str, str)
	return _bool_str.lower() == 'true'
