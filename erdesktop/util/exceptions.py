
class CloudStorageException(Exception):
	"""Cloud storage error occurred"""


class LoginFailedError(CloudStorageException):
	"""Unable to login exception"""


class LoginFailedCredentialsError(LoginFailedError):
	"""Unable to log in with provided credentials exception"""


class LogoutFailedError(CloudStorageException):
	"""Unable to log out"""


class RegisterFailedError(CloudStorageException):
	"""Unable to register an account"""


class RegisterFailedUsernameIsNotProvidedError(RegisterFailedError):
	"""Unable to register an account because of username was not provided in parameters"""


class RegisterFailedEmailIsNotProvidedError(RegisterFailedError):
	"""Unable to register an account because of email was not provided in parameters"""


class RegisterFailedUserAlreadyExistsError(RegisterFailedError):
	"""Unable to register an account because of user already exists"""


class AuthRequiredError(CloudStorageException):
	"""Authentication required exception"""


class UserRetrievingError(CloudStorageException):
	"""Unable to get user information exception"""


class UserUpdatingError(CloudStorageException):
	"""Unable to update user exception"""


class RequestTokenError(CloudStorageException):
	"""Unable to send token request exception"""


class ResetPasswordError(CloudStorageException):
	"""Unable to reset user password exception"""


class ReadingBackupsError(CloudStorageException):
	"""Unable to retrieve backups exception"""


class BackupAlreadyExistsError(CloudStorageException):
	"""Backups already exists on server"""


class BackupUploadingError(CloudStorageException):
	"""Unable to upload backup to server exception"""


class BackupDownloadingError(CloudStorageException):
	"""Unable to download backup to server exception"""


class BackupDeletingError(CloudStorageException):
	"""Unable to delete backup to server exception"""


class DatabaseException(Exception):
	"""Error occurred during accessing the database"""


class AutoStartIsNotSupportedError(Exception):
	"""Unable to perform any operation with application's auto start"""


class ShortcutIconIsNotSupportedError(Exception):
	"""Unable to create shortcut icon in current system"""
