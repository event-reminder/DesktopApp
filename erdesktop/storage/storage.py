import os
import json
import pickle
import base64
import sqlite3

from hashlib import sha512
from datetime import datetime

from erdesktop.storage.sql import *
from erdesktop.settings import Settings, APP_DB_FILE, APP_DB_PATH
from erdesktop.storage.models import EventModel
from erdesktop.settings import BACKUP_FILE_NAME
from erdesktop.util.exceptions import DatabaseException


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

	def __init__(self, db_path=APP_DB_PATH, db_file=APP_DB_FILE, try_to_reconnect=False, backup_file=BACKUP_FILE_NAME):
		if not os.path.exists(db_path):
			os.makedirs(db_path)

		self.__db = None
		self.__cursor = None
		self.__db_file = db_file
		self.__backup_file_name = backup_file
		self.try_to_reconnect = try_to_reconnect
		self.is_connected = False

		self.connect()

	def connect(self):
		self.__db = sqlite3.connect(self.__db_file, check_same_thread=False)
		self.__cursor = self.__db.cursor()
		EventModel.create_table(self.__cursor)
		self.is_connected = True

	def disconnect(self):
		self.__cursor.close()
		self.__db.close()
		self.is_connected = False

	def event_exists(self, pk):
		return self.get_event_by_id(pk) is not None

	def create_event(self, title, e_date, e_time, description, repeat_weekly, is_past=False):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Creation failure: connect to the database first')
		event = EventModel((
			None,
			title,
			e_date,
			e_time,
			description,
			is_past,
			repeat_weekly,
			0
		))
		event.id = EventModel.insert(self.__cursor, event)
		self.__db.commit()
		return event

	def update_event(self, pk, title=None, e_date=None, e_time=None, description=None, is_past=None, repeat_weekly=None, is_notified=None):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Updating failure: connect to the database first')
		event = self.get_event_by_id(pk)
		if event:
			if title is not None:
				event.title = title
			if e_time is not None:
				event.time = e_time
			if e_date is not None:
				event.date = e_date
			if description is not None:
				event.description = description
			if event.date >= datetime.today().date() and is_past is None:
				event.is_past = False
			else:
				event.is_past = is_past
			if repeat_weekly is not None:
				event.repeat_weekly = repeat_weekly
			if is_notified is not None:
				event.is_notified = is_notified
			EventModel.update(self.__cursor, event)
			self.__db.commit()
			return event
		raise DatabaseException('Updating failure: event does not exist')

	def delete_event(self, pk):
		if self.try_to_reconnect:
			self.connect()
		if not self.is_connected:
			raise DatabaseException('Deleting failure: connect to the database first')
		EventModel.delete(self.__cursor, pk)
		self.__db.commit()
		return None

	def get_events(self, e_date=None, e_time=None, delta=None):
		if not self.is_connected:
			raise DatabaseException('Retrieving failure: connect to the database first')
		return EventModel.select(self.__cursor, e_date, e_time, delta)

	def to_array(self):
		self.connect()
		events = self.get_events()
		return [x.to_dict() for x in events]

	def get_event_by_id(self, pk):
		return EventModel.get(self.__cursor, pk)

	def from_array(self, arr):
		for item in arr:
			EventModel.insert(self.__cursor, EventModel.from_dict(item))
		self.__db.commit()

	@staticmethod
	def prepare_backup_data(events_array, timestamp, include_settings, username=None, settings=Settings().to_dict()):
		data = {
			'db': events_array
		}
		if include_settings:
			data['settings'] = settings
		if username is not None:
			data['username'] = username
		data = json.dumps(data).encode('utf8')
		encoded_data = base64.b64encode(data)
		return {
			'digest': sha512(data).hexdigest(),
			'timestamp': timestamp,
			'backup': encoded_data,
			'backup_size': Storage.count_str_size(encoded_data),
			'events_count': len(events_array),
			'contains_settings': include_settings
		}

	@staticmethod
	def count_str_size(_str):
		units = ['BYTES', 'KB', 'MB', 'GB']
		counter = 0
		k = 1000
		size_in_bytes = len(_str)
		while size_in_bytes > k - 1 and counter < len(units):
			size_in_bytes /= k
			counter += 1
		return str(round(size_in_bytes, 2)) + ' ' + units[counter]

	def restore_from_dict(self, data):
		err_template = 'Restore failure: {}.'
		for key in ['digest', 'timestamp', 'backup']:
			if key not in data:
				raise DatabaseException(err_template.format('invalid backup file'))
		if datetime.now() < datetime.strptime(data['timestamp'], EventModel.TIMESTAMP_FORMAT):
			raise DatabaseException(err_template.format('incorrect timestamp'))
		backup_decoded = base64.b64decode(data['backup'])
		if sha512(backup_decoded).hexdigest() != data['digest']:
			raise DatabaseException(err_template.format('backup is broken'))
		backup = json.loads(backup_decoded.decode('utf8'))
		if 'db' not in backup:
			raise DatabaseException(err_template.format('invalid backup data'))
		self.__cursor.execute(QUERY_DELETE_ALL_EVENTS)
		self.from_array(backup['db'])
		if 'settings' in backup:
			Settings().from_dict(backup['settings'])

	def backup(self, path: str, include_settings):
		timestamp = datetime.strftime(datetime.now(), EventModel.TIMESTAMP_FORMAT)
		with open('{}/{} {}.bak'.format(path.rstrip('/'), self.__backup_file_name, timestamp), 'wb') as file:
			file.write(pickle.dumps(self.prepare_backup_data(self.to_array(), timestamp, include_settings)))

	def restore(self, file_path: str):
		with open(file_path, 'rb') as file:
			self.restore_from_dict(pickle.loads(file.read()))
