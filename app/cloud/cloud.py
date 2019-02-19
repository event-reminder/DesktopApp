import os
import pickle
import requests

from app.cloud import routes, status
from app.settings import APP_DATA_PATH
from app.decorators import failure_wrapper
from app.exceptions import CloudStorageException


class CloudStorage:
	"""
	Cloud storage implements methods to access Event Reminder server-side data.
	"""

	def __init__(self):
		self.session = requests.Session()
		token = self.__retrieve_token()
		if token:
			self.session.headers.update({
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

	def __remove_token(self):
		token_path = '{}/token'.format(APP_DATA_PATH)
		if os.path.exists(token_path):
			os.remove(token_path)
		if 'Authorization' in self.session.headers:
			self.session.headers.pop('Authorization')

	@failure_wrapper(method_desc='Login')
	def login(self, username, password, remember=False):
		login_failed_template = 'Login failed: {}.'
		response = self.session.post(routes.AUTH_LOGIN, json={
			'username': username,
			'password': password
		})
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise CloudStorageException(
				login_failed_template.format('unable to login with provided credentials')
			)
		elif response.status_code != status.HTTP_200_OK:
			raise CloudStorageException(login_failed_template.format(
				'unable to login, status {}'.format(response.status_code))
			)
		token = response.json()['key']
		self.session.headers.update({
			'Authorization': 'Token {}'.format(token)
		})
		if remember:
			with open('{}/token'.format(APP_DATA_PATH), 'wb') as token_file:
				token_file.write(pickle.dumps(token))
		return token

	@failure_wrapper(method_desc='Logout')
	def logout(self):
		response = self.session.post(routes.AUTH_LOGOUT)
		if response.status_code != status.HTTP_200_OK:
			raise CloudStorageException(
				'Logout failure: unable to logout, status {}'.format(response.status_code)
			)
		self.__remove_token()

	@failure_wrapper(method_desc='Registration')
	def register_account(self, username, email):
		registration_failed_template = 'Registration failed: {}.'
		response = self.session.post(routes.ACCOUNT_CREATE, json={
			'username': username,
			'email': email
		})
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			json_response = response.json()
			err_msg = 'credentials error'
			if 'non_field_errors' in json_response:
				if 'username' in json_response['non_field_errors']:
					err_msg = 'username is not provided'
				elif 'email' in json_response['non_field_errors']:
					err_msg = 'email is not provided'
			raise CloudStorageException(registration_failed_template.format(err_msg))
		elif response.status_code != status.HTTP_201_CREATED:
			raise CloudStorageException(registration_failed_template.format(
				'unable to register an account, status'.format(response.status_code))
			)

	@failure_wrapper(method_desc='Reading account')
	def user(self):
		response = self.session.get(routes.ACCOUNT_DETAILS)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise CloudStorageException('Reading account failure: authentication is required.')
		if response.status_code != status.HTTP_200_OK:
			raise CloudStorageException('Reading account failure: unable to retrieve account information.')
		return response.json()

	@failure_wrapper(method_desc='Reading backups')
	def backups(self):
		get_backups_failed_template = 'Reading backups failed: {}.'
		response = self.session.get(routes.BACKUPS)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise CloudStorageException(
				get_backups_failed_template.format('authentication is required')
			)
		elif response.status_code != status.HTTP_200_OK:
			raise CloudStorageException(
				get_backups_failed_template.format('unable to retrieve backups data from the server')
			)
		return response.json()

	@failure_wrapper(method_desc='Backup uploading')
	def upload_backup(self, backup):
		backup_upload_failed_template = 'Backup uploading failed: {}.'
		response = self.session.post(routes.BACKUP_CREATE, data=backup)
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise CloudStorageException(backup_upload_failed_template.format('authentication is required'))
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise CloudStorageException(
				backup_upload_failed_template.format('backup already exists')
			)
		elif response.status_code != status.HTTP_201_CREATED:
			raise CloudStorageException(
				backup_upload_failed_template.format(
					'unable to upload backup, status {}'.format(response.status_code)
				)
			)

	@failure_wrapper(method_desc='Backup downloading')
	def download_backup(self, backup_hash):
		backup_download_failed_template = 'Backup downloading failed: {}.'
		response = self.session.get('{}{}'.format(routes.BACKUP_DETAILS, backup_hash))
		if response.status_code == status.HTTP_401_UNAUTHORIZED:
			raise CloudStorageException(
				backup_download_failed_template.format('authentication is required')
			)
		elif response.status_code != status.HTTP_200_OK:
			raise CloudStorageException(backup_download_failed_template.format(
				'unable to download backup, status {}'.format(response.status_code)
			))
		return response.json()

	@failure_wrapper(method_desc='Backup deleting')
	def delete_backup(self, backup_hash):
		backup_delete_failed_template = 'Backup deleting failed: {}.'
		response = self.session.post('{}{}'.format(routes.BACKUP_DELETE, backup_hash))
		if response.status_code == status.HTTP_400_BAD_REQUEST:
			raise CloudStorageException(
				backup_delete_failed_template.format('authentication is required')
			)
		elif response.status_code != status.HTTP_201_CREATED:
			raise CloudStorageException(
				backup_delete_failed_template.format(
					'unable to delete backup, status {}'.format(response.status_code)
				)
			)
