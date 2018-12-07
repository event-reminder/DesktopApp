from app.reminder.db.models import EventModel
from app.reminder.db.models import database_instance


def connect():
	database_instance.create_tables([EventModel])
	if database_instance.is_closed():
		database_instance.connect()


def disconnect():
	if not database_instance.is_closed():
		database_instance.close()


def create_event(title: str, description: str=None, e_date=None, e_time=None):
	if database_instance.is_closed():
		database_instance.connect()
	data = {
		'title': title
	}
	if description:
		data['description'] = description
	if e_time:
		data['time'] = e_time
	if e_date:
		data['date'] = e_date
	EventModel.create(**data)


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


"""
if __name__ == '__main__':
	from datetime import date, time
	event_date = date(2018, 12, 14)
	event_time = time(0, 0)

	connect()
#	create_event('Some other deadline efregrgerg', 'Need to finissfdfrefrreh the task', event_date, event_time)
	print(get_events(e_time=event_time))
	disconnect()
"""
