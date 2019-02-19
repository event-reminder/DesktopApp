import os
import pickle
import requests

from app.cloud import routes
from app.settings import APP_PATH


class CloudStorage:
	connection_failed_msg = 'can not connect to the server...'

	login_failed_template = 'Login failed: {}'
	logout_failed_template = 'Logout failed: {}'
	registration_failed_template = 'Registration failed: {}'
	get_account_failed_template = 'Reading account failed: {}'
	get_backups_failed_template = 'Reading backups failed: {}'
	backup_upload_failed_template = 'Backup uploading failed: {}'
	backup_download_failed_template = 'Backup downloading failed: {}'
	backup_delete_failed_template = 'Backup deleting failed: {}'

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
			with open('{}token'.format(APP_PATH), 'rb') as token_file:
				token = pickle.loads(token_file.read())
				return token
		except FileNotFoundError:
			pass
		return None

	def __remove_token(self):
		token_path = '{}/token'.format(APP_PATH)
		if os.path.exists(token_path):
			os.remove(token_path)
		if 'Authorization' in self.session.headers:
			self.session.headers.pop('Authorization')

	def login(self, username, password, remember=False):
		try:
			response = self.session.post(routes.AUTH_LOGIN, json={
				'username': username,
				'password': password
			})
			if response.status_code == 400:
				raise Exception(self.login_failed_template.format('unable to login with provided credentials'))
			elif response.status_code != 200:
				raise Exception(self.login_failed_template.format(
					'unable to login, status {}'.format(response.status_code))
				)
			token = response.json()['key']
			self.session.headers.update({
				'Authorization': 'Token {}'.format(token)
			})
			if remember:
				with open('{}/token'.format(APP_PATH), 'wb') as token_file:
					token_file.write(pickle.dumps(token))
			return token
		except requests.ConnectionError:
			raise requests.ConnectionError(self.login_failed_template.format(self.connection_failed_msg))

	def logout(self):
		try:
			response = self.session.post(routes.AUTH_LOGOUT)
			if response.status_code != 200:
				raise Exception(self.logout_failed_template.format(
					'unable to logout, status {}'.format(response.status_code))
				)
			self.__remove_token()
		except requests.ConnectionError:
			raise requests.ConnectionError(self.logout_failed_template.format(self.connection_failed_msg))

	def register_account(self, username, email):
		try:
			response = self.session.post(routes.ACCOUNT_CREATE, json={
				'username': username,
				'email': email
			})
			if response.status_code == 400:
				json_response = response.json()
				err_msg = 'credentials error'
				if 'non_field_errors' in json_response:
					if 'username' in json_response['non_field_errors']:
						err_msg = 'username is not provided'
					elif 'email' in json_response['non_field_errors']:
						err_msg = 'email is not provided'
				raise Exception(self.registration_failed_template.format(err_msg))
			elif response.status_code != 201:
				raise Exception(self.registration_failed_template.format(
					'unable to register an account, status'.format(response.status_code))
				)
		except requests.ConnectionError:
			raise requests.ConnectionError(self.registration_failed_template.format(self.connection_failed_msg))

	def validate_token(self):
		try:
			if not ('Authorization' in self.session.headers and self.session.get(routes.ACCOUNT_DETAILS).status_code == 200):
				self.__remove_token()
				raise requests.RequestException('Authorization is required')
		except requests.ConnectionError:
			raise requests.ConnectionError('Connection error: {}'.format(self.connection_failed_msg))

	def user(self):
		try:
			response = self.session.get(routes.ACCOUNT_DETAILS)
			if response.status_code != 200:
				raise Exception(self.get_account_failed_template.format('unable to retrieve account information'))
			return response.json()
		except requests.ConnectionError:
			raise requests.ConnectionError(self.get_account_failed_template.format(self.connection_failed_msg))

	def backups(self):
		try:
			response = self.session.get(routes.BACKUPS)

			print(response.json())

			if response.status_code == 401:
				raise Exception(self.get_backups_failed_template.format('authentication is required'))
			elif response.status_code != 200:
				raise Exception(self.get_backups_failed_template.format('unable to retrieve backups data from the server'))
			return response.json()
		except requests.ConnectionError:
			raise requests.ConnectionError(self.get_backups_failed_template.format(self.connection_failed_msg))

	def upload_backup(self, backup):
		try:
			response = self.session.post(routes.BACKUP_CREATE, data=backup)
			if response.status_code == 401:
				raise Exception(self.backup_upload_failed_template.format('authentication is required'))
			if response.status_code == 400:
				raise Exception(
					self.backup_upload_failed_template.format('backup already exists')
				)
			elif response.status_code != 201:
				raise Exception(
					self.backup_upload_failed_template.format(
						'unable to upload backup, status {}'.format(response.status_code)
					)
				)
		except requests.ConnectionError:
			raise requests.ConnectionError(self.backup_upload_failed_template.format(self.connection_failed_msg))

	def download_backup(self, backup_hash):
		try:
			response = self.session.get('{}{}'.format(routes.BACKUP_DETAILS, backup_hash))
			if response.status_code == 401:
				raise Exception(self.backup_download_failed_template.format('authentication is required'))
			elif response.status_code != 200:
				raise Exception(self.backup_download_failed_template.format(
					'unable to download backup, status {}'.format(response.status_code)
				))
			return response.json()
		except requests.ConnectionError:
			raise requests.ConnectionError(self.backup_download_failed_template.format(self.connection_failed_msg))

	def delete_backup(self, backup_hash):
		try:
			response = self.session.post('{}{}'.format(routes.BACKUP_DELETE, backup_hash))
			if response.status_code == 400:
				raise Exception(self.backup_delete_failed_template.format('authentication is required'))
			elif response.status_code != 201:
				raise Exception(self.backup_delete_failed_template.format(
					'unable to delete backup, status {}'.format(response.status_code)
				))
		except requests.ConnectionError:
			raise requests.ConnectionError(self.backup_delete_failed_template.format(self.connection_failed_msg))
