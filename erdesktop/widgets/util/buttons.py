from PyQt5.QtWidgets import QPushButton


class PushButton(QPushButton):

	def __init__(self, title, width, height, function, *__args):
		super().__init__(*__args)
		self.setText(title)
		self.setFixedWidth(width)
		self.setFixedHeight(height)

		# noinspection PyUnresolvedReferences
		self.clicked.connect(function)
