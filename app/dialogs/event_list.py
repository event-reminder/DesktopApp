from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QHBoxLayout

from app.widgets.util import PushButton
from app.widgets.event_list_widget import EventListWidget


class EventsListDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))
		self.setFixedSize(500, 400)
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

		self.calendar = kwargs.get('calendar', None)
		if self.calendar is None:
			raise RuntimeError('EventsListDialog: calendar is not set')

		self.list_widget = EventListWidget(**{
			'parent': self,
			'update_dialog': self.calendar.event_creation_dialog
		})

		self.setup_ui()

	def closeEvent(self, event):
		self.list_widget.clear()
		super(EventsListDialog, self).closeEvent(event)

	def setup_ui(self):
		content = QVBoxLayout()
		scroll_view = QScrollArea()
		scroll_view.setWidget(self.list_widget)
		scroll_view.setWidgetResizable(True)
		scroll_view.setFixedHeight(300)
		content.addWidget(scroll_view)
		buttons = QHBoxLayout()
		buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		btn_new_event = PushButton('New', 90, 30, self.create_event_click)
		buttons.addWidget(btn_new_event, 0, Qt.AlignRight)
		btn_close = PushButton('Close', 90, 30, self.close)
		buttons.addWidget(btn_close, 0, Qt.AlignRight)
		content.addLayout(buttons)
		self.setLayout(content)

	def create_event_click(self):
		self.close()
		self.calendar.open_create_event()

	def set_data(self, data, date):
		self.setWindowTitle('Events for {}'.format(date))
		self.list_widget.set_data(data)
