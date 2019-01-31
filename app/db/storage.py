import os

from app.db.models import EventModel
from app.db.instance import DATABASE_INSTANCE
from app.settings.default import APP_DB_PATH

import pickle
from hashlib import sha512
from datetime import datetime

from app.settings import Settings


class Storage:

	def __init__(self, connect=True):
		if not os.path.exists(APP_DB_PATH):
			os.makedirs(APP_DB_PATH)

		self.__instance = DATABASE_INSTANCE

		if len(self.__instance.get_tables()) < 1:
			self.__instance.create_tables([EventModel])

		if connect:
			self.connect()

	def connect(self):
		if not self.connected:
			self.__instance.connect()
		return self.connected

	def disconnect(self):
		if self.connected:
			self.__instance.close()
		return not self.connected

	@property
	def connected(self):
		return not self.__instance.is_closed()

	def event_exists(self, pk):
		return self.get_event_by_id(pk) is not None

	@staticmethod
	def get_event_by_id(pk):
		return EventModel.get_by_id(pk)

	def create_event(self, title: str, e_date, e_time, description: str, repeat_weekly: bool, is_past: bool = False):
		if not self.connected:
			raise RuntimeError('creation error: connect to the database first')
		event = EventModel.create(
			title=title,
			time=e_time,
			date=e_date,
			description=description,
			repeat_weekly=repeat_weekly,
			is_past=is_past
		)
		event.save()

	def update_event(self, pk, title=None, e_date=None, e_time=None, description=None, is_past=None, repeat_weekly=None):
		if not self.connected:
			raise RuntimeError('updating error: connect to the database first')
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
		if not self.connected:
			raise RuntimeError('deleting error: connect to the database first')
		event = self.get_event_by_id(pk)
		if event:
			event.delete_instance(recursive=True)

	def get_events(self, e_date=None, e_time=None):
		if not self.connected:
			raise RuntimeError('retrieving error: connect to the database first')
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
		events = self.get_events()
		return [x.to_dict() for x in events]

	@staticmethod
	def from_array(arr):
		for item in arr:
			EventModel.from_dict(item)

	def backup(self, path: str, include_settings=True):
		data = {
			'db': self.to_array()
		}
		if include_settings:
			data['settings'] = Settings().to_dict()
		timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		backup_data = pickle.dumps({
			'digest': sha512(pickle.dumps(data)).hexdigest(),
			'timestamp': timestamp,
			'backup': data
		})
		with open('{}/Event Reminder Backup {}.bak'.format(path.rstrip('/'), timestamp), 'wb') as file:
			file.write(backup_data)

	def restore(self, file_path: str, include_settings=True):
		with open(file_path, 'rb') as file:
			data = pickle.loads(file.read())
			for key in ['digest', 'timestamp', 'backup']:
				if key not in data:
					raise KeyError('invalid backup file')
			if datetime.now() < datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'):
				raise AssertionError('incorrect timestamp')
			if sha512(pickle.dumps(data['backup'])).hexdigest() != data['digest']:
				raise AssertionError('backup is broken')
			if 'db' not in data['backup']:
				raise KeyError('invalid backup data')
			EventModel.delete().execute()
			self.from_array(data['backup']['db'])
			if include_settings:
				if 'settings' not in data['backup']:
					raise KeyError('can\'t restore settings')
				Settings().from_dict(data['backup']['settings'])
