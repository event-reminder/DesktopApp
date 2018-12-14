import peewee

from app.reminder.db.db import database_instance


class EventModel(peewee.Model):
	title = peewee.CharField(max_length=500)
	date = peewee.DateField(formats=['%Y-%m-%d'])
	time = peewee.TimeField(formats=['%H:%M'])
	description = peewee.TextField()
	is_past = peewee.BooleanField(default=False)

	def __str__(self):
		return """Event Model:
	title: {},
	date: {},
	time: {},
	description: {}
""".format(self.title, self.date, self.time, self.description)

	class Meta:
		database = database_instance
