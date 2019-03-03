import peewee
from datetime import datetime

from erdesktop.storage.instance import DATABASE_INSTANCE


class EventModel(peewee.Model):
	"""
	Represents event in database.
	"""

	title = peewee.CharField(max_length=500)
	date = peewee.DateField(formats=['%Y-%m-%d'])
	time = peewee.TimeField(formats=['%H:%M'])
	description = peewee.TextField()
	is_past = peewee.BooleanField(default=False)
	repeat_weekly = peewee.BooleanField(default=False)

	def to_dict(self):
		return {
			'title': self.title,
			'date': '{:%Y-%m-%d}'.format(self.date),
			'time': self.time,
			'description': self.description,
			'is_past': self.is_past,
			'repeat_weekly': self.repeat_weekly
		}

	@staticmethod
	def from_dict(data):
		event = EventModel.create(
			title=data['title'],
			time=datetime.strptime(data['time'], '%H:%M:00'),
			date=datetime.strptime(data['date'], '%Y-%m-%d'),
			description=data['description'],
			repeat_weekly=data['repeat_weekly'],
			is_past=data['is_past']
		)
		event.save()

	class Meta:
		database = DATABASE_INSTANCE
