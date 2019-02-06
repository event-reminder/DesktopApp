_HOST = 'localhost'
_PORT = '8000'

_BASE = 'http://{}:{}'.format(_HOST, _PORT)

_API = '{}/api/v1'.format(_BASE)

REGISTER = '{}/accounts'.format(_API)
ACCOUNTS_EDIT = '{}/edit'.format(REGISTER)

LOGIN = '{}/auth/login/'.format(_API)
LOGOUT = '{}/auth/logout/'.format(_API)
USER = '{}/auth/user/'.format(_API)

BACKUPS = '{}/backups'.format(_API)
BACKUPS_GET = '{}/get'.format(BACKUPS)
