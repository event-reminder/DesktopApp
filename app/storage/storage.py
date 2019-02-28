import os
import json
import pickle
import base64
from hashlib import sha512
from datetime import datetime

from app.settings import Settings
from app.storage.models import EventModel
from app.util.exceptions import DatabaseException
from app.storage.instance import DATABASE_INSTANCE
from app.settings.default import APP_DB_PATH, BACKUP_FILE_NAME


class Storage:
	"""
	Implements methods for accessing events from the database.

	Backup:
		Prepare data
			Backup is represented in json (python dictionary) format. 'Data' contains
			a list of events took from the database, settings if it is included in
			backup and username of its author if backup is preparing for uploading to
			cloud. It is serialized to a binary string. 'Digest' is sha512 sum of
			serialized 'data'. 'Timestamp' is date and time when backups is created.
			'Backup' is serialized 'data' which is encoded using base64 algorithm.

		Save to file
			Prepared data is beeing serialized to a binary string and saved to a file.

	Restore:
		Read:
			Program reads file with backup data and deserializes it from binary string.

		Restore data
			Algorithm checks if all required keys are in dictionary object. If this operation
			is succeeded it checks if date and time of backup is valid, i.e. takes current
			date and time and checks if it is greater than backup's one. Than program decodes
			'backup' using base64 decoding, takes its sha512 sum and compares it with written
			in backup data. After success algorithm deserializes 'backup', restores database
			and settings if the last one is included in backup.
	"""

	def __init__(self, try_to_reconnect=False):
		if not os.path.exists(APP_DB_PATH):
			os.makedirs(APP_DB_PATH)

		self.__instance = DATABASE_INSTANCE

		if len(self.__instance.get_tables()) < 1:
			self.__instance.create_tables([EventModel])

		self.try_to_reconnect = try_to_reconnect

		self.connect()

	@property
	def is_connected(self):
		return self.__instance.is_closed() is False

	def connect(self):
		if not self.is_connected:
			self.__instance.connect()
		return self.is_connected

	def disconnect(self):
		if self.is_connected:
			self.__instance.close()
		return not self.is_connected

	def event_exists(self, pk):
		return self.get_event_by_id(pk) is not None

	def create_event(self, title, e_date, e_time, description, repeat_weekly, is_past=False):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Creation failure: connect to the database first.')
		EventModel.create(**{
			'title': title,
			'time': e_time,
			'date': e_date,
			'description': description,
			'repeat_weekly': repeat_weekly,
			'is_past': is_past
		}).save()

	def update_event(self, pk, title=None, e_date=None, e_time=None, description=None, is_past=None, repeat_weekly=None):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Updating failure: connect to the database first.')
		event = self.get_event_by_id(pk)
		if event:
			if title:
				event.title = title
			if e_time:
				event.time = e_time
			if e_date:
				event.date = e_date
			if description:
				event.description = description
			if is_past:
				event.is_past = is_past
			if repeat_weekly:
				event.repeat_weekly = repeat_weekly
			event.save()
		return event

	def delete_event(self, pk):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Deleting failure: connect to the database first.')
		event = self.get_event_by_id(pk)
		if event:
			event.delete_instance(recursive=True)

	def get_events(self, e_date=None, e_time=None):
		if not self.is_connected:
			raise DatabaseException('Retrieving failure: connect to the database first.')
		if e_date is not None and e_time is not None:
			result = EventModel.select().where((EventModel.time == e_time) & (EventModel.date == e_date))
		elif e_date is not None:
			result = EventModel.select().where(EventModel.date == e_date)
		elif e_time is not None:
			result = EventModel.select().where(EventModel.time == e_time)
		else:
			result = EventModel.select()
		return [item for item in result]

	def to_array(self):
		self.connect()
		events = self.get_events()
		return [x.to_dict() for x in events]

	@staticmethod
	def get_event_by_id(pk):
		return EventModel.get_by_id(pk)

	@staticmethod
	def from_array(arr):
		for item in arr:
			EventModel.from_dict(item)

	@staticmethod
	def prepare_backup_data(db, timestamp, include_settings, username=None):
		data = {
			'db': db
		}
		if include_settings:
			data['settings'] = Settings().to_dict()
		if username is not None:
			data['username'] = username
		data = pickle.dumps(json.dumps(data))
		return {
			'digest': sha512(data).hexdigest(),
			'timestamp': timestamp,
			'backup': base64.b64encode(data)
		}

	def restore_from_dict(self, data):
		err_template = 'Restore failure: {}.'
		for key in ['digest', 'timestamp', 'backup']:
			if key not in data:
				raise DatabaseException(err_template.format('invalid backup file'))
		if datetime.now() < datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'):
			raise DatabaseException(err_template.format('incorrect timestamp'))
		backup_decoded = base64.b64decode(data['backup'])
		if sha512(backup_decoded).hexdigest() != data['digest']:
			raise DatabaseException(err_template.format('backup is broken'))
		backup = json.loads(pickle.loads(backup_decoded))
		if 'db' not in backup:
			raise DatabaseException(err_template.format('invalid backup data'))
		EventModel.delete().execute()
		self.from_array(backup['db'])
		if 'settings' in backup:
			Settings().from_dict(backup['settings'])

	def backup(self, path: str, include_settings):
		timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		with open('{}/{} {}.bak'.format(path.rstrip('/'), BACKUP_FILE_NAME, timestamp), 'wb') as file:
			file.write(pickle.dumps(self.prepare_backup_data(self.to_array(), timestamp, include_settings)))

	def restore(self, file_path: str):
		with open(file_path, 'rb') as file:
			self.restore_from_dict(pickle.loads(file.read()))
