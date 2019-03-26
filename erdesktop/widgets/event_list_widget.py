from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QSizePolicy

from erdesktop.widgets.event_widget import EventWidget


class EventListWidget(QListWidget):

	def __init__(self, **kwargs):
		super(EventListWidget, self).__init__()

		self.setContentsMargins(0, 0, 0, 0)

		self.parent = kwargs.get('parent', None)
		if self.parent is None:
			raise RuntimeError('EventListWidget: parent is not set')

		self.selected_item = None

		# noinspection PyUnresolvedReferences
		self.itemClicked.connect(self.item_clicked)

	def item_clicked(self, item):
		self.selected_item = self.itemWidget(item).event_data

	def append_event_item(self, event_item):
		item = EventWidget(self, event_item)
		list_item = QListWidgetItem(self)
		list_item.setSizeHint(item.sizeHint())
		self.setItemWidget(list_item, item)

	def set_data(self, data):
		self.clear()
		if data is not None:
			for data_item in data:
				self.append_event_item(data_item)

	def set_empty(self):
		self.clear()
		lbl = QLabel('No events')
		lbl.setAlignment(Qt.AlignCenter)
		lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		lbl.setStyleSheet('color: gray;')
		lbl.setFont(QFont('18'))
		lbl.setContentsMargins(0, 10, 0, 0)

		lbl_item = QListWidgetItem(self)
		lbl_item.setFlags(Qt.NoItemFlags)
		lbl_item.setSizeHint(lbl.sizeHint())

		self.setItemWidget(lbl_item, lbl)
