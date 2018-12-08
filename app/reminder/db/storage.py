from app.reminder.db.models import EventModel
from app.reminder.db.models import database_instance


def connect():
	database_instance.create_tables([EventModel])
	if database_instance.is_closed():
		database_instance.connect()


def disconnect():
	if not database_instance.is_closed():
		database_instance.close()


def create_event(title: str, e_date, e_time, description: str):
	if database_instance.is_closed():
		database_instance.connect()
	event = EventModel.create(
		title=title,
		time=e_time,
		date=e_date,
		description=description
	)
	event.save()


def get_events(e_date=None, e_time=None):
	if database_instance.is_closed():
		database_instance.connect()
	if e_date is not None and e_time is not None:
		result = EventModel.select().where((EventModel.time == e_time) & (EventModel.date == e_date))
	elif e_date is not None:
		result = EventModel.select().where(EventModel.date == e_date)
	elif e_time is not None:
		result = EventModel.select().where(EventModel.time == e_time)
	else:
		result = EventModel.select()
	return [item for item in result]
