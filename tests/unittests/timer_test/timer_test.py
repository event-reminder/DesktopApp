import unittest

from app.utils.timer import Timer


class TestStringMethods(unittest.TestCase):

	def timer_method(self):
		self.assertTrue(True)

	def test_timer_start(self):
		timer = Timer(1, self.timer_method)
		timer.start()
		self.assertEqual(timer.is_active(), True)
		timer.wait()
		self.assertEqual(timer.is_active(), False)

	def test_timer_stop(self):
		timer = Timer(1, self.timer_method)
		timer.start()
		self.assertEqual(timer.is_active(), True)
		timer.stop()
		self.assertEqual(timer.is_active(), False)

	def test_timer_restart(self):
		timer = Timer(1, self.timer_method)
		timer.start()
		self.assertEqual(timer.is_active(), True)
		timer.stop()
		self.assertEqual(timer.is_active(), False)
		timer.start()
		self.assertEqual(timer.is_active(), True)
		timer.wait()
		self.assertEqual(timer.is_active(), False)
