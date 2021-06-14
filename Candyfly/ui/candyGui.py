import os

from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QDir, QUrl
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QPolygonF
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QWidget, QMainWindow, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsPolygonItem, QFileSystemModel, QAbstractItemView

from ui.Ui_candy import Ui_MainWindow
from ui.rangeslider import QRangeSlider

BG_COL = Qt.black
FG_COL = Qt.lightGray
FG_COL_2 = Qt.darkGray
ON_COL = Qt.darkGreen

FG_PEN = QPen(FG_COL)
BG_PEN = QPen(BG_COL)
ON_PEN = QPen(Qt.green)
OFF_PEN = QPen(Qt.red)

FG_BRUSH = QBrush(FG_COL)
ON_BRUSH = QBrush(Qt.green)
PROGRESS_BRUSH = QBrush(Qt.yellow)
OFF_BRUSH = QBrush(Qt.red)
SEL_BRUSH = QColor(169, 49, 178)

HANDLE_BRUSH = QBrush(FG_COL)
VAL_BRUSH = QBrush(Qt.darkGreen)

ACTIVE_COL = QColor(Qt.green)
ACTIVE_COL.setAlphaF(0.6)
ACTIVE_BRUSH = QBrush(ACTIVE_COL)
IDLE_COL = QColor(FG_COL)
IDLE_COL.setAlphaF(0.6)
IDLE_BRUSH = QBrush(IDLE_COL)

gauge_danger = "QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: #000000;} " \
               "QProgressBar::chunk { background-color: red; width: 20px; } "
gauge_warning = "QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: #000000;} " \
                "QProgressBar::chunk { background-color: orange; width: 20px; } "
gauge_safe = "QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: #000000;} " \
             "QProgressBar::chunk { background-color: green; width: 20px; } "

TAKEOFF_BUTTON_STYLE_SHEET = "background-color: green; border-style: outset; border-width: 1px; border-radius: 2px; " \
                             "color:lightGray ;border-color: beige; min-width:120px; min-height:60px;"

LAND_BUTTON_STYLE_SHEET = "background-color: red; border-style: outset; border-width: 1px; border-radius: 2px; " \
                          "color:lightGray ;border-color: beige; min-width:120px; min-height:60px;"

STATUS_OFF_STYLE = "border-radius:10px; background: red; color: #4A0C46;border: 1px solid black; min-height: " \
                   "20px;max-height: 20px;min-width: 20px;max-width: 20px; "
STATUS_PROGRESS_STYLE = "border-radius:10px; background: orange; color: #4A0C46;border: 1px solid black; min-height: " \
                        "20px;max-height: 20px;min-width: 20px;max-width: 20px; "
STATUS_ON_STYLE = "border-radius:10px; background: green; color: #4A0C46;border: 1px solid black; min-height: " \
                  "20px;max-height: 20px;min-width: 20px;max-width: 20px; "


