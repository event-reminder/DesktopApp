_HOST = 'localhost'
_PORT = '8000'

_BASE = 'http://{}:{}'.format(_HOST, _PORT)

_API = '{}/api/v1'.format(_BASE)

REGISTER = '{}/accounts/'.format(_API)
ACCOUNTS_EDIT = '{}/edit'.format(REGISTER)

_AUTH = '{}/auth/'.format(_API)

LOGIN = '{}login/'.format(_AUTH)
LOGOUT = '{}logout/'.format(_AUTH)
USER = '{}user/'.format(_AUTH)

BACKUPS = '{}/backups/'.format(_API)
BACKUPS_CREATE = '{}create'.format(BACKUPS)
BACKUP_DETAILS = '{}details/'.format(BACKUPS)
