import os
from datetime import datetime
from unittest import TestCase, skip

import peewee

from erdesktop.settings import APP_DB_FILE
from erdesktop.storage.models import EventModel
from erdesktop.storage.storage import Storage
from erdesktop.util.exceptions import DatabaseException


class TestStorage(TestCase):

	def setUp(self):
		self.storage = Storage(backup_file='./test.bak')

	def doCleanups(self):
		if os.path.exists(APP_DB_FILE + 'test.db'):
			pass
			# os.remove(APP_DB_FILE + 'test.db')
		if os.path.exists('./test.bak'):
			os.remove('./test.bak')

	def test_is_connected(self):
		self.storage.disconnect()
		self.storage.connect()
		self.assertEqual(self.storage.is_connected, True)

	def test_is_not_connected(self):
		self.storage.disconnect()
		self.assertEqual(self.storage.is_connected, False)

	def test_event_exists(self):
		model = EventModel.create(**{
			'title': 'some_title',
			'time': datetime.now().time(),
			'date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		})
		model.save()
		self.assertTrue(self.storage.event_exists(model.id))
		EventModel.get_by_id(model.id).delete_instance(recursive=True)

	def test_event_does_not_exists(self):
		self.assertFalse(self.storage.event_exists(256))

	def test_create_event(self):
		self.storage.disconnect()
		self.storage.try_to_reconnect = True
		expected = {
			'title': 'some title',
			'e_time': datetime.now().time(),
			'e_date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		}
		event_id = self.storage.create_event(**expected).id
		try:
			event = EventModel.get_by_id(event_id)
			self.assertEqual(event.title, expected['title'])
			self.assertEqual(event.time, str(expected['e_time']))
			self.assertEqual(event.date, expected['e_date'])
			self.assertEqual(event.description, expected['description'])
			self.assertEqual(event.repeat_weekly, expected['repeat_weekly'])
			self.assertEqual(event.is_past, expected['is_past'])
			event.delete_instance(recursive=True)
		except peewee.DoesNotExist:
			self.fail()

	def test_create_event_db_connection_failed(self):
		self.storage.disconnect()
		self.assertRaises(DatabaseException, self.storage.create_event, **{
			'title': 'some title',
			'e_time': datetime.now().time(),
			'e_date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		})

	@skip
	def test_update_event(self):
		data = {
			'title': 'some_title_title',
			'time': datetime.now().time(),
			'date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		}
		model = EventModel.create(**data)
		model.save()
		event = EventModel.get_by_id(model.id)
		self.assertEqual(event.title, data['title'])
		self.assertEqual(event.time, str(data['time']))
		self.assertEqual(event.date, data['date'])
		self.assertEqual(event.description, data['description'])
		self.assertEqual(event.repeat_weekly, data['repeat_weekly'])
		self.assertEqual(event.is_past, data['is_past'])
		expected = {
			'title': 'some title',
			'e_time': datetime.now().time(),
			'e_date': datetime.now().date(),
			'description': 'some_____description',
			'repeat_weekly': False,
			'is_past': False
		}
		actual = self.storage.update_event(model.id, **expected)
		self.assertEqual(actual.title, expected['title'])
		self.assertEqual(actual.time, expected['e_time'])
		self.assertEqual(actual.date, expected['e_date'])
		self.assertEqual(actual.description, expected['description'])
		self.assertEqual(actual.repeat_weekly, expected['repeat_weekly'])
		self.assertEqual(actual.is_past, expected['is_past'])
		actual.delete_instance(recursive=True)

	def test_delete_event(self):
		model = EventModel.create(**{
			'title': 'some_title',
			'time': datetime.now().time(),
			'date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		})
		model.save()
		self.assertTrue(self.storage.event_exists(model.id))
		self.storage.try_to_reconnect = True
		self.storage.delete_event(model.id)
		self.assertFalse(self.storage.event_exists(model.id))

	def test_delete_event_db_connection_failed(self):
		self.storage.disconnect()
		self.assertRaises(DatabaseException, self.storage.delete_event, *(999999,))
