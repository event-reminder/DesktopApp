from datetime import datetime, timedelta

from erdesktop.storage.sql import (
	QUERY_INSERT_EVENT,
	QUERY_UPDATE_EVENT,
	QUERY_SELECT_EVENTS_BY,
	QUERY_DELETE_EVENT_BY_ID,
	QUERY_CREATE_EVENT_TABLE
)


class EventModel:
	"""
	Represents event in database.
	"""

	DATE_FORMAT = '%Y-%m-%d'
	TIME_FORMAT = '%H:%M:%S'
	TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
	DATE_TIME_FORMAT = '{} {}'.format(DATE_FORMAT, TIME_FORMAT)

	def __init__(self, fields):
		if isinstance(fields, dict):
			fields = self.to_tuple(fields)
		elif isinstance(fields, tuple) and len(fields) != 8:
			fields = (None,) + fields
		self.id = fields[0]
		self.title = fields[1]

		date = fields[2]
		if isinstance(date, str):
			self.date = datetime.strptime(date, self.DATE_FORMAT).date()
		else:
			self.date = date

		time = fields[3]
		if isinstance(date, str):
			last_dot = time.rfind('.')
			if last_dot != -1:
				time = time[:last_dot]
			self.time = datetime.strptime(time, self.TIME_FORMAT).time()
		else:
			self.time = time.replace(microsecond=0)
		self.description = fields[4]
		self.is_past = True if fields[5] == 1 else False
		self.repeat_weekly = True if fields[6] == 1 else False
		self.is_notified = fields[7]

	@staticmethod
	def to_tuple(fields: dict):
		return (
			fields.get('id', None),
			fields.get('title', None),
			fields.get('date', None),
			fields.get('time', None),
			fields.get('description', None),
			fields.get('is_past', None),
			fields.get('repeat_weekly', None),
			fields.get('is_notified', None) != 0
		)

	def to_dict(self):
		return {
			'title': self.title,
			'date': self.date.strftime(self.DATE_FORMAT),
			'time': self.time.strftime(self.TIME_FORMAT),
			'description': self.description,
			'is_past': 1 if self.is_past is True else 0,
			'repeat_weekly': 1 if self.repeat_weekly is True else 0,
			'is_notified': self.is_notified
		}

	@staticmethod
	def from_dict(data):
		return EventModel(EventModel.to_tuple(data))

	@staticmethod
	def create_table(cursor):
		cursor.execute(QUERY_CREATE_EVENT_TABLE)

	@staticmethod
	def get(cursor, pk):
		result_tuple = cursor.execute(QUERY_SELECT_EVENTS_BY.format('WHERE id = ?'), (pk,)).fetchone()
		if result_tuple is not None:
			return EventModel(result_tuple)
		return None

	@staticmethod
	def insert(cursor, model):
		cursor.execute(QUERY_INSERT_EVENT, (
			model.title,
			model.date.strftime(EventModel.DATE_FORMAT),
			model.time.strftime(EventModel.TIME_FORMAT),
			model.description,
			model.is_past,
			model.repeat_weekly
		))
		return cursor.lastrowid

	@staticmethod
	def update(cursor, model):
		cursor.execute(QUERY_UPDATE_EVENT, (
			model.title,
			model.date.strftime(EventModel.DATE_FORMAT),
			model.time.strftime(EventModel.TIME_FORMAT),
			model.description,
			model.is_past,
			model.repeat_weekly,
			model.is_notified,
			model.id
		))
		return model.id

	@staticmethod
	def delete(cursor, pk):
		if EventModel.get(cursor, pk) is not None:
			cursor.execute(QUERY_DELETE_EVENT_BY_ID, (pk,))
			return True
		return False

	@staticmethod
	def select(cursor, date=None, time=None, delta=None):
		condition = ''
		if date is not None:
			condition += '(date '
			if delta is not None:
				condition += 'BETWEEN \'{}\' AND \'{}\')'.format(
					date.strftime(EventModel.DATE_FORMAT),
					(date + timedelta(minutes=delta)).strftime(EventModel.DATE_FORMAT)
				)
			else:
				condition += '= \'{}\')'.format(date.strftime(EventModel.DATE_FORMAT))
		if time is not None:
			time_condition = 'time = \'{}\''.format(time.strftime(EventModel.TIME_FORMAT))
			if condition != '':
				condition += ' AND '
			condition += time_condition
		if condition != '':
			condition = 'WHERE ' + condition
		query_result = cursor.execute(QUERY_SELECT_EVENTS_BY.format(condition)).fetchall()
		return [EventModel(item) for item in query_result]

	def expired(self, now):
		return now >= datetime.combine(self.date, self.time)
