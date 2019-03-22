from datetime import datetime

from erdesktop.storage.sql import QUERY_INSERT_EVENT, QUERY_UPDATE_EVENT, QUERY_DELETE_EVENT_BY_ID, \
	QUERY_SELECT_EVENT_BY_ID, QUERY_SELECT_EVENTS_BY, QUERY_CREATE_EVENT_TABLE


class EventModel:
	"""
	Represents event in database.
	"""

	def __init__(self, fields):
		self.id = fields[0]
		self.title = fields[1]
		dt = fields[2]
		if isinstance(dt, str):
			last_dot = dt.rfind('.')
			dt = dt[:last_dot + 1]
			self.date = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').date()
			self.time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').time()
		else:
			self.date = dt.date()
			self.time = dt.time()
		self.description = fields[3]
		self.is_past = True if fields[4] == 1 else False
		self.repeat_weekly = True if fields[5] == 1 else False

	def to_dict(self):
		return {
			'title': self.title,
			'date': '{:%Y-%m-%d}'.format(self.date),
			'time': '{:%H:%M:00}'.format(self.time),
			'description': self.description,
			'is_past': 1 if self.is_past is True else 0,
			'repeat_weekly': 1 if self.repeat_weekly is True else 0
		}

	@staticmethod
	def from_dict(data):
		return EventModel((
			None,
			data['title'],
			datetime.combine(data['date'], data['time']).strftime('%Y-%m-%d %H:%M:00'),
			data['description'],
			data['is_past'],
			data['repeat_weekly']
		))

	@staticmethod
	def create_table(cursor):
		print(cursor.execute(QUERY_CREATE_EVENT_TABLE).fetchone())

	@staticmethod
	def select(cursor, date=None, time=None):
		condition = ''
		if date is not None:
			condition += 'date = {}'.format(date.strftime('%Y-%m-%d'))
		if time is not None:
			time_condition = 'time = {}'.format(time.strftime('%H:%M:00'))
			if condition != '':
				condition += ' AND '
			condition += time_condition
		if condition != '':
			condition = ' WHERE ' + condition
		query_result = cursor.execute(QUERY_SELECT_EVENTS_BY.format(condition)).fetchall()
		return [EventModel(item) for item in query_result]

	@staticmethod
	def get(cursor, pk):
		result_tuple = cursor.execute(QUERY_SELECT_EVENTS_BY.format('WHERE id = ?'), (pk,)).fetchone()
		if result_tuple is not None:
			print(result_tuple)
			return EventModel(result_tuple)
		return None

	@staticmethod
	def insert(cursor, model):
		print(cursor.execute(
			QUERY_INSERT_EVENT,
			(model.title, datetime.combine(model.date, model.time), model.description, model.is_past, model.repeat_weekly)
		).fetchone())
		return cursor.lastrowid

	@staticmethod
	def update(cursor, model):
		print(cursor.execute(
			QUERY_UPDATE_EVENT,
			(model.title, datetime.combine(model.date, model.time), model.description, model.is_past, model.repeat_weekly, model.id)
		).fetchall())
		return cursor.lastrowid

	@staticmethod
	def delete(cursor, pk):
		print(cursor.execute(QUERY_DELETE_EVENT_BY_ID, (pk,)).fetchall())
		return cursor.lastrowid
