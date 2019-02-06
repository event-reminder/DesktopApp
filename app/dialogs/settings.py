from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.settings import (
	Settings,
	FONT_LARGE,
	FONT_SMALL,
	FONT_NORMAL
)


# noinspection PyArgumentList,PyUnresolvedReferences
class SettingsDialog(QDialog):

	def __init__(self, flags, *args, **kwargs):
		super().__init__(flags=flags, *args)

		if 'palette' in kwargs:
			self.setPalette(kwargs.get('palette'))
		if 'font' in kwargs:
			self.setFont(kwargs.get('font'))

		self.calendar = kwargs['calendar']

		self.setFixedSize(550, 400)
		self.setWindowTitle('Settings')
		self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

		self.settings = Settings()

		self.opacity_enter_slider = QSlider(Qt.Horizontal)
		self.opacity_leave_slider = QSlider(Qt.Horizontal)
		self.always_on_top_check_box = QCheckBox()
		self.opacity_enter_label = QLabel('Window opacity enter    {}%'.format(
			str(float(self.settings.mouse_enter_opacity) * 100)
		))
		self.opacity_leave_label = QLabel('Window opacity leave    {}%'.format(
			str(float(self.settings.mouse_leave_opacity) * 100)
		))
		self.font_combo_box = QComboBox()
		self.show_calendar_on_startup_check_box = QCheckBox()
		self.theme_combo_box = QComboBox()

		self.remove_after_time_up_check_box = QCheckBox()
		self.notification_duration_input = QLineEdit()
		self.remind_time_before_event_input = QLineEdit()

		self.ui_is_loaded = False
		self.setup_ui()
		self.ui_is_loaded = True

	def setup_ui(self):
		content = QVBoxLayout()
		settings_general_tabs = QTabWidget(self)
		settings_general_tabs.setMinimumWidth(self.width() - 22)
		self.setup_app_settings_ui(settings_general_tabs)
		self.setup_events_settings_ui(settings_general_tabs)
		content.addWidget(settings_general_tabs, alignment=Qt.AlignLeft)
		self.setLayout(content)

	def setup_app_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(50, 10, 50, 10)
		layout.setSpacing(20)

		layout.addWidget(QLabel('Theme'), 0, 0)
		self.theme_combo_box.currentIndexChanged.connect(self.theme_changed)
		self.theme_combo_box.addItems(['Light', 'Dark'])
		self.theme_combo_box.setCurrentIndex(1 if self.settings.is_dark_theme else 0)
		layout.addWidget(self.theme_combo_box, 0, 1)

		layout.addWidget(QLabel('Font'), 1, 0)
		self.font_combo_box.currentIndexChanged.connect(self.font_changed)
		self.font_combo_box.addItems(['Small', 'Normal', 'Large'])
		curr_idx = 0
		if self.settings.app_font == FONT_NORMAL:
			curr_idx = 1
		elif self.settings.app_font == FONT_LARGE:
			curr_idx = 2
		self.font_combo_box.setCurrentIndex(curr_idx)
		layout.addWidget(self.font_combo_box, 1, 1)

		layout.addWidget(QLabel('Show calendar on startup'), 2, 0)
		self.show_calendar_on_startup_check_box.stateChanged.connect(self.show_calendar_on_startup_changed)
		self.show_calendar_on_startup_check_box.setChecked(self.settings.show_calendar_on_startup)
		layout.addWidget(self.show_calendar_on_startup_check_box, 2, 1)

		layout.addWidget(QLabel('Always on top (need restart)'), 3, 0)
		self.always_on_top_check_box.stateChanged.connect(self.always_on_top_changed)
		self.always_on_top_check_box.setChecked(self.settings.is_always_on_top)
		layout.addWidget(self.always_on_top_check_box, 3, 1)

		layout.addWidget(self.opacity_enter_label, 4, 0)
		self.opacity_enter_slider.setFocusPolicy(Qt.StrongFocus)
		self.opacity_enter_slider.setTickPosition(QSlider.TicksBothSides)
		self.opacity_enter_slider.setMinimum(0)
		self.opacity_enter_slider.setMaximum(10)
		self.opacity_enter_slider.setSingleStep(1)
		self.opacity_enter_slider.valueChanged.connect(self.opacity_enter_changed)
		self.opacity_enter_slider.setValue(float(self.settings.mouse_enter_opacity) * 10)
		layout.addWidget(self.opacity_enter_slider, 4, 1)

		layout.addWidget(self.opacity_leave_label, 5, 0)
		self.opacity_leave_slider.setFocusPolicy(Qt.StrongFocus)
		self.opacity_leave_slider.setTickPosition(QSlider.TicksBothSides)
		self.opacity_leave_slider.setMinimum(0)
		self.opacity_leave_slider.setMaximum(10)
		self.opacity_leave_slider.setSingleStep(1)
		self.opacity_leave_slider.valueChanged.connect(self.opacity_leave_changed)
		self.opacity_leave_slider.setValue(float(self.settings.mouse_leave_opacity) * 10)
		layout.addWidget(self.opacity_leave_slider, 5, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, 'App')

	def setup_events_settings_ui(self, tabs):
		tab = QWidget(flags=tabs.windowFlags())

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(50, 30, 50, 10)
		layout.setSpacing(20)

		layout.addWidget(QLabel('Remove event after time is up'), 0,  0)
		self.remove_after_time_up_check_box.stateChanged.connect(self.remove_after_time_up_changed)
		self.remove_after_time_up_check_box.setChecked(self.settings.remove_event_after_time_up)
		layout.addWidget(self.remove_after_time_up_check_box, 0, 1)

		layout.addWidget(QLabel('Notification duration (sec)'), 1, 0)
		self.notification_duration_input.setValidator(QIntValidator())
		self.notification_duration_input.setText(str(self.settings.notification_duration))
		self.notification_duration_input.textChanged.connect(self.notification_duration_changed)
		layout.addWidget(self.notification_duration_input, 1, 1)

		layout.addWidget(QLabel('Notify before event (min)'), 2, 0)
		self.remind_time_before_event_input.setValidator(QIntValidator())
		self.remind_time_before_event_input.setText(str(self.settings.remind_time_before_event))
		self.remind_time_before_event_input.textChanged.connect(self.remind_time_before_event_changed)
		layout.addWidget(self.remind_time_before_event_input, 2, 1)

		tab.setLayout(layout)
		tabs.addTab(tab, 'Events')

	def opacity_enter_changed(self):
		if self.ui_is_loaded:
			self.settings.set_mouse_enter_opacity(float(self.opacity_enter_slider.value()) / 10)
			self.opacity_enter_label.setText('Window opacity enter    {}%'.format(
				int(self.opacity_enter_slider.value()) * 10)
			)

	def opacity_leave_changed(self):
		if self.ui_is_loaded:
			self.settings.set_mouse_leave_opacity(float(self.opacity_leave_slider.value()) / 10)
			self.opacity_leave_label.setText('Window opacity leave    {}%'.format(
				int(self.opacity_leave_slider.value()) * 10)
			)

	def always_on_top_changed(self):
		if self.ui_is_loaded:
			self.settings.set_is_always_on_top(self.always_on_top_check_box.isChecked())

	def font_changed(self, current):
		if self.ui_is_loaded:
			new_font = FONT_SMALL
			if current == 1:
				new_font = FONT_NORMAL
			elif current == 2:
				new_font = FONT_LARGE
			font = QFont('SansSerif', new_font)

			self.calendar.setFont(font)
			self.calendar.parent.setFont(font)
			for dialog in self.calendar.dialogs:
				dialog.setFont(font)
			self.settings.set_font(new_font)

	def show_calendar_on_startup_changed(self):
		if self.ui_is_loaded:
			self.settings.set_show_calendar_on_startup(self.show_calendar_on_startup_check_box.isChecked())

	def theme_changed(self, current):
		if self.ui_is_loaded:
			self.settings.set_theme(current == 1)
			self.calendar.setPalette(self.settings.app_theme)
			self.calendar.parent.setPalette(self.settings.app_theme)
			for dialog in self.calendar.dialogs:
				dialog.setPalette(self.settings.app_theme)

	def remove_after_time_up_changed(self):
		self.settings.set_remove_event_after_time_up(self.remove_after_time_up_check_box.isChecked())

	def notification_duration_changed(self):
		text = self.notification_duration_input.text()
		if len(text) > 0:
			self.settings.set_notification_duration(int(text))

	def remind_time_before_event_changed(self):
		text = self.remind_time_before_event_input.text()
		if len(text) > 0:
			self.settings.set_remind_time_before_event(int(text))

	def save_btn_click(self):
		self.close()
