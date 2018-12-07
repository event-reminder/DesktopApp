import peewee

from app.reminder.db.db import database_instance


class EventModel(peewee.Model):
	title = peewee.CharField(max_length=500)
	description = peewee.CharField(max_length=4096)
	date = peewee.DateField(formats=['%Y-%m-%d'])
	time = peewee.TimeField(formats=['%H:%M'])

	class Meta:
		database = database_instance