class VerticalAxis(QGraphicsPolygonItem):
    def __init__(self, _icon_top_file, _icon_bottom_file, _win):
        super().__init__()

        self.index = 0
        self.active = False
        self.win = _win

        width = 80
        self.width = width
        height = 250
        self.height = height
        height_ratio = 8
        width_ratio = 4

        points = [QPointF(width / 2, 0), QPointF(width, height / height_ratio),
                  QPointF((width_ratio - 1) * width / width_ratio, height / height_ratio),
                  QPointF((width_ratio - 1) * width / width_ratio, (height_ratio - 1) * height / height_ratio),
                  QPointF(width, (height_ratio - 1) * height / height_ratio), QPointF(width / 2, height),
                  QPointF(0, (height_ratio - 1) * height / height_ratio),
                  QPointF(width / width_ratio, (height_ratio - 1) * height / height_ratio),
                  QPointF(width / width_ratio, height / height_ratio),
                  QPointF(0, height / height_ratio), QPointF(width / 2, 0)
                  ]
        needle = QPolygonF(points)
        self.setPolygon(needle)
        self.setBrush(IDLE_BRUSH)
        self.setPen(ON_PEN)

        self.value_point = QGraphicsEllipseItem(width / 2 - 5, height / 2 - 5, 10, 10)
        self.value_point.setPen(BG_PEN)
        self.value_point.setBrush(FG_COL)
        self.value_point.setParentItem(self)
        self.value_point.setZValue(10)

        self.value_point_raw = QGraphicsEllipseItem(width / 2 - 3, height / 2 - 3, 6, 6)
        self.value_point_raw.setPen(BG_PEN)
        self.value_point_raw.setBrush(FG_COL_2)
        self.value_point_raw.setParentItem(self)
        self.value_point_raw.setZValue(9)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_top_path = script_dir + os.path.sep + "img" + os.path.sep + _icon_top_file
        icon_bottom_path = script_dir + os.path.sep + "img" + os.path.sep + _icon_bottom_file
        self.top = QGraphicsPixmapItem(self)
        self.top.setPixmap(QPixmap(icon_top_path))
        self.top.setPos(width / 2 - 8, -18)
        self.top.setScale(0.5)
        self.top.setOpacity(0.5)
        self.bottom = QGraphicsPixmapItem(self)
        self.bottom.setPixmap(QPixmap(icon_bottom_path))
        self.bottom.setPos(width / 2 - 8, height + 2)
        self.bottom.setScale(0.5)
        self.bottom.setOpacity(0.5)

    def set_active(self, is_active):
        self.active = is_active
        self.update_active()

    def update_active(self):
        if self.active:
            self.setBrush(ACTIVE_BRUSH)
        else:
            self.setBrush(IDLE_BRUSH)

    def is_active(self):
        return self.active

    def mousePressEvent(self, event):
        self.active = not self.active
        self.win.update_activated_axis()
        self.update_active()

    def display(self, value):
        _x = self.width / 2 - 5
        h = self.height

        _y = (1 - value) * h / 2
        # scale input between 1 and -1 between 0 (1) and height
        self.value_point.setRect(_x, _y - 5, 10, 10)

    def display_raw(self, value):
        _x = self.width / 2 - 3
        h = self.height

        _y = (1 - value) * h / 2
        # scale input between 1 and -1 between 0 (1) and height
        self.value_point_raw.setRect(_x, _y - 3, 6, 6)


class RectSelector(QGraphicsRectItem):
    def __init__(self, _axis1, _axis2, _win):
        super().__init__(0, 0, 40, 40)
        self.setBrush(Qt.transparent)
        self.setPen(FG_PEN)
        self.axis1 = _axis1
        self.axis2 = _axis2
        self.setZValue(8)
        self.win = _win

    def mousePressEvent(self, event):
        active = True
        if (self.axis1 and self.axis2 and (self.axis1.is_active() or self.axis2.is_active())):
            # if any is active then switch off both
            active = False
        if self.axis1:
            self.axis1.set_active(active)
        if self.axis2:
            self.axis2.set_active(active)
        self.win.update_activated_axis()

    def set_axis(self, _axis1, _axis2):
        self.axis1 = _axis1
        self.axis2 = _axis2


class SoundPlayer():
    def __init__(self):
        super().__init__()
        self.right = QSoundEffect()
        self.right.setSource(QUrl.fromLocalFile('./sounds/right.wav'))
        self.right.setLoopCount(QSoundEffect.Infinite)
        self.left = QSoundEffect()
        self.left.setSource(QUrl.fromLocalFile('./sounds/left.wav'))
        self.left.setLoopCount(QSoundEffect.Infinite)
        self.up = QSoundEffect()
        self.up.setSource(QUrl.fromLocalFile('./sounds/up.wav'))
        self.up.setLoopCount(QSoundEffect.Infinite)
        self.down = QSoundEffect()
        self.down.setSource(QUrl.fromLocalFile('./sounds/down.wav'))
        self.down.setLoopCount(QSoundEffect.Infinite)
        self.front = QSoundEffect()
        self.front.setSource(QUrl.fromLocalFile('./sounds/front.wav'))
        self.front.setLoopCount(QSoundEffect.Infinite)
        self.back = QSoundEffect()
        self.back.setSource(QUrl.fromLocalFile('./sounds/back.wav'))
        self.back.setLoopCount(QSoundEffect.Infinite)
        self.clock = QSoundEffect()
        self.clock.setSource(QUrl.fromLocalFile('./sounds/clock.wav'))
        self.clock.setLoopCount(QSoundEffect.Infinite)
        self.a_clock = QSoundEffect()
        self.a_clock.setSource(QUrl.fromLocalFile('./sounds/a_clock.wav'))
        self.a_clock.setLoopCount(QSoundEffect.Infinite)

        self.right.setVolume(0)
        self.left.setVolume(0)
        self.up.setVolume(0)
        self.down.setVolume(0)
        self.front.setVolume(0)
        self.back.setVolume(0)
        self.clock.setVolume(0)
        self.a_clock.setVolume(0)

        self.right.play()
        self.left.play()
        self.up.play()
        self.down.play()
        self.front.play()
        self.back.play()
        self.clock.play()
        self.a_clock.play()

    def update(self, _up, _rotate, _front, _right):
        if _up >= 0:
            self.up.setVolume(_up)
            self.down.setVolume(0)
        elif _up <= 0:
            self.up.setVolume(0)
            self.down.setVolume(-_up)

        if _right >= 0:
            self.right.setVolume(_right)
            self.left.setVolume(0)
        elif _right <= 0:
            self.left.setVolume(-_right)
            self.right.setVolume(0)

        if _rotate >= 0:
            self.clock.setVolume(_rotate)
            self.a_clock.setVolume(0)
        elif _up <= 0:
            self.clock.setVolume(0)
            self.a_clock.setVolume(-_rotate)

        if _front >= 0:
            self.front.setVolume(_front)
            self.back.setVolume(0)
        elif _right <= 0:
            self.back.setVolume(-_front)
            self.front.setVolume(0)

        #print("sounds", self.right.volume(), self.left.volume(), self.up.volume(), self.down.volume())

