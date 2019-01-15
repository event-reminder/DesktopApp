from app.settings import AppSettings, UserSettings


class Settings:

	def __init__(self):
		self.app = AppSettings()
		self.user = UserSettings()
