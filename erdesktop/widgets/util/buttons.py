from PyQt5.QtWidgets import QPushButton


# noinspection PyUnresolvedReferences
class PushButton(QPushButton):

	def __init__(self, title, width, height, function, *__args):
		super().__init__(*__args)
		self.setText(title)
		self.setFixedWidth(width)
		self.setFixedHeight(height)
		self.clicked.connect(function)
