from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QSizePolicy, QAbstractItemView

from erdesktop.widgets.event_widget import EventWidget


class EventListWidget(QListWidget):

	def __init__(self, **kwargs):
		super(EventListWidget, self).__init__()

		self.setContentsMargins(0, 0, 0, 0)

		self.parent = kwargs.get('parent', None)
		if self.parent is None:
			raise RuntimeError('EventListWidget: parent is not set')

		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.verticalScrollBar().setPageStep(1)
		self.verticalScrollBar().setRange(0, 100)

		self.set_empty()

	@property
	def selected_item(self):
		if len(self.selectedItems()) > 0:
			return self.itemWidget(self.selectedItems()[0]).event_data
		return None

	def selected_ids(self):
		return [self.itemWidget(x).event_data.id for x in self.selectedItems()]

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
		self.setCurrentRow(0)

	def set_empty(self):
		self.clear()
		lbl = QLabel(self.tr('No events'))
		lbl.setAlignment(Qt.AlignCenter)
		lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		lbl.setStyleSheet('color: gray;')
		lbl.setFont(QFont('18'))
		lbl.setContentsMargins(0, 10, 0, 0)

		lbl_item = QListWidgetItem(self)
		lbl_item.setFlags(Qt.NoItemFlags)
		lbl_item.setSizeHint(lbl.sizeHint())

		self.setItemWidget(lbl_item, lbl)
