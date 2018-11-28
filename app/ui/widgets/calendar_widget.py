from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils import popup


class CalendarWidget(QCalendarWidget):

	def __init__(self, parent, width, height):
		super().__init__()
		self.parent = parent
		self.setGeometry(0, 0, width, height)
		self.setGridVisible(True)
		events = self.get_click_events()
		for event in events:
			self.clicked[event['item']].connect(event['handler'])

	def get_click_events(self):
		return [
			{
				'item': QDate,
				'handler': self.show_date
			}
		]

	def resize_handler(self):
		self.resize(self.parent.width(), self.parent.height())

	def show_date(self, date):
		popup.question(self, 'Current Date', date.toString())
