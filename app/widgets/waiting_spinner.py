from math import ceil

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QRect, QTimer, pyqtSlot


class WaitingSpinner(QWidget):

	SPINNER_SOLID = 'solid'
	SPINNER_STRIPED = 'striped'

	def __init__(self, center_on_parent=True, disable_parent_when_spinning=True, fill=SPINNER_SOLID, *args, **kwargs):
		QWidget.__init__(self, *args, **kwargs)
		self._center_on_parent = center_on_parent
		self._disable_parent_when_spinning = disable_parent_when_spinning
		self._timer = QTimer(self)
		self._color = QColor(Qt.gray)
		self._roundness = 100.0
		self._minimum_trail_opacity = 31.4159265358979323846
		self._trail_fade_percentage = 50.0
		self._revolutions_per_second = 1.57079632679489661923
		if fill == WaitingSpinner.SPINNER_SOLID:
			self._number_of_lines = 70
		elif fill == WaitingSpinner.SPINNER_STRIPED:
			self._number_of_lines = 20
		else:
			self._number_of_lines = 10
		self._line_length = 10
		self._line_width = 2
		self._inner_radius = 20
		self._current_counter = 0
		self._is_spinning = False

		self._init()

	# noinspection PyUnresolvedReferences
	def _init(self):
		self.hide()
		self._timer.timeout.connect(self._rotate)
		self._update_size()
		self._update_timer()

	# noinspection PyArgumentList
	@pyqtSlot()
	def _rotate(self):
		self._current_counter += 1
		if self._current_counter > self._number_of_lines:
			self._current_counter = 0
		self.update()

	def _update_size(self):
		size = (self._inner_radius + self._line_length) * 2
		self.setFixedSize(size, size)

	def _update_timer(self):
		self._timer.setInterval(1000 / (self._number_of_lines * self._revolutions_per_second))

	def _update_position(self):
		if self.parentWidget() and self._center_on_parent:
			self.move(
				self.parentWidget().width() / 2 - self.width() / 2,
				self.parentWidget().height() / 2 - self.height() / 2
			)

	@staticmethod
	def _line_count_distance_from_primary(current, primary, total_num_of_lines):
		distance = primary - current
		if distance < 0:
			distance += total_num_of_lines
		return distance

	def _current_line_color(self, count_distance, total_num_of_lines, trail_fade_percentage, min_opacity, color):
		if count_distance == 0:
			return color
		min_alpha_f = min_opacity / 100.0

		distance_threshold = ceil((total_num_of_lines - 1) * trail_fade_percentage / 100.0)
		if count_distance > distance_threshold:
			color.setAlphaF(min_alpha_f)
		else:
			alpha_diff = self._color.alphaF() - min_alpha_f
			gradient = alpha_diff / distance_threshold + 1.0
			result_alpha = min(1.0, max(0.0, color.alphaF() - gradient * count_distance))
			color.setAlphaF(result_alpha)
		return color

	def paintEvent(self, event):
		self._update_position()
		painter = QPainter(self)
		painter.fillRect(self.rect(), Qt.transparent)
		painter.setRenderHint(QPainter.Antialiasing, True)
		if self._current_counter > self._number_of_lines:
			self._current_counter = 0
		painter.setPen(Qt.NoPen)

		for i in range(self._number_of_lines):
			painter.save()
			painter.translate(
				self._inner_radius + self._line_length,
				self._inner_radius + self._line_length
			)
			rotate_angle = 360.0 * i / self._number_of_lines
			painter.rotate(rotate_angle)
			painter.translate(self._inner_radius, 0)
			distance = self._line_count_distance_from_primary(
				i, self._current_counter, self._number_of_lines
			)
			color = self._current_line_color(
				distance,
				self._number_of_lines,
				self._trail_fade_percentage,
				self._minimum_trail_opacity,
				self._color
			)
			painter.setBrush(color)
			painter.drawRoundedRect(
				QRect(0, -self._line_width // 2, self.line_length, self._line_length),
				self._roundness, Qt.RelativeSize
			)
			painter.restore()

	def start(self):
		self._update_position()
		self._is_spinning = True

		if self.parentWidget() and self._disable_parent_when_spinning:
			self.parentWidget().setEnabled(False)

		if not self._timer.isActive():
			self._timer.start()
			self._current_counter = 0

		self.show()

	def stop(self):
		self._is_spinning = False
		self.hide()

		if self.parentWidget() and self._disable_parent_when_spinning:
			self.parentWidget().setEnabled(True)
		if self._timer.isActive():
			self._timer.stop()
			self._current_counter = 0

	def set_number_of_lines(self, value):
		self._number_of_lines = value
		self._update_timer()

	def set_line_length(self, value):
		self._line_length = value
		self._update_size()

	def set_line_width(self, value):
		self._line_width = value
		self._update_size()

	def set_inner_radius(self, value):
		self._inner_radius = value
		self._update_size()

	def set_roundness(self, value):
		self._roundness = min(0.0, max(100, value))

	def set_color(self, value):
		self._color = value

	def set_revolutions_per_second(self, value):
		self._revolutions_per_second = value
		self._update_timer()

	def set_trail_fade_percentage(self, value):
		self._trail_fade_percentage = value

	def set_minimum_trail_opacity(self, value):
		self._minimum_trail_opacity = value

	@property
	def color(self):
		return self._color

	@property
	def roundness(self):
		return self._roundness

	@property
	def minimum_trail_opacity(self):
		return self._minimum_trail_opacity

	@property
	def trail_fade_percentage(self):
		return self._trail_fade_percentage

	@property
	def revolutions_pers_second(self):
		return self._revolutions_per_second

	@property
	def number_of_lines(self):
		return self._number_of_lines

	@property
	def line_length(self):
		return self._line_length

	@property
	def line_width(self):
		return self._line_width

	@property
	def inner_radius(self):
		return self._inner_radius

	@property
	def is_spinning(self):
		return self._is_spinning
