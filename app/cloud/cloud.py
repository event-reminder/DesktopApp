import os
import pickle
import requests

from app.cloud import routes
from app.settings import APP_PATH


class CloudStorage:

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
		response = self.session.post(routes.LOGIN, json={
			'username': username,
			'password': password
		})
		if response.status_code != 200:
			raise Exception('login failed, response status code: {}'.format(response.status_code))
		token = response.json()['key']
		self.session.headers.update({
			'Authorization': 'Token {}'.format(token)
		})
		if remember:
			with open('{}/token'.format(APP_PATH), 'wb') as token_file:
				token_file.write(pickle.dumps(token))
		return token

	def logout(self):
		response = self.session.post(routes.LOGOUT)
		if response.status_code != 200:
			raise Exception('logout failed, response status code: {}'.format(response.status_code))
		self.__remove_token()

	def register_account(self, username, email):
		response = self.session.post(routes.REGISTER, json={
			'username': username,
			'email': email
		})
		if response.status_code != 201:
			json_response = response.json()
			err_msg = ''
			if 'non_field_errors' in json_response:
				errors = response.json()['non_field_errors'] or response.json()
				for err in errors:
					err_msg += '  {}\n'.format(err)
			elif 'detail' in json_response:
				err_msg = json_response['detail']
			else:
				err_msg = json_response
			print(json_response)
			raise Exception('registration failed:\n{}'.format(err_msg))

	def validate_token(self):
		result = 'Authorization' in self.session.headers and self.session.get(routes.USER).status_code == 200
		if result is False:
			self.__remove_token()
			raise requests.exceptions.RequestException('Authorization is required')

	def user(self):
		response = self.session.get(routes.USER)
		if response.status_code != 200:
			raise Exception('retrieving user data failed, response status code: {}'.format(response.json()))
		return response.json()

	def backups(self):
		response = self.session.get(routes.BACKUPS)
		if response.status_code != 200:
			raise Exception('retrieving backups failed, response status code: {}'.format(response.status_code))
		return response.json()

	def upload_backup(self, backup):
		response = self.session.post(routes.BACKUPS_CREATE, data=backup)
		code = response.status_code
		if code != 201:
			if code == 400:
				raise Exception('Upload was rejected: this backup already exists.')
			raise Exception('uploading failed, response status code: {}'.format(response.status_code))

	def download_backup(self, backup_hash):
		response = self.session.get('{}{}'.format(routes.BACKUP_DETAILS, backup_hash))
		if response.status_code != 200:
			raise Exception('downloading failed, response status code: {}'.format(response.status_code))
		return response.json()

	def delete_backup(self, backup_hash):
		response = self.session.post('{}{}'.format(routes.BACKUP_DETAILS, backup_hash))
		if response.status_code != 201:
			raise Exception('deleting failed, response status code: {}'.format(response.status_code))