class CandyWinForm(QMainWindow):
@    refreshDroneAsked = pyqtSignal()
    refreshArduinoAsked = pyqtSignal()
    refreshRiotAsked = pyqtSignal()

    verticalSpeedValueChanged = pyqtSignal(float)
    horizontalSpeedValueChanged = pyqtSignal(float)
    rotationSpeedValueChanged = pyqtSignal(int)

    axesChanged = pyqtSignal(list)

    presetChanged = pyqtSignal(str)
    saveAsked = pyqtSignal()

    closing = pyqtSignal()
    discrete_threshold_changed = pyqtSignal(int)
    discrete_duration_changed = pyqtSignal(int)
    control_changed = pyqtSignal(str)
    drone_changed = pyqtSignal(str)

    calibrationChanged = pyqtSignal()

    ask_take_off = pyqtSignal()
    ask_land = pyqtSignal()

    def __init__(self):
        super().__init__()

        # create the form
        self.ui = Ui_MainWindow()
        widget = QWidget()
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)

        # create the scene and add it to the tabs
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(BG_COL)

        self.view = self.ui.graphicsView

        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.scale(1.2, 1.2)

        # set up the central scene with axis
        self.z_axis = VerticalAxis("up.png", "down.png", self)
        self.rotation_axis = VerticalAxis("clock.png", "anticlock.png", self)
        self.rotation_axis.setRotation(90)
        self.axis1_rect = RectSelector(self.z_axis, self.rotation_axis, self)

        self.front_axis = VerticalAxis("front.png", "back.png", self)
        self.right_axis = VerticalAxis("front.png", "back.png", self)
        self.right_axis.setRotation(90)
        self.axis2_rect = RectSelector(self.front_axis, self.right_axis, self)

        self.scene.addItem(self.z_axis)
        self.scene.addItem(self.rotation_axis)
        self.scene.addItem(self.axis1_rect)

        self.scene.addItem(self.front_axis)
        self.scene.addItem(self.right_axis)
        self.scene.addItem(self.axis2_rect)

        self.ui.simple_mode.stateChanged.connect(self.set_simplified)
        self.set_simplified(False)

        # set up the calibration widgets
        self.range_keys = ["up", "down", "clock", "anticlock", "front", "back", 'right', 'left']
        self.range_sliders = {}

        for key in self.range_keys:
            _min = 0
            _max = 100
            _start = 5
            _end = 95
            rs = QRangeSlider()
            rs.setMin(_min)
            rs.setMax(_max)
            rs.setRange(_start, _end)
            rs.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
            rs.handle.setStyleSheet(
                'background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')

            rs.endValueChanged.connect(self.calibrationChanged)
            rs.startValueChanged.connect(self.calibrationChanged)
            self.range_sliders[key] = rs

        self.ui.top_down_layout.addWidget(self.range_sliders['up'])
        self.ui.top_down_layout.addWidget(self.range_sliders['down'])
        self.ui.clock_anticlock_layout.addWidget(self.range_sliders['clock'])
        self.ui.clock_anticlock_layout.addWidget(self.range_sliders['anticlock'])
        self.ui.front_back_layout.addWidget(self.range_sliders['front'])
        self.ui.front_back_layout.addWidget(self.range_sliders['back'])
        self.ui.right_left_layout.addWidget(self.range_sliders['right'])
        self.ui.right_left_layout.addWidget(self.range_sliders['left'])

        # handle presets
        self.current_preset = None
        self.presets_path = ""
        self.file_model = QFileSystemModel(self)

        self.ui.save_as_btn.clicked.connect(self.saveAsked)

        # add bindings to values
        self.ui.discrete_treshold_sld.valueChanged.connect(self.discrete_threshold_changed)
        self.ui.discrete_treshold_spin.valueChanged.connect(self.discrete_threshold_changed)

        self.ui.drone_refresh_btn.clicked.connect(lambda: self.ui.take_off_btn.setEnabled(True))
        self.ui.drone_refresh_btn.clicked.connect(self.refreshDroneAsked.emit)

        self.ui.arduino_refresh_btn.clicked.connect(self.refreshArduinoAsked.emit)

        self.ui.control_group.buttonClicked.connect(lambda button: self.control_changed.emit(button.text()))
        self.ui.drone_group.buttonClicked.connect(lambda button: self.drone_changed.emit(button.text()))

        # process speed sliders (handle double values)
        self.ui.vert_speed_spin.valueChanged.connect(self.verticalSpeedValueChanged)
        self.ui.horiz_speed_spin.valueChanged.connect(self.horizontalSpeedValueChanged)
        self.ui.rot_speed_spin.valueChanged.connect(self.rotationSpeedValueChanged)

        self.ui.vert_speed_spin.valueChanged.connect(lambda val: self.ui.vert_speed_sld.setValue(val * 100))
        self.ui.vert_speed_sld.valueChanged.connect(lambda val: self.ui.vert_speed_spin.setValue(val / 100))
        self.ui.horiz_speed_spin.valueChanged.connect(lambda val: self.ui.horiz_speed_sld.setValue(val * 100))
        self.ui.horiz_speed_sld.valueChanged.connect(lambda val: self.ui.horiz_speed_spin.setValue(val / 100))
        self.ui.rot_speed_spin.valueChanged.connect(self.ui.rot_speed_sld.setValue)
        self.ui.rot_speed_sld.valueChanged.connect(self.ui.rot_speed_spin.setValue)
        self.ui.take_off_btn.clicked.connect(lambda: self.ask_take_off.emit())
        self.ui.land_btn.clicked.connect(lambda: self.ask_land.emit())
        self.sndPlayer = SoundPlayer()

    def display_processed_inputs(self, _up, _rotate, _front, _right):
        self.z_axis.display(_up)
        self.rotation_axis.display(_rotate)
        self.front_axis.display(_front)
        self.right_axis.display(_right)
        self.sndPlayer.update(_up, _rotate, _front, _right)

    def display_raw_inputs(self, _up, _rotate, _front, _right):
        self.z_axis.display_raw(_up)
        self.rotation_axis.display_raw(_rotate)
        self.front_axis.display_raw(_front)
        self.right_axis.display_raw(_right)

    def set_simplified(self, is_simplified):
        if is_simplified:
            self.front_axis.set_active(False)
            self.rotation_axis.set_active(False)
            self.rotation_axis.hide()
            self.front_axis.hide()
            self.axis2_rect.hide()

            self.z_axis.show()
            self.z_axis.setPos(270, 50)
            self.right_axis.show()
            self.right_axis.setPos(435, 135)
            self.axis1_rect.show()
            self.axis1_rect.setPos(290, 155)
            self.axis1_rect.set_axis(self.z_axis, self.right_axis)
        else:
            # axis 1
            self.z_axis.show()
            self.z_axis.setPos(110, 50)
            self.rotation_axis.show()
            self.rotation_axis.setPos(275, 135)
            self.axis1_rect.show()
            self.axis1_rect.setPos(130, 155)
            self.axis1_rect.set_axis(self.z_axis, self.rotation_axis)

            # axis 2
            self.front_axis.show()
            self.front_axis.setPos(410, 50)
            self.right_axis.show()
            self.right_axis.setPos(575, 135)
            self.axis2_rect.show()
            self.axis2_rect.setPos(430, 155)

    def get_calibration(self):
        res = {}
        for key in self.range_keys:
            slider = self.range_sliders[key]
            res[key] = [slider.start() / 100, slider.end() / 100]
        return res

    def set_calibration(self, calibration_list):
        for key in self.range_keys:
            slider = self.range_sliders[key]
            if key in calibration_list:
                values = calibration_list[key]
                slider.setStart_silent(values[0] * 100)
                slider.setEnd_silent(values[1] * 100)
            else:
                slider.setStart_silent(5)
                slider.setEnd_silent(95)
        self.calibrationChanged.emit()

    def update_battery_level(self, battery_val):
        max = 4.3
        mid = 3.6
        min = 3.1

        percentage = (battery_val / max) * 100
        self.ui.drone_battery_gauge.setValue(int(percentage))

        style = gauge_danger
        if battery_val > mid:
            style = gauge_safe
        elif battery_val > min:
            style = gauge_warning
        self.ui.drone_battery_gauge.setStyleSheet(style)
        self.ui.drone_battery_gauge.setFormat("{:.2f}".format(battery_val) + "v (%p%)")

    def update_drone_connection(self, connection_status):
        if connection_status == "on":
            self.ui.drone_status_lbl.setStyleSheet(STATUS_ON_STYLE)
        elif connection_status == "progress":
            self.ui.drone_status_lbl.setStyleSheet(STATUS_PROGRESS_STYLE)
        else:
            self.ui.drone_status_lbl.setStyleSheet(STATUS_OFF_STYLE)

        if connection_status != "on":
            self.update_battery_level(0)

    def update_arduino_connection(self, is_connected):
        if is_connected:
            self.ui.arduino_status_lbl.setStyleSheet(STATUS_ON_STYLE)
        else:
            self.ui.arduino_status_lbl.setStyleSheet(STATUS_OFF_STYLE)

    def set_max_vert_speed(self, val):
        self.ui.vert_speed_spin.setValue(val)

    def set_max_horiz_speed(self, val):
        self.ui.horiz_speed_spin.setValue(val)

    def set_max_rotation_speed(self, val):
        self.ui.rot_speed_spin.setValue(val)

    def get_control_mode(self):
        return self.ui.control_group.checkedButton().text()

    def set_control_mode(self, _mode):
        if _mode == "Arduino Continu":
            self.ui.arduino_continous_radio.setChecked(True)
        else:
            self.ui.arduino_discrete_radio.setChecked(True)

    def get_drone_type(self):
        return self.ui.drone_group.checkedButton().text()

    def set_drone_type(self, _type):
        if _type == "Crazyflie":
            self.ui.crazy_radio.setChecked(True)
        elif _type == "ARDrone":
            self.ui.ar_radio.setChecked(True)
        else:
            self.ui.tello_radio.setChecked(True)

    def set_comments(self, comments):
        self.ui.comment_textEdit.setText(comments)

    def set_discrete_threshold(self, _threshold):
        self.ui.discrete_treshold_spin.setValue(_threshold)

    def set_discrete_duration(self, _duration):
        self.ui.discrete_duration_spin.setValue(_duration)

    def get_max_vert_speed(self):
        return self.ui.vert_speed_spin.value()

    def get_max_horiz_speed(self):
        return self.ui.horiz_speed_spin.value()

    def get_max_rotation_speed(self):
        return self.ui.rot_speed_spin.value()

    def update_activated_axis(self):
        self.axesChanged.emit(self.get_axes())

    def set_axes(self, _axes):
        self.z_axis.set_active(bool(_axes[0]))
        if not self.ui.simple_mode.isChecked():
            self.rotation_axis.set_active(bool(_axes[1]))
            self.front_axis.set_active(bool(_axes[2]))
        else:
            self.rotation_axis.set_active(False)
            self.front_axis.set_active(False)

        self.right_axis.set_active(bool(_axes[3]))

    def get_axes(self):
        return [self.z_axis.is_active(), self.rotation_axis.is_active(), self.front_axis.is_active(),
                self.right_axis.is_active()]

    def get_comments(self):
        return self.ui.comment_textEdit.toPlainText()

    def get_discrete_threshold(self):
        return self.ui.discrete_treshold_spin.value()

    def get_discrete_duration(self):
        return self.ui.discrete_duration_spin.value()

    def closeEvent(self, event):
        self.closing.emit()

    def on_selection_changed(self, selected, deselected):
        index = self.ui.presets_listView.currentIndex()
        preset = str(index.data())
        self.presetChanged.emit(preset)

    def populate_presets(self, path):
        self.presets_path = path
        self.file_model.setRootPath(path)
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.ui.presets_listView.setModel(self.file_model)

        def load_first_element(val):
            self.ui.presets_listView.setCurrentIndex(self.file_model.index(0, 0, self.ui.presets_listView.rootIndex()))

        self.file_model.directoryLoaded.connect(load_first_element)
        self.ui.presets_listView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.presets_listView.setRootIndex(self.file_model.index(path))
        self.ui.presets_listView.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def get_current_preset(self):
        return self.current_preset
