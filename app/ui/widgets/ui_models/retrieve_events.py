from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui.utils import popup
from app.ui.utils.creator import new_button


class EventWidget(QWidget):
	def __init__(self, delete_handler, parent: QListWidget):
		super(EventWidget, self).__init__(parent)
		self.titleLabel = QLabel()
		self.timeLabel = QLabel()
		self.parent = parent
		self.setLayout(self.get_content())
		self.id = -1
		self.delete_handler = delete_handler

	def get_content(self):
		layout = QVBoxLayout()
		layout.addWidget(self.timeLabel)
		layout.addWidget(self.titleLabel)
		return layout

	def set_data(self, pk, title, time):
		self.timeLabel.setText('Event #{} at {}'.format(pk, time[:5]))
		self.titleLabel.setText(title)
		self.id = pk

	def contextMenuEvent(self, event):
		menu = QMenu(self)
		delete_action = menu.addAction('Delete')
		action = menu.exec_(self.mapToGlobal(event.pos()))
		if action == delete_action:
			ret_action = popup.question(self.parent, 'Deleting an event', 'Do you really want to delete the event?')
			if ret_action == QMessageBox.Yes:
				self.delete_handler(self.id)
				self.parent.takeItem(self.parent.currentRow())


class RetrieveEventsDialogUI:

	def __init__(self, parent, delete_events_handler):
		self.delete_events_handler = delete_events_handler
		self.parent = parent
		self.parent.setFixedSize(500, 400)
		self.list_view = QListWidget()
		self.parent.setLayout(self.get_content())

	def get_content(self):
		content = QVBoxLayout()
		scroll_view = QScrollArea()
		scroll_view.setWidget(self.list_view)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedHeight(300)
		content.addWidget(scroll_view)
		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		btn_close = new_button('Close', 100, 50, self.close_btn_click)
		buttons.addWidget(btn_close, 0, Qt.AlignRight)
		content.addLayout(buttons)
		return content

	def append_event_item(self, data_item):
		item = EventWidget(self.delete_events_handler, self.list_view)
		item.set_data(data_item.id, data_item.title, data_item.time)
		item.setToolTip(self.get_tool_tip(data_item.description))
		list_widget_item = QListWidgetItem(self.list_view)
		list_widget_item.setSizeHint(item.sizeHint())
		self.list_view.addItem(list_widget_item)
		self.list_view.setItemWidget(list_widget_item, item)

	def set_data(self, data, date):
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
		self.parent.close()
		self.list_view.clear()
