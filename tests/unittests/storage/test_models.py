import os
import sqlite3
from datetime import datetime
from unittest import TestCase
from datetime import timedelta

from erdesktop.storage.models import EventModel
from erdesktop.storage.sql import QUERY_CREATE_EVENT_TABLE


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
class TestStorage(TestCase):

	def setUp(self):
		self.db = sqlite3.connect('./test.db')
		self.cursor = self.db.cursor()
		EventModel.create_table(self.cursor)

	def doCleanups(self):
		self.db.close()
		if os.path.exists('./test.db'):
			os.remove('./test.db')

	def clean_db(self):
		self.cursor.execute('DELETE FROM Events;')

	def test_init_dict(self):
		dt = datetime.now()
		expected = {
			'title': 'some title',
			'date': dt.date().strftime('%Y-%m-%d'),
			'time': dt.time().strftime('%H:%M:%S.%f'),
			'description': 'Some description',
			'is_past': 1,
			'repeat_weekly': 0
		}
		actual = EventModel(expected)
		self.assertEqual(actual.id, None)
		self.assertEqual(actual.title, expected.get('title'))
		self.assertEqual(actual.date, datetime.strptime(expected.get('date'), '%Y-%m-%d').date())
		self.assertEqual(actual.time, datetime.strptime(expected.get('time'), '%H:%M:%S.%f').time().replace(microsecond=0))
		self.assertEqual(actual.description, expected.get('description'))
		self.assertEqual(actual.is_past, expected.get('is_past'))
		self.assertEqual(actual.repeat_weekly, expected.get('repeat_weekly'))

	def test_init_tuple(self):
		dt = datetime.now()
		expected = ('some title', dt.date().strftime('%Y-%m-%d'), dt.time().strftime('%H:%M:%S.%f'), 'Some description', 1, 0)
		actual = EventModel(expected)
		self.assertEqual(actual.id, None)
		self.assertEqual(actual.title, expected[0])
		self.assertEqual(actual.date, datetime.strptime(expected[1], '%Y-%m-%d').date())
		self.assertEqual(actual.time, datetime.strptime(expected[2], '%H:%M:%S.%f').time().replace(microsecond=0))
		self.assertEqual(actual.description, expected[3])
		self.assertEqual(actual.is_past, expected[4])
		self.assertEqual(actual.repeat_weekly, expected[5])

	def test_to_tuple(self):
		expected = {
			'id': 1,
			'title': 'some title',
			'date': datetime.now().strftime(EventModel.DATE_FORMAT),
			'time': datetime.now().strftime(EventModel.TIME_FORMAT),
			'description': 'Some description',
			'is_past': 1,
			'repeat_weekly': 0
		}
		actual = EventModel.to_tuple(expected)
		self.assertEqual(expected.get('id'), actual[0])
		self.assertEqual(expected.get('title'), actual[1])
		self.assertEqual(expected.get('date'), actual[2])
		self.assertEqual(expected.get('time'), actual[3])
		self.assertEqual(expected.get('description'), actual[4])
		self.assertEqual(expected.get('is_past'), actual[5])
		self.assertEqual(expected.get('repeat_weekly'), actual[6])

	def test_to_dict(self):
		expected = {
			'title': 'some title',
			'date': datetime.now().strftime(EventModel.DATE_FORMAT),
			'time': datetime.now().strftime(EventModel.TIME_FORMAT),
			'description': 'Some description',
			'is_past': 1,
			'repeat_weekly': 0,
			'is_notified': True
		}
		actual = EventModel(expected).to_dict()
		self.assertDictEqual(expected, actual)

	def test_from_dict(self):
		expected = {
			'id': 1,
			'title': 'some title',
			'date': datetime.now().date().strftime(EventModel.DATE_FORMAT),
			'time': datetime.now().time().strftime(EventModel.TIME_FORMAT),
			'description': 'Some description',
			'is_past': 1,
			'repeat_weekly': 0
		}
		actual = EventModel.from_dict(expected)
		self.assertEqual(actual.id, expected.get('id'))
		self.assertEqual(actual.title, expected.get('title'))
		self.assertEqual(actual.date, datetime.strptime(expected.get('date'), EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(expected.get('time'), EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, expected.get('description'))
		self.assertEqual(actual.is_past, expected.get('is_past'))
		self.assertEqual(actual.repeat_weekly, expected.get('repeat_weekly'))

	def test_table_exists(self):
		try:
			self.cursor.execute('SELECT * FROM Events').fetchall()
		except sqlite3.Error:
			self.fail()
		self.clean_db()

	def test_table_does_not_exist(self):
		self.cursor.execute('DROP TABLE Events;')
		self.assertRaises(sqlite3.Error, self.cursor.execute, *('SELECT * FROM Events',))
		self.cursor.execute(QUERY_CREATE_EVENT_TABLE)

	def test_get(self):
		expected = ('Some title', datetime.now().date().strftime(EventModel.DATE_FORMAT), datetime.now().time().strftime(EventModel.TIME_FORMAT), 'Some description', 1, 0)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?);',
			expected
		)
		item_id = self.cursor.lastrowid
		actual = EventModel.get(self.cursor, item_id)
		self.assertIsNotNone(actual)
		self.assertEqual(actual.id, item_id)
		self.assertEqual(actual.title, expected[0])
		self.assertEqual(actual.date, datetime.strptime(expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, expected[3])
		self.assertEqual(actual.is_past, expected[4])
		self.assertEqual(actual.repeat_weekly, expected[5])
		self.clean_db()

	def test_get_failed(self):
		self.assertIsNone(EventModel.get(self.cursor, 1))

	def test_insert(self):
		dt = datetime.now()
		item_id = EventModel.insert(
			self.cursor,
			EventModel((None, 'Some title', dt.date(), dt.time(), 'Some description', 1, 0))
		)
		self.assertEqual(item_id, 1)
		actual = self.cursor.execute('SELECT * FROM Events WHERE id = ?;', (item_id,)).fetchone()
		self.assertIsNotNone(actual)
		self.assertTupleEqual(
			(item_id, 'Some title', dt.date().strftime(EventModel.DATE_FORMAT), dt.time().strftime(EventModel.TIME_FORMAT), 'Some description', 1, 0), actual
		)
		self.clean_db()

	def test_update(self):
		dt = datetime.now()
		expected = ('Some title', dt.date().strftime(EventModel.DATE_FORMAT), dt.time().strftime(EventModel.TIME_FORMAT), 'Some description', 1, 1)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?);',
			('Some title', dt.date().strftime(EventModel.DATE_FORMAT), dt.time().strftime(EventModel.TIME_FORMAT), 'Some description', 1, 1)
		)
		actual = self.cursor.execute('SELECT * FROM Events WHERE id = ?;', (self.cursor.lastrowid,)).fetchone()
		self.assertIsNotNone(actual)
		self.assertEqual(1, actual[0])
		self.assertEqual(expected[0], actual[1])
		self.assertEqual(expected[1], actual[2])
		self.assertEqual(expected[2], actual[3])
		self.assertEqual(expected[3], actual[4])
		self.assertEqual(expected[4], actual[5])
		self.assertEqual(expected[5], actual[6])

		dt_modified = dt + timedelta(days=1)
		modified = (1, 'Some title edited', dt_modified.date().strftime(EventModel.DATE_FORMAT), dt_modified.time().strftime(EventModel.TIME_FORMAT), 'Some description edited', 0, 1)
		model = EventModel(modified)
		item_id = EventModel.update(self.cursor, model)
		actual = self.cursor.execute('SELECT * FROM Events WHERE id = ?;', (item_id,)).fetchone()
		self.assertIsNotNone(actual)
		self.assertEqual(modified[0], actual[0])
		self.assertEqual(modified[1], actual[1])
		self.assertEqual(modified[2], actual[2])
		self.assertEqual(modified[3], actual[3])
		self.assertEqual(modified[4], actual[4])
		self.assertEqual(modified[5], actual[5])
		self.assertEqual(modified[6], actual[6])

		self.clean_db()

	def test_delete(self):
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?);',
			('Some title', datetime.now().date().strftime(EventModel.DATE_FORMAT), datetime.now().time().strftime(EventModel.TIME_FORMAT), 'Some description', 1, 1)
		)
		self.assertIsNotNone(self.cursor.execute('SELECT * FROM Events WHERE id = ?;', (1,)).fetchone())
		EventModel.delete(self.cursor, self.cursor.lastrowid)
		self.assertIsNone(self.cursor.execute('SELECT * FROM Events WHERE id = ?;', (1,)).fetchone())

	def test_delete_not_existing(self):
		self.assertFalse(EventModel.delete(self.cursor, 99999))

	def test_select_all(self):
		now = datetime.now()
		item_1_expected = ('Some title 1', (now + timedelta(days=2)).date().strftime(EventModel.DATE_FORMAT), (now + timedelta(days=2)).time().strftime(EventModel.TIME_FORMAT), 'Some description 1', 0, 1)
		item_2_expected = ('Some title 2', now.date().strftime(EventModel.DATE_FORMAT), now.time().strftime(EventModel.TIME_FORMAT), 'Some description 2', 1, 0)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?);',
			item_1_expected + item_2_expected
		)
		actual = EventModel.select(self.cursor)
		self.assertEqual(len(actual), 2)
		actual_1 = actual[0]
		self.assertEqual(actual_1.id, 1)
		self.assertEqual(actual_1.title, item_1_expected[0])
		self.assertEqual(actual_1.date, datetime.strptime(item_1_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual_1.time, datetime.strptime(item_1_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual_1.description, item_1_expected[3])
		self.assertEqual(actual_1.is_past, item_1_expected[4])
		self.assertEqual(actual_1.repeat_weekly, item_1_expected[5])

		actual_2 = actual[1]
		self.assertEqual(actual_2.id, 2)
		self.assertEqual(actual_2.title, item_2_expected[0])
		self.assertEqual(actual_2.date, datetime.strptime(item_2_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual_2.time, datetime.strptime(item_2_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual_2.description, item_2_expected[3])
		self.assertEqual(actual_2.is_past, item_2_expected[4])
		self.assertEqual(actual_2.repeat_weekly, item_2_expected[5])

	def test_select_by_date(self):
		dt = datetime.now()
		item_1_expected = ('Some title 1', (dt + timedelta(days=2)).date().strftime(EventModel.DATE_FORMAT), (dt + timedelta(days=2)).time().strftime(EventModel.TIME_FORMAT), 'Some description 1', 0, 1)
		item_2_expected = ('Some title 2', dt.date().strftime(EventModel.DATE_FORMAT), dt.time().strftime(EventModel.TIME_FORMAT), 'Some description 2', 1, 0)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?);',
			item_1_expected + item_2_expected
		)
		actual_list = EventModel.select(self.cursor, date=(dt + timedelta(days=2)).date())
		self.assertEqual(len(actual_list), 1)
		actual = actual_list[0]
		self.assertEqual(actual.id, 1)
		self.assertEqual(actual.title, item_1_expected[0])
		self.assertEqual(actual.date, datetime.strptime(item_1_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(item_1_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, item_1_expected[3])
		self.assertEqual(actual.is_past, item_1_expected[4])
		self.assertEqual(actual.repeat_weekly, item_1_expected[5])

		actual_list = EventModel.select(self.cursor, date=dt.date())
		self.assertEqual(len(actual_list), 1)
		actual = actual_list[0]
		self.assertEqual(actual.id, 2)
		self.assertEqual(actual.title, item_2_expected[0])
		self.assertEqual(actual.date, datetime.strptime(item_2_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(item_2_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, item_2_expected[3])
		self.assertEqual(actual.is_past, item_2_expected[4])
		self.assertEqual(actual.repeat_weekly, item_2_expected[5])

		self.clean_db()

	def test_select_by_time(self):
		dt = datetime.now()
		item_1_expected = ('Some title 1', (dt + timedelta(minutes=30)).date().strftime(EventModel.DATE_FORMAT), (dt + timedelta(minutes=30)).time().strftime(EventModel.TIME_FORMAT), 'Some description 1', 0, 1)
		item_2_expected = ('Some title 2', dt.date().strftime(EventModel.DATE_FORMAT), dt.time().strftime(EventModel.TIME_FORMAT), 'Some description 2', 1, 0)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?);',
			item_1_expected + item_2_expected
		)
		actual_list = EventModel.select(self.cursor, time=(dt + timedelta(minutes=30)).time())
		self.assertEqual(len(actual_list), 1)
		actual = actual_list[0]
		self.assertEqual(actual.id, 1)
		self.assertEqual(actual.title, item_1_expected[0])
		self.assertEqual(actual.date, datetime.strptime(item_1_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(item_1_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, item_1_expected[3])
		self.assertEqual(actual.is_past, item_1_expected[4])
		self.assertEqual(actual.repeat_weekly, item_1_expected[5])

		actual_list = EventModel.select(self.cursor, time=dt.time())
		self.assertEqual(len(actual_list), 1)
		actual = actual_list[0]
		self.assertEqual(actual.id, 2)
		self.assertEqual(actual.title, item_2_expected[0])
		self.assertEqual(actual.date, datetime.strptime(item_2_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(item_2_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, item_2_expected[3])
		self.assertEqual(actual.is_past, item_2_expected[4])
		self.assertEqual(actual.repeat_weekly, item_2_expected[5])

		self.clean_db()

	def test_select_by_date_and_time(self):
		dt = datetime.now()
		item_1_expected = ('Some title 1', dt.date().strftime(EventModel.DATE_FORMAT), (dt + timedelta(minutes=30)).time().strftime(EventModel.TIME_FORMAT), 'Some description 1', 0, 1)
		self.cursor.execute(
			'INSERT INTO Events(title, date, time, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?, ?);',
			item_1_expected
		)
		actual_list = EventModel.select(self.cursor, date=dt.date(), time=(dt + timedelta(minutes=30)).time())
		self.assertEqual(len(actual_list), 1)
		actual = actual_list[0]
		self.assertEqual(actual.id, 1)
		self.assertEqual(actual.title, item_1_expected[0])
		self.assertEqual(actual.date, datetime.strptime(item_1_expected[1], EventModel.DATE_FORMAT).date())
		self.assertEqual(actual.time, datetime.strptime(item_1_expected[2], EventModel.TIME_FORMAT).time())
		self.assertEqual(actual.description, item_1_expected[3])
		self.assertEqual(actual.is_past, item_1_expected[4])
		self.assertEqual(actual.repeat_weekly, item_1_expected[5])

		self.clean_db()
