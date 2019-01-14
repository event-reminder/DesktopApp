from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QListWidget,
	QVBoxLayout,
	QScrollArea,
	QHBoxLayout,
	QListWidgetItem
)

from app.ui.utils.creator import new_button
from app.ui.widgets.event_widget import EventWidget


class EventsListForm:

	def __init__(self, parent):
		self.parent = parent
		self.parent.setFixedSize(500, 400)
		self.list_view = QListWidget()
		self.calendar = None
		self.setup_ui()

	def setup_ui(self):
		content = QVBoxLayout()
		scroll_view = QScrollArea()
		scroll_view.setWidget(self.list_view)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedHeight(300)
		content.addWidget(scroll_view)
		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		btn_new_event = new_button('New', 100, 50, self.handle_create_event)
		buttons.addWidget(btn_new_event, 0, Qt.AlignRight)
		btn_close = new_button('Close', 100, 50, self.close_btn_click)
		buttons.addWidget(btn_close, 0, Qt.AlignRight)
		content.addLayout(buttons)
		self.parent.setLayout(content)

	def set_calendar_widget(self, calendar):
		self.calendar = calendar

	def handle_create_event(self):
		self.list_view.clear()
		self.parent.close()
		self.calendar.create_event()

	def update_day(self, clear_list=False):
		self.calendar.update()
		if clear_list:
			self.list_view.clear()
			self.parent.close()

	def append_event_item(self, data_item):
		item = EventWidget(self.list_view, self.update_day)
		item.set_data(data_item.id, data_item.title, data_item.time, data_item.date)
		if len(data_item.description) > 0:
			item.setToolTip(self.get_tool_tip(data_item.description))
		list_widget_item = QListWidgetItem(self.list_view)
		list_widget_item.setSizeHint(item.sizeHint())
		self.list_view.addItem(list_widget_item)
		self.list_view.setItemWidget(list_widget_item, item)

	def set_data(self, data, date):
		self.list_view.clear()
		self.parent.setWindowTitle('Events for {}'.format(date))
		if data is not None:
			for data_item in data:
				self.append_event_item(data_item)

	@staticmethod
	def get_tool_tip(description):
		split_str = description.split()
		result = 'Description:\n\n'
		for i in range(len(split_str)):
			if i % 10 == 0 and i != 0:
				result += '\n'
			result += split_str[i] + ' '
		return result

	def close_btn_click(self):
		self.list_view.clear()
		self.parent.close()
