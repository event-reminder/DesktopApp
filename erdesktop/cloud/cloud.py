import os
import pickle
import requests

from erdesktop.cloud import routes
from erdesktop.cloud import status
from erdesktop.settings import APP_DATA_PATH
from erdesktop.util import exceptions as exc
from erdesktop.util.decorators import failure_wrapper


class CloudStorage:
	"""
	Cloud storage implements methods to access Event Reminder server-side data.
	"""

	def __init__(self):
		self.client = requests.Session()
		token = self.__retrieve_token()
		if token:
			self.client.headers.update({
				'Authorization': 'Token {}'.format(token)
			})

	@staticmethod
	def __retrieve_token():
		try:
			with open('{}token'.format(APP_DATA_PATH), 'rb') as token_file:
				token = pickle.loads(token_file.read())
				return token
		except FileNotFoundError:
			pass
		return None

	def remove_token(self):
		token_path = '{}/token'.format(APP_DATA_PATH)
		if os.path.exists(token_path):
			os.remove(token_path)
		if 'Authorization' in self.client.headers:
			self.client.headers.pop('Authorization')

	@failure_wrapper(method_desc='Login')
	def login(self, username, password, remember=False):
		response = self.client.post(routes.AUTH_LOGIN, json={
			'username': username,
			'password': password
		})
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise exc.LoginFailedCredentialsError()
		elif response.status_code != status.HTTP_200_OK:
			raise exc.LoginFailedError(str(response.status_code))
		token = response.json()['key']
		self.client.headers.update({
			'Authorization': 'Token {}'.format(token)
		})
		if remember:
			with open('{}/token'.format(APP_DATA_PATH), 'wb') as token_file:
				token_file.write(pickle.dumps(token))
		return token

	@failure_wrapper(method_desc='Logout')
	def logout(self):
		response = self.client.post(routes.AUTH_LOGOUT)
		if response.status_code != status.HTTP_200_OK:
			raise exc.LogoutFailedError(response.status_code)
		self.remove_token()

	@failure_wrapper(method_desc='Registration')
	def register_account(self, username, email):
		if 'Authorization' in self.client.headers:
			token = self.client.headers.pop('Authorization')
		else:
			token = None
		response = self.client.post(routes.ACCOUNT_CREATE, json={
			'username': username,
			'email': email
		})
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			json_response = response.json()
			if 'non_field_errors' in json_response:
				if 'username' in json_response['non_field_errors']:
					raise exc.RegisterFailedUsernameIsNotProvidedError()
				elif 'email' in json_response['non_field_errors']:
					raise exc.RegisterFailedEmailIsNotProvidedError()
			raise exc.RegisterFailedUserAlreadyExistsError(response.status_code)
		elif response.status_code != status.HTTP_201_CREATED:
			raise exc.RegisterFailedError(response.status_code)
		if token is not None:
			self.client.headers.update({
				'Authorization': token
			})

	@failure_wrapper(method_desc='Reading account')
	def user(self):
		response = self.client.get(routes.ACCOUNT_DETAILS)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise exc.AuthRequiredError()
		if response.status_code != status.HTTP_200_OK:
			raise exc.UserRetrievingError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Updating account')
	def update_user(self, max_backups=None):
		context = {}
		if max_backups is not None:
			context['max_backups'] = max_backups
		response = self.client.post(routes.ACCOUNT_EDIT, json=context)
		if response.status_code != status.HTTP_201_CREATED:
			raise exc.UserUpdatingError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Token request')
	def request_token(self, email):
		response = self.client.post(routes.ACCOUNT_SEND_TOKEN, json={'email': email})
		if response.status_code != status.HTTP_201_CREATED:
			raise exc.RequestTokenError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Password reset')
	def reset_password(self, email, new_password, new_password_confirm, confirmation_code):
		response = self.client.post(routes.ACCOUNT_PASSWORD_RESET, json={
			'email': email,
			'new_password': new_password,
			'new_password_confirm': new_password_confirm,
			'confirmation_code': confirmation_code
		})
		if response.status_code != status.HTTP_201_CREATED:
			raise exc.ResetPasswordError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Reading backups')
	def backups(self):
		response = self.client.get(routes.BACKUPS)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise exc.AuthRequiredError()
		elif response.status_code != status.HTTP_200_OK:
			raise exc.ReadingBackupsError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Backup uploading')
	def upload_backup(self, backup):
		response = self.client.post(routes.BACKUP_CREATE, data=backup)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise exc.AuthRequiredError()
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise exc.BackupAlreadyExistsError()
		elif response.status_code != status.HTTP_201_CREATED:
			raise exc.BackupUploadingError(response.status_code)

	@failure_wrapper(method_desc='Backup downloading')
	def download_backup(self, backup_hash):
		response = self.client.get('{}{}'.format(routes.BACKUP_DETAILS, backup_hash))
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise exc.AuthRequiredError()
		elif response.status_code != status.HTTP_200_OK:
			raise exc.BackupDownloadingError(response.status_code)
		return response.json()

	@failure_wrapper(method_desc='Backup deleting')
	def delete_backup(self, backup_hash):
		response = self.client.post('{}{}'.format(routes.BACKUP_DELETE, backup_hash))
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise exc.AuthRequiredError()
		elif response.status_code != status.HTTP_201_CREATED:
			raise exc.BackupDeletingError(response.status_code)
