import os
import sqlite3
from datetime import datetime
from unittest import TestCase, skip

import peewee

from erdesktop.settings import APP_DB_PATH
from erdesktop.storage.models import EventModel
from erdesktop.storage.storage import Storage
from erdesktop.util.exceptions import DatabaseException


@skip
class TestStorage(TestCase):

	def setUp(self):
		self.storage = Storage(db_file='./test.db', backup_file='./test.bak')
		self.db = sqlite3.connect('./test.db')
		EventModel.create_table(self.db.cursor())

	def doCleanups(self):
		self.db.close()
		if os.path.exists('./test.db'):
			os.remove('./test.db')
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
		model = EventModel((
			None,
			'some_title',
			datetime.now().strftime('%Y-%m-%d %H:%M:00'),
			'some description',
			False,
			True,
		))
		lrid = EventModel.insert(self.db.cursor(), model)

		print(lrid)

		self.db.commit()
		self.assertTrue(self.storage.event_exists(lrid))

	def test_event_does_not_exists(self):
		self.assertFalse(self.storage.event_exists(256))

	def test_create_event(self):
	#	self.storage.disconnect()
	#	self.storage.try_to_reconnect = True
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
			event = EventModel.get(self.db.cursor(), event_id)
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
			'e_time': datetime.now().time().strftime('%H:%M:00'),
			'e_date': datetime.now().date().strftime('%Y-%m-%d'),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		})

	@skip
	def test_update_event(self):
		data = (
			None,
			'some_title_title',
			datetime.now().date().strftime('%Y-%m-%d'),
			datetime.now().time().strftime('%H:%M:00'),
			'some description',
			False,
			True
		)
		model = EventModel(data)
		EventModel.insert(self.db.cursor(), model)
		self.db.commit()
		event = EventModel.get(self.db.cursor(), model.id)
		self.assertEqual(event.title, data[1])
		self.assertEqual(event.time, str(data[3]))
		self.assertEqual(event.date, data[2])
		self.assertEqual(event.description, data[4])
		self.assertEqual(event.repeat_weekly, data[5])
		self.assertEqual(event.is_past, data[6])
		expected = {
			'title': 'some title',
			'e_time': datetime.now().time().replace(microsecond=0),
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
		model = EventModel((
			None,
			'some_title',
			datetime.now(),
			'some description',
			False,
			True
		))
		last = EventModel.insert(self.db.cursor(), model)
		self.db.commit()
		self.assertTrue(self.storage.event_exists(last))
		self.storage.try_to_reconnect = True
		self.storage.delete_event(last)
		self.assertFalse(self.storage.event_exists(last))

	def test_delete_event_db_connection_failed(self):
		self.storage.disconnect()
		self.assertRaises(DatabaseException, self.storage.delete_event, *(999999,))
