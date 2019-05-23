import os
import sqlite3
from datetime import datetime
from unittest import TestCase
from datetime import timedelta

from erdesktop.storage.storage import Storage
from erdesktop.storage.models import EventModel
from erdesktop.util.exceptions import DatabaseException


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
class TestStorage(TestCase):

	def setUp(self):
		self.storage = Storage(db_file='./test.db', backup_file='./test.bak')
		self.db = sqlite3.connect('./test.db')
		self.cursor = self.db.cursor()
		EventModel.create_table(self.db.cursor())

	def doCleanups(self):
		self.db.close()
		if os.path.exists('./test.db'):
			os.remove('./test.db')
		if os.path.exists('./test.bak'):
			os.remove('./test.bak')

	def clean_db(self):
		self.cursor.execute('DELETE FROM Events;')
		self.db.commit()

	def test_event_exists(self):
		model = EventModel((
			None,
			'some_title',
			datetime.now().date(),
			datetime.now().time(),
			'some description',
			False,
			True,
		))
		lrid = EventModel.insert(self.cursor, model)
		self.db.commit()
		self.assertTrue(self.storage.event_exists(lrid))
		self.clean_db()

	def test_event_does_not_exists(self):
		self.assertFalse(self.storage.event_exists(256))

	def test_create_event(self):
		self.storage.disconnect()
		self.storage.try_to_reconnect = True
		expected = {
			'title': 'some title',
			'e_time': datetime.now().time().replace(microsecond=0),
			'e_date': datetime.now().date(),
			'description': 'some description',
			'repeat_weekly': True,
			'is_past': False
		}
		event_id = self.storage.create_event(**expected).id

		event = EventModel.get(self.cursor, event_id)
		self.assertEqual(event.title, expected['title'])
		self.assertEqual(event.time, expected['e_time'])
		self.assertEqual(event.date, expected['e_date'])
		self.assertEqual(event.description, expected['description'])
		self.assertEqual(event.repeat_weekly, expected['repeat_weekly'])
		self.assertEqual(event.is_past, expected['is_past'])

		self.clean_db()

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

	def test_update_event(self):
		data = (
			None,
			'2019-05-02',
			datetime.now().date(),
			datetime.now().time().replace(microsecond=0),
			'some description',
			False,
			True
		)
		model = EventModel(data)
		model.id = EventModel.insert(self.db.cursor(), model)
		self.db.commit()
		event = EventModel.get(self.db.cursor(), model.id)
		self.assertEqual(event.title, data[1])
		self.assertEqual(event.time, data[3])
		self.assertEqual(event.date, data[2])
		self.assertEqual(event.description, data[4])
		self.assertEqual(event.is_past, data[5])
		self.assertEqual(event.repeat_weekly, data[6])
		expected = {
			'title': 'some title',
			'e_time': datetime.now().time().replace(microsecond=0),
			'e_date': datetime.now().date(),
			'description': 'some_____description',
			'repeat_weekly': False,
			'is_past': False
		}
		self.storage.disconnect()
		self.storage.try_to_reconnect = True
		actual = self.storage.update_event(model.id, **expected)
		self.storage.try_to_reconnect = False
		self.assertEqual(actual.title, expected['title'])
		self.assertEqual(actual.time, expected['e_time'])
		self.assertEqual(actual.date, expected['e_date'])
		self.assertEqual(actual.description, expected['description'])
		self.assertEqual(actual.repeat_weekly, expected['repeat_weekly'])
		self.assertEqual(actual.is_past, expected['is_past'])

		self.clean_db()

	def test_update_event_not_exists(self):
		expected = (
			1,
			'some title',
			datetime.now().date(),
			datetime.now().time().replace(microsecond=0),
			'some_____description',
			False,
			False
		)
		self.assertRaises(DatabaseException, self.storage.update_event, *expected)

	def test_update_event_not_connected(self):
		expected = (
			1,
			'some title',
			datetime.now().date(),
			datetime.now().time().replace(microsecond=0),
			'some_____description',
			False,
			False
		)
		self.storage.disconnect()
		self.assertRaises(DatabaseException, self.storage.update_event, *expected)
		self.storage.connect()

	def test_delete_event(self):
		model = EventModel((
			None,
			'some_title',
			datetime.now().date(),
			datetime.now().time(),
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
		self.storage.try_to_reconnect = False
		self.assertRaises(DatabaseException, self.storage.delete_event, *(999999,))

	def test_get_events(self):
		expected = [
			(
				'title 1', datetime.now().date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 1', 0, 0
			),
			(
				'title 2', (datetime.now() + timedelta(days=2)).date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 2', 0, 1
			),
			(
				'title 3', datetime.now().date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 3', 1, 0
			),
			(
				'title 4', (datetime.now() + timedelta(days=9)).date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 4', 1, 1
			),
		]
		self.cursor.executemany(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?)',
			expected
		)
		self.db.commit()

		actual = self.storage.get_events()
		self.assertEqual(len(actual), len(expected))
		for i in range(len(expected)):
			self.assertEqual(actual[i].id, i + 1)
			self.assertEqual(actual[i].title, expected[i][0])
			self.assertEqual(actual[i].date.strftime(EventModel.DATE_FORMAT), expected[i][1])
			self.assertEqual(actual[i].time.strftime(EventModel.TIME_FORMAT), expected[i][2])
			self.assertEqual(actual[i].description, expected[i][3])
			self.assertEqual(actual[i].is_past, expected[i][4])
			self.assertEqual(actual[i].repeat_weekly, expected[i][5])

		self.clean_db()

	def test_get_events_not_connected(self):
		self.storage.disconnect()
		self.assertRaises(DatabaseException, self.storage.get_events)
		self.storage.connect()

	def test_get_array(self):
		expected = [
			(
				'title 1', datetime.now().date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 1', 0, 0
			),
			(
				'title 2', (datetime.now() + timedelta(days=2)).date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 2', 0, 1
			),
			(
				'title 3', datetime.now().date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 3', 1, 0
			),
			(
				'title 4', (datetime.now() + timedelta(days=9)).date().strftime(EventModel.DATE_FORMAT),
				datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some descr 4', 1, 1
			),
		]
		self.cursor.executemany(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?)',
			expected
		)
		self.db.commit()

		actual = self.storage.to_array()
		self.assertEqual(len(actual), len(expected))
		for i in range(len(expected)):
			self.assertEqual(actual[i].get('title'), expected[i][0])
			self.assertEqual(actual[i].get('date'), expected[i][1])
			self.assertEqual(actual[i].get('time'), expected[i][2])
			self.assertEqual(actual[i].get('description'), expected[i][3])
			self.assertEqual(actual[i].get('is_past'), expected[i][4])
			self.assertEqual(actual[i].get('repeat_weekly'), expected[i][5])

		self.clean_db()

	def test_get_event_by_id(self):
		expected = (
			'some title', datetime.now().date().strftime(EventModel.DATE_FORMAT),
			datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT), 'Some description', 0, 0
		)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?)',
			expected
		)
		self.db.commit()
		actual = self.storage.get_event_by_id(self.cursor.lastrowid)
		self.assertIsNotNone(actual)
		self.assertEqual(actual.title, expected[0])
		self.assertEqual(actual.date.strftime(EventModel.DATE_FORMAT), expected[1])
		self.assertEqual(actual.time.strftime(EventModel.TIME_FORMAT), expected[2])
		self.assertEqual(actual.description, expected[3])
		self.assertEqual(actual.is_past, expected[4])
		self.assertEqual(actual.repeat_weekly, expected[5])

	def test_get_event_by_id_not_existing(self):
		self.assertIsNone(self.storage.get_event_by_id(9999))

	def test_from_array(self):
		expected = [
			{
				'title': 'title 1',
				'date':	datetime.now().date().strftime(EventModel.DATE_FORMAT),
				'time':	datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT),
				'description': 'Some descr 1',
				'is_past': 0,
				'repeat_weekly': 0
			},
			{
				'title': 'title 2',
				'date': (datetime.now() + timedelta(days=2)).date().strftime(EventModel.DATE_FORMAT),
				'time': datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT),
				'description': 'Some descr 2',
				'is_past': 0,
				'repeat_weekly': 1
			},
			{
				'title': 'title 3',
				'date': datetime.now().date().strftime(EventModel.DATE_FORMAT),
				'time': datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT),
				'description': 'Some descr 3',
				'is_past': 1,
				'repeat_weekly': 0
			},
			{
				'title': 'title 4',
				'date': (datetime.now() + timedelta(days=9)).date().strftime(EventModel.DATE_FORMAT),
				'time': datetime.now().time().replace(microsecond=0).strftime(EventModel.TIME_FORMAT),
				'description': 'Some descr 4',
				'is_past': 1,
				'repeat_weekly': 1
			}
		]
		self.storage.from_array(expected)
		actual = self.cursor.execute('SELECT * FROM Events;').fetchall()
		self.assertEqual(len(actual), len(expected))
		for i in range(len(expected)):
			self.assertEqual(actual[i][0], i + 1)
			self.assertEqual(actual[i][1], expected[i].get('title'))
			self.assertEqual(actual[i][2], expected[i].get('date'))
			self.assertEqual(actual[i][3], expected[i].get('time'))
			self.assertEqual(actual[i][4], expected[i].get('description'))
			self.assertEqual(actual[i][5], expected[i].get('is_past'))
			self.assertEqual(actual[i][6], expected[i].get('repeat_weekly'))

		self.clean_db()
