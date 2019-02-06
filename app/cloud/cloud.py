import requests

from app.cloud import urls


class CloudStorage:

	def __init__(self, token=None):
		self.session = requests.Session()
		if token:
			self.session.headers.update({
				'Authorization': 'Token {}'.format(token)
			})

	def login(self, username, password):
		response = self.session.post(urls.LOGIN, json={
			'username': username,
			'password': password
		})
		if response.status_code != 200:
			raise Exception('login failed, response status code: {}'.format(response.status_code))
		token = response.json()['key']
		self.session.headers.update({
			'Authorization': 'Token {}'.format(token)
		})
		return token

	def logout(self):
		response = self.session.post(urls.LOGOUT)
		if response.status_code != 200:
			raise Exception('logout failed, response status code: {}'.format(response.status_code))

	def register_account(self, username, email):
		response = self.session.post(urls.REGISTER, json={
			'username': username,
			'email': email
		})
		if response.status_code != 201:
			raise Exception('registration failed, response status code: {}'.format(response.status_code))

	def user(self):
		response = self.session.get(urls.USER)
		if response.status_code != 200:
			raise Exception('retrieving user data failed, response status code: {}'.format(response.status_code))
		return response.json()

	def upload_backup(self, data):
		pass

	def download_backup(self, backup_id):
		pass
