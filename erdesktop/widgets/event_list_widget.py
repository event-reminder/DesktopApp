from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from erdesktop.widgets.event_widget import EventWidget


class EventListWidget(QListWidget):

	def __init__(self, **kwargs):
		super(EventListWidget, self).__init__()

		self.parent = kwargs.get('parent', None)
		if self.parent is None:
			raise RuntimeError('EventListWidget: parent is not set')

		self.mouse_button = None

		# noinspection PyUnresolvedReferences
		self.itemClicked.connect(self.item_clicked)

		self.update_dialog = kwargs.get('update_dialog', None)
		if self.update_dialog is None:
			raise RuntimeError('EventListWidget: update dialog is not set')

	def mousePressEvent(self, event):
		self.mouse_button = event.button()
		super(EventListWidget, self).mousePressEvent(event)

	def item_clicked(self, item):
		if self.mouse_button == Qt.LeftButton:
			self.update_dialog.reset_inputs(event_data=self.itemWidget(item).event_data)
			self.parent.close()
			self.update_dialog.exec_()

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
