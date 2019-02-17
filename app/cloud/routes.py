_HOST = 'localhost'
_PORT = '8000'

_BASE = 'http://{}:{}'.format(_HOST, _PORT)

_API = '{}/api/v1'.format(_BASE)

_AUTH = '{}/auth/'.format(_API)

AUTH_LOGIN = '{}login/'.format(_AUTH)
AUTH_LOGOUT = '{}logout/'.format(_AUTH)

_ACCOUNTS = '{}/accounts'.format(_API)

ACCOUNT_EDIT = '{}/edit'.format(_ACCOUNTS)
ACCOUNT_DETAILS = '{}/user'.format(_ACCOUNTS)
ACCOUNT_CREATE = '{}/create'.format(_ACCOUNTS)
ACCOUNT_DELETE = '{}/delete'.format(_ACCOUNTS)
ACCOUNT_SEND_TOKEN = '{}/send/token'.format(_ACCOUNTS)
ACCOUNT_PASSWORD_RESET = '{}/password/reset'.format(_ACCOUNTS)

BACKUPS = '{}/backups/'.format(_API)
BACKUP_CREATE = '{}create'.format(BACKUPS)
BACKUP_DELETE = '{}delete/'.format(BACKUPS)
BACKUP_DETAILS = '{}details/'.format(BACKUPS)
