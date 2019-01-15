from app.reminder.db.models import EventModel
from app.reminder.db.models import database_instance


def create_if_not_exist():
	if len(database_instance.get_tables()) < 1:
		database_instance.create_tables([EventModel])


def connect():
	create_if_not_exist()
	if database_instance.is_closed():
		database_instance.connect()


def disconnect():
	if not database_instance.is_closed():
		database_instance.close()


def exists(pk):
	return EventModel.get_by_id(pk) is not None


def get_by_id(pk):
	try:
		return EventModel.get_by_id(pk)
	except Exception as exc:
		print(exc)
	return None


def create_event(title: str, e_date, e_time, description: str, repeat_weekly: bool):
	connected_locally = False
	if database_instance.is_closed():
		connected_locally = True
		database_instance.connect()
	event = EventModel.create(
		title=title,
		time=e_time,
		date=e_date,
		description=description,
		repeat_weekly=repeat_weekly
	)
	event.save()
	if connected_locally:
		disconnect()


def update_event(pk, title=None, e_date=None, e_time=None, description=None, is_past=None, repeat_weekly=None):
	connected_locally = False
	if database_instance.is_closed():
		connected_locally = True
		database_instance.connect()
	event = get_by_id(pk)
	if event:
		data = {}
		if title:
			data['title'] = title
		if e_time:
			data['time'] = e_time
		if e_date:
			data['date'] = e_date
		if description:
			data['description'] = description
		if is_past:
			data['is_past'] = is_past
		if repeat_weekly:
			data['repeat_weekly'] = repeat_weekly
		event.update(**data).execute()
	if connected_locally:
		disconnect()
	return event


def delete_event(pk):
	connected_locally = False
	if database_instance.is_closed():
		connected_locally = True
		database_instance.connect()
	event = get_by_id(pk)
	if event:
		event.delete_instance(recursive=True)
	if connected_locally:
		disconnect()


def get_events(e_date=None, e_time=None):
	connected_locally = False
	if database_instance.is_closed():
		connected_locally = True
		database_instance.connect()
	if e_date is not None and e_time is not None:
		result = EventModel.select().where((EventModel.time == e_time) & (EventModel.date == e_date))
	elif e_date is not None:
		result = EventModel.select().where(EventModel.date == e_date)
	elif e_time is not None:
		result = EventModel.select().where(EventModel.time == e_time)
	else:
		result = EventModel.select()
	if connected_locally:
		disconnect()
	return [item for item in result]
