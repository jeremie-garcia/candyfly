import os

from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QFileSystemWatcher
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QFont, QPixmap, QIcon, QPolygonF
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsEllipseItem, QSlider, QGraphicsProxyWidget, QGraphicsPixmapItem, QPushButton, \
    QGraphicsPolygonItem, QRadioButton, \
    QButtonGroup, QTextEdit, QGraphicsItem

from rangeslider import QRangeSlider

BG_COL = Qt.black
FG_COL = Qt.lightGray
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

TOP_ANCHOR = 0
LEFT_ANCHOR = 0

TITLE_FONT = QFont('Helvetica', 12)
STRIP_FONT = QFont('Helvetica', 8)

SLIDER_STYLE_SHEET = "background-color: transparent; border-style: outset; border-width: 2px; border-radius: 10px; " \
                     "border-color: beige; "
SLIDER_STYLE_SHEET = ""
BUTTON_STYLE_SHEET = "background-color: black; border-style: none;color:lightGray"
TEXT_EDIT_STYLE_SHEET = "background-color: black; border-style: none; border-width: 0px; color:lightGray"
SAVE_BUTTON_STYLE_SHEET = "background-color: black; border-style: outset; border-width: 1px; border-radius: 10px; " \
                          "color:lightGray ;border-color: beige; "
PAGE_BUTTON_STYLE_SHEET = "background-color: black; border-style: outset; border-width: 1px; border-radius: 0px; " \
                          "color:lightGray ;border-color: beige; "
ACTIVE_PAGE_BUTTON_STYLE_SHEET = "background-color: rgb(169,49,178); border-style: outset; border-width: 1px; " \
                                 "border-radius: 0px; color:lightGray ;border-color: beige; "

TAKEOFF_BUTTON_STYLE_SHEET = "background-color: green; border-style: outset; border-width: 1px; border-radius: 2px; " \
                          "color:lightGray ;border-color: beige; min-width:120px; min-height:60px;"

LAND_BUTTON_STYLE_SHEET = "background-color: red; border-style: outset; border-width: 1px; border-radius: 2px; " \
                          "color:lightGray ;border-color: beige; min-width:120px; min-height:60px;"


class DroneStrip(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 0, 300, 100)
        _scene = _win.scene
        self.win = _win

        self.setPen(FG_PEN)

        QGraphicsTextItem("Drone Strip", self).setDefaultTextColor(FG_COL)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = script_dir + os.path.sep + "img" + os.path.sep + 'refresh.png'
        self.refresh = QPushButton("")
        self.refresh.setStyleSheet(BUTTON_STYLE_SHEET)
        self.refresh.setIcon(QIcon(icon_path))
        self.proxy = _scene.addWidget(self.refresh)
        self.proxy.setPos(275, TOP_ANCHOR + 2)

        QGraphicsLineItem(0, 20, 300, 20, self).setPen(FG_PEN)

        drone_text = QGraphicsTextItem("Connection: ", self)
        drone_text.setDefaultTextColor(FG_COL)
        drone_text.setPos(0, 30)

        drone_led = QGraphicsEllipseItem(80, 28, 30, 30, self)
        drone_led.setPen(FG_PEN)
        drone_led.setBrush(OFF_BRUSH)
        self.status_led = drone_led

        battery_text = QGraphicsTextItem("Battery: ", self)
        battery_text.setDefaultTextColor(FG_COL)
        battery_text.setPos(0, 65)

        battery_level_bg = QGraphicsRectItem(55, 63, 80, 30, self)
        battery_level_bg.setPen(FG_PEN)
        battery_level_bg.setBrush(Qt.darkGray)
        self.battery_level_bg = battery_level_bg

        battery_level = QGraphicsRectItem(56, 64, 10, 28, self)
        battery_level.setPen(Qt.transparent)
        battery_level.setBrush(Qt.darkRed)
        self.battery_level_rect = battery_level

        battery_level_value = QGraphicsTextItem("0v", self)
        battery_level_value.setDefaultTextColor(BG_COL)
        battery_level_value.setPos(80, 70)
        self.battery_level_value = battery_level_value

        self.is_flying = False
        self.takeoff = QPushButton("Décollage")
        self.takeoff.setStyleSheet(TAKEOFF_BUTTON_STYLE_SHEET)
        self.proxy_btn = _scene.addWidget(self.takeoff)
        self.proxy_btn.setPos(160, TOP_ANCHOR + 30)
        self.takeoff.clicked.connect(self.process_takeoff_land_req_click)

    def process_takeoff_land_req_click(self):
        if self.is_flying:
            self.win.ask_land.emit()
        else:
            self.win.ask_take_off.emit()

    def update_is_flying(self, is_flying):
        self.is_flying = is_flying
        if is_flying:
            self.takeoff.setStyleSheet(LAND_BUTTON_STYLE_SHEET)
            self.takeoff.setText('Atterrissage')
        else:
            self.takeoff.setStyleSheet(TAKEOFF_BUTTON_STYLE_SHEET)
            self.takeoff.setText('Décollage')

    def update_connection(self, status):
        if status == "on":
            self.status_led.setBrush(ON_BRUSH)
        elif status == "progress":
            self.status_led.setBrush(PROGRESS_BRUSH)
        else:
            self.status_led.setBrush(OFF_BRUSH)

    def update_battery_level(self, val_in_volt):
        self.battery_level_value.setPlainText("{:.1f}".format(val_in_volt))

        max = 4.3
        mid = 3.6
        min = 3.1

        col = Qt.red
        if val_in_volt > mid:
            col = Qt.green
        elif val_in_volt > min:
            col = Qt.yellow

        self.battery_level_rect.setBrush(QBrush(col))

        percentage = val_in_volt / max
        max_width = 80  # in scene
        width = max_width * percentage
        rect = self.battery_level_bg.boundingRect()
        rect.setWidth(width)
        rect.setHeight(rect.height() - 1)
        rect.setTop(rect.top() + 1)
        rect.setLeft(rect.left() + 1)
        self.battery_level_rect.setRect(rect)


class CommandStrip(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 0, 300, 100)
        _scene = _win.scene

        self.setPen(FG_PEN)

        text = QGraphicsTextItem("Commande Strip", self)
        text.setDefaultTextColor(FG_COL)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = script_dir + os.path.sep + "img" + os.path.sep + 'refresh.png'
        self.refresh = QPushButton("")
        self.refresh.setStyleSheet(BUTTON_STYLE_SHEET)
        self.refresh.setIcon(QIcon(icon_path))
        self.proxy = _scene.addWidget(self.refresh)
        self.proxy.setPos(575, TOP_ANCHOR + 2)

        line = QGraphicsLineItem(0, 20, 300, 20, self)
        line.setPen(FG_PEN)

        riot_text = QGraphicsTextItem("Riot: ", self)
        riot_text.setDefaultTextColor(FG_COL)
        riot_text.setPos(0, 30)

        riot_led = QGraphicsEllipseItem(50, 28, 30, 30, self)
        riot_led.setPen(FG_PEN)
        riot_led.setBrush(OFF_BRUSH)
        self.riot_led = riot_led

        control_toggle = QGraphicsRectItem(90, 30, 40, 20, self)
        control_toggle.setPen(FG_PEN)
        self.selected_control = QGraphicsRectItem(90, 30, 20, 20, self)
        self.selected_control.setPen(FG_PEN)
        self.selected_control.setBrush(SEL_BRUSH)

        arduino_text = QGraphicsTextItem("ARDUINO: ", self)
        arduino_text.setDefaultTextColor(FG_COL)
        arduino_text.setPos(150, 30)

        arduino_led = QGraphicsEllipseItem(220, 28, 30, 30, self)
        arduino_led.setPen(FG_PEN)
        arduino_led.setBrush(OFF_BRUSH)
        self.arduino_led = arduino_led

        self.modeGroup = QButtonGroup()
        self.mode_continu = QRadioButton("continu")
        self.mode_discret = QRadioButton("discret")
        self.modeGroup.addButton(self.mode_continu)
        self.modeGroup.addButton(self.mode_discret)
        self.mode_continu.setStyleSheet(BUTTON_STYLE_SHEET)
        self.mode_discret.setStyleSheet(BUTTON_STYLE_SHEET)

        self.continu = _scene.addWidget(self.mode_continu)
        self.continu.setPos(450, TOP_ANCHOR + 55)

        self.discret = _scene.addWidget(self.mode_discret)
        self.discret.setPos(450, TOP_ANCHOR + 75)

    def set_selected_control(self, _control):
        # print("controller", _control)
        if _control == "riot":
            self.selected_control.setPos(0, 0)
        else:
            self.selected_control.setPos(20, 0)

    def set_mode(self, _mode):
        if _mode == "continu":
            self.mode_continu.setChecked(True)
        else:
            self.mode_discret.setChecked(True)

    def update_riot_connection(self, is_connected):
        # print("connection ", is_connected)
        if is_connected:
            self.riot_led.setBrush(ON_BRUSH)
        else:
            self.riot_led.setBrush(OFF_BRUSH)

    def update_arduino_connection(self, is_connected):
        if is_connected:
            self.arduino_led.setBrush(ON_BRUSH)
        else:
            self.arduino_led.setBrush(OFF_BRUSH)


class VerticalAxis(QGraphicsPolygonItem):
    def __init__(self, parent, _icon_top_file, _icon_bottom_file):
        super().__init__(parent)

        self.index = 0
        self.active = False

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
        self.setBrush(ON_BRUSH)
        self.setPen(ON_PEN)

        self.value_point = QGraphicsEllipseItem(width / 2 - 5, height / 2 - 5, 10, 10)
        self.value_point.setPen(BG_PEN)
        self.value_point.setBrush(FG_COL)
        self.value_point.setParentItem(self)
        self.value_point.setZValue(10)

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
        self.parentItem().parentItem().update_activated_axis()
        self.update_active()

    def display(self, value):
        _x = self.width / 2 - 5
        h = self.height

        _y = (1 - value) * h / 2
        # scale input between 1 and -1 between 0 (1) and height
        self.value_point.setRect(_x, _y - 5, 10, 10)


class RectSelector(QGraphicsRectItem):
    def __init__(self, parent, _axis1, _axis2):
        super().__init__(0, 0, 40, 40)
        self.setBrush(Qt.transparent)
        self.setParentItem(parent)
        self.setPen(FG_PEN)
        self.axis1 = _axis1
        self.axis2 = _axis2
        self.setZValue(8)

    def mousePressEvent(self, event):
        active = True
        if (self.axis1 and self.axis2 and (self.axis1.is_active() or self.axis2.is_active())):
            #if any is active then switch off both
            active = False
        if self.axis1:
            self.axis1.set_active(active)
        if self.axis2:
            self.axis2.set_active(active)
        self.parentItem().parentItem().update_activated_axis()

    def set_axis(self, _axis1, _axis2):
        self.axis1 = _axis1
        self.axis2 = _axis2


class CalibrationRange(QGraphicsProxyWidget):
    def __init__(self, _parent=None, _title="range", _min=0, _max=100, _start=5, _end=95, _win=None):
        super().__init__()
        _scene = _win.scene
        self.setParentItem(_parent)
        self.text = QGraphicsTextItem(_title, self)
        self.text.setFont(STRIP_FONT)
        self.text.setDefaultTextColor(FG_COL)
        self.text.setPos(0, 0)
        self.rs = QRangeSlider()
        self.rs.setMin(_min)
        self.rs.setMax(_max)
        self.rs.setRange(_start, _end)
        self.rs.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.rs.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.proxy = _scene.addWidget(self.rs)
        # prevent some caching errors in repaint
        self.proxy.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.proxy.setZValue(1)
        self.rs.endValueChanged.connect(_win.calibrationChanged)
        self.rs.startValueChanged.connect(_win.calibrationChanged)

    def paint(self, painter, option, widget):
        QGraphicsProxyWidget.paint(self, painter, option, widget)
        scene_pos = self.mapToScene(self.text.pos())
        scene_pos.setY(scene_pos.y() + 15)
        self.proxy.setPos(scene_pos)

    def hide(self):
        self.rs.hide()
        self.text.hide()

    def show(self):
        self.rs.show()
        self.text.show()

    def set_default_range(self):
        self.set_start(0)
        self.set_end(1)

    def set_start(self, _start):
        self.rs.setStart_silent(_start * 100)

    def set_end(self, _end):
        self.rs.setEnd_silent(_end * 100)

    def get_start(self):
        return self.rs.start() / 100

    def get_end(self):
        return self.rs.end() / 100


class CommandView(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 20, 600, 340)
        self.scene = _win.scene
        self.setBrush(Qt.transparent)
        self.setPen(FG_PEN)

        self.z_axis = VerticalAxis(self, "up.png", "down.png")
        self.rotation_axis = VerticalAxis(self, "clock.png", "anticlock.png")
        self.rotation_axis.setRotation(90)
        self.axis1_rect = RectSelector(self, self.z_axis, self.rotation_axis)

        self.front_axis = VerticalAxis(self, "front.png", "back.png")
        self.right_axis = VerticalAxis(self, "front.png", "back.png")
        self.right_axis.setRotation(90)
        self.axis2_rect = RectSelector(self, self.front_axis, self.right_axis)

        self.range_keys = ["up", "down", "clock", "anticlock", "front", "back", 'right', 'left']
        self.range_sliders = {}

        for key in self.range_keys:
            self.range_sliders[key] = CalibrationRange(self, key, _win=_win)

        self.range_sliders['up'].setPos(40, 50)
        self.range_sliders['down'].setPos(40, 110)
        self.range_sliders['clock'].setPos(40, 170)
        self.range_sliders['anticlock'].setPos(40, 230)
        self.range_sliders['front'].setPos(320, 50)
        self.range_sliders['back'].setPos(320, 110)
        self.range_sliders['right'].setPos(320, 170)
        self.range_sliders['left'].setPos(320, 230)

        self.discrete_label = QGraphicsTextItem("Réglages mode discret", self)
        self.discrete_label.setDefaultTextColor(FG_COL)
        self.discrete_label.setPos(30, 300)
        self.discrete_threshold_slider = SimpleSlider("                        seuil (%)", 0, 1, 0.5, self.scene)
        self.discrete_threshold_slider.setPos(130, 300)
        self.discrete_threshold_slider.setParentItem(self)
        self.discrete_duration_slider = SimpleSlider("                        durée (s)", 0, 2000, 1, self.scene)
        self.discrete_duration_slider.setPos(130, 330)
        self.discrete_duration_slider.setParentItem(self)

    def display_main_page(self):
        self.parentItem().set_selected_page("main")
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

        self.hide_calibration()

    def display_simple_page(self):
        self.parentItem().set_selected_page("simple")
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

        self.hide_calibration()

    def hide_calibration(self):
        for key in self.range_keys:
            slider = self.range_sliders[key]
            slider.hide()
        self.discrete_duration_slider.hide()
        self.discrete_label.hide()
        self.discrete_threshold_slider.hide()

    def show_calibration(self):
        for key in self.range_keys:
            slider = self.range_sliders[key]
            slider.show()
        self.discrete_duration_slider.show()
        self.discrete_label.show()
        self.discrete_threshold_slider.show()

    def display_calibration_page(self):
        self.parentItem().set_selected_page("calibration")
        self.z_axis.hide()
        self.front_axis.hide()
        self.right_axis.hide()
        self.rotation_axis.hide()
        self.axis1_rect.hide()
        self.axis2_rect.hide()
        self.show_calibration()


class CommandViewer(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 0, 600, 400)
        _scene = _win.scene
        self.setPen(FG_PEN)
        self.win = _win

        text = QGraphicsTextItem("Command Viewer", self)
        text.setDefaultTextColor(FG_COL)
        line = QGraphicsLineItem(0, 20, 600, 20, self)
        line.setPen(FG_PEN)

        self.view = CommandView(self.win)
        self.view.setParentItem(self)

        # page buttons
        page_main = QPushButton("PRINCIPALE")
        page_main.setStyleSheet(ACTIVE_PAGE_BUTTON_STYLE_SHEET)
        page_main.setMinimumHeight(40)
        page_main.setMinimumWidth(200)
        page_main.clicked.connect(self.view.display_main_page)
        self.main_button = page_main
        proxy = _scene.addWidget(page_main)
        proxy.setPos(0, TOP_ANCHOR + 460)

        page_simple = QPushButton("SIMPLIFIE")
        page_simple.setStyleSheet(PAGE_BUTTON_STYLE_SHEET)
        page_simple.setMinimumHeight(40)
        page_simple.setMinimumWidth(200)
        page_simple.clicked.connect(self.view.display_simple_page)
        self.simple_button = page_simple
        proxy = _scene.addWidget(page_simple)
        proxy.setPos(200, TOP_ANCHOR + 460)

        page_calibration = QPushButton("CALIBRATION")
        page_calibration.setStyleSheet(PAGE_BUTTON_STYLE_SHEET)
        page_calibration.setMinimumHeight(40)
        page_calibration.setMinimumWidth(200)
        page_calibration.clicked.connect(self.view.display_calibration_page)
        self.calibration_button = page_calibration
        proxy = _scene.addWidget(page_calibration)
        proxy.setPos(400, TOP_ANCHOR + 460)

        self.selected_page = ""
        self.view.display_main_page()

    def set_selected_page(self, page):
        self.selected_page = page
        self.calibration_button.setStyleSheet(PAGE_BUTTON_STYLE_SHEET)
        self.simple_button.setStyleSheet(PAGE_BUTTON_STYLE_SHEET)
        self.main_button.setStyleSheet(PAGE_BUTTON_STYLE_SHEET)
        if page == "main":
            self.main_button.setStyleSheet(ACTIVE_PAGE_BUTTON_STYLE_SHEET)
        elif page == 'simple':
            self.simple_button.setStyleSheet(ACTIVE_PAGE_BUTTON_STYLE_SHEET)
        else:
            self.calibration_button.setStyleSheet(ACTIVE_PAGE_BUTTON_STYLE_SHEET)

    def set_axes(self, _axes):
        self.view.z_axis.set_active(bool(_axes[0]))
        if not self.selected_page == "simple":
            self.view.rotation_axis.set_active(bool(_axes[1]))
            self.view.front_axis.set_active(bool(_axes[2]))
        else:
            self.view.rotation_axis.set_active(False)
            self.view.front_axis.set_active(False)

        self.view.right_axis.set_active(bool(_axes[3]))

    def get_axes(self):
        return [self.view.z_axis.is_active(), self.view.rotation_axis.is_active(), self.view.front_axis.is_active(),
                self.view.right_axis.is_active()]

    def get_calibration(self):
        res = {}
        for key in self.view.range_keys:
            slider = self.view.range_sliders[key]
            res[key] = [slider.get_start(), slider.get_end()]
        return res

    def set_calibration(self, calibration_list):
        for key in self.view.range_keys:
            if key in calibration_list:
                values = calibration_list[key]
                slider = self.view.range_sliders[key]
                slider.set_start(values[0])
                slider.set_end(values[1])
            else:
                self.view.range_sliders[key].set_default_range()
        self.win.calibrationChanged.emit()

    def display_processed_inputs(self, _up, _rotate, _front, _right):
        self.view.z_axis.display(_up)
        self.view.rotation_axis.display(_rotate)
        self.view.front_axis.display(_front)
        self.view.right_axis.display(_right)

    def display_raw_inputs(self, _up, _rotate, _front, _right):
        pass

    def update_activated_axis(self):
        self.win.axesChanged.emit(self.get_axes())


class SimpleSlider(QGraphicsProxyWidget):
    def __init__(self, _title="slider", _min=0, _max=2, _value=0, _scene=None):
        super().__init__()
        self.value = _value
        self.min = _min
        self.max = _max
        self.range = min(_max - _min, 0)

        # title
        text = QGraphicsTextItem(_title, self)
        text.setFont(STRIP_FONT)
        text.setDefaultTextColor(FG_COL)
        text.setPos(0, 0)
        self.title = text

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(_min * 100)
        self.slider.setMaximum(_max * 100)
        self.slider.setStyleSheet(SLIDER_STYLE_SHEET)
        self.proxy = _scene.addWidget(self.slider)
        self.proxy.setPos(0, 200)

        self.slider.valueChanged.connect(lambda val: text.setPlainText(str(val / 100)))

        # value
        text = QGraphicsTextItem("value", self)
        text.setDefaultTextColor(FG_COL)
        text.setFont(STRIP_FONT)
        text.setPos(330, 0)
        self.text_value = text

        self.slider.setValue(_value * 100)

        self.setMaximumHeight(30)

    def paint(self, painter, option, widget):
        QGraphicsProxyWidget.paint(self, painter, option, widget)
        scene_pos = self.mapToScene(self.text_value.pos())
        scene_pos.setX(scene_pos.x() - 200)
        self.proxy.setPos(scene_pos)

    def setValue(self, value):
        self.slider.setValue(value * 100)

    def get_value(self):
        return self.slider.value() / 100

    def hide(self):
        self.slider.hide()
        self.text_value.hide()
        self.title.hide()

    def show(self):
        self.slider.show()
        self.text_value.show()
        self.title.show()


class SpeedStrip(QGraphicsRectItem):
    def __init__(self, _win):
        width = 400
        super().__init__(0, 0, width, 100)
        _scene = _win.scene

        self.setPen(FG_PEN)

        text = QGraphicsTextItem("Speed Strip", self)
        text.setDefaultTextColor(FG_COL)
        line = QGraphicsLineItem(0, 20, width, 20, self)
        line.setPen(FG_PEN)

        # horizontal
        self.horiz_speed_slider = SimpleSlider("Horizontal Speed (m/s)", 0, 2, 0.5, _scene)
        self.horiz_speed_slider.setPos(0, 25)
        # to divide by 100
        self.horiz_speed_slider.slider.valueChanged.connect(
            lambda val: _win.horizontalSpeedValueChanged.emit(val / 100))
        self.horiz_speed_slider.setParentItem(self)

        self.vert_speed_slider = SimpleSlider("Vertical Speed (m/s)", 0, 2, 0.5, _scene)
        self.vert_speed_slider.setPos(0, 50)
        self.vert_speed_slider.slider.valueChanged.connect(
            lambda val: _win.verticalSpeedValueChanged.emit(val / 100))
        self.vert_speed_slider.setParentItem(self)
        self.rotation_speed_slider = SimpleSlider("Rotation Speed (°/s)", 0, 360, 90, _scene)
        self.rotation_speed_slider.setPos(0, 75)
        self.rotation_speed_slider.slider.valueChanged.connect(
            lambda val: _win.rotationSpeedValueChanged.emit(val / 100))
        self.rotation_speed_slider.setParentItem(self)


class PresetItem(QGraphicsTextItem):
    def __init(self, *args):
        super().__init__(*args)
        self.path = None
        self.signal = None

    def set_path(self, _path):
        self.path = _path

    def set_signal(self, _signal):
        self.signal = _signal

    def mousePressEvent(self, event):
        self.parentItem().win.presetChanged.emit(self.path)


class PresetStrip(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 0, 200, 501)

        self.win = _win
        self.setPen(FG_PEN)
        line = QGraphicsLineItem(0, 20, 200, 20, self)
        line.setPen(FG_PEN)

        text = QGraphicsTextItem("Presets", self)
        text.setDefaultTextColor(FG_COL)

        self.watcher = QFileSystemWatcher()
        self.current_preset = None

        # slider
        self.save_button = QPushButton(" Enregistrer Sous ")
        self.save_button.setStyleSheet(SAVE_BUTTON_STYLE_SHEET)
        self.proxy = self.win.scene.addWidget(self.save_button)
        self.proxy.setPos(610, TOP_ANCHOR + 410)
        self.save_button.clicked.connect(self.win.saveAsked.emit)

        # add logos
        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = script_dir + os.path.sep + "img" + os.path.sep + 'candyfly-logo.png'
        logo = QGraphicsPixmapItem(self)
        logo.setPixmap(QPixmap(icon_path))

        enac_path = script_dir + os.path.sep + "img" + os.path.sep + 'ENAC-Bleu.png'
        logo_enac = QGraphicsPixmapItem(self)
        logo_enac.setPixmap(QPixmap(enac_path))

        logo.setScale(0.08)
        logo.setPos(110, 445)

        logo_enac.setScale(0.2)
        logo_enac.setPos(20, 450)

    def clear_view(self):
        for item in self.childItems():
            if isinstance(item, PresetItem):
                item.deleteLater()

    def on_dir_change(self, data):
        self.populate_presets(data)

    def populate_presets(self, path):
        self.watcher.addPath(path)
        self.watcher.directoryChanged.connect(self.on_dir_change)

        self.clear_view()
        vert_pos = 20

        files = []
        for root, dirs, files in os.walk(path, topdown=True):
            files = [f for f in files if (f.endswith(".json") and not f.startswith("."))]
            files.sort()
            for file in files:
                basename = os.path.basename(file)
                item = PresetItem(basename.replace(".json", ""), self)
                item.set_path(file)
                item.set_signal(self.win.presetChanged)
                item.setDefaultTextColor(FG_COL)
                item.setPos(0, vert_pos)
                vert_pos += 20
        if self.current_preset:
            self.win.presetChanged.emit(self.current_preset)
        elif len(files) > 0:
            # print("opening " + files[0])
            self.win.presetChanged.emit(files[0])
        else:
            pass
            # print("no presets available")

    def set_current(self, file):
        self.current_preset = file
        for child in self.childItems():
            if isinstance(child, PresetItem):
                if child.path == file:
                    child.setDefaultTextColor(ON_COL)
                else:
                    child.setDefaultTextColor(FG_COL)

    def get_current(self):
        return self.current_preset


class CommentStrip(QGraphicsRectItem):
    def __init__(self, _win):
        super().__init__(0, 0, 400, 100)

        self.win = _win
        _scene = self.win.scene

        self.setPen(FG_PEN)
        line = QGraphicsLineItem(0, 20, 400, 20, self)
        line.setPen(FG_PEN)

        text = QGraphicsTextItem("Commentaires", self)
        text.setDefaultTextColor(FG_COL)

        # slider
        self.comment = QTextEdit()
        self.comment.setStyleSheet(TEXT_EDIT_STYLE_SHEET)
        self.comment.setFixedWidth(400)
        self.comment.setFixedHeight(80)
        self.comment.setPlaceholderText("Tapez un commentaires ici")
        self.proxy = _scene.addWidget(self.comment)
        self.proxy.setPos(400, 541)

    def set_comments(self, _comments):
        self.comment.setText(_comments)

    def get_comments(self):
        return self.comment.toPlainText()


class CandyWin(QMainWindow):
    refreshDroneAsked = pyqtSignal()
    refreshDeviceAsked = pyqtSignal()
    verticalSpeedValueChanged = pyqtSignal(float)
    horizontalSpeedValueChanged = pyqtSignal(float)
    rotationSpeedValueChanged = pyqtSignal(float)
    axesChanged = pyqtSignal(list)
    presetChanged = pyqtSignal(str)
    closing = pyqtSignal()
    commandModeChanged = pyqtSignal(str)
    saveAsked = pyqtSignal()
    calibrationChanged = pyqtSignal()
    discrete_threshold_changed = pyqtSignal(float)
    discrete_duration_changed = pyqtSignal(float)
    ask_take_off = pyqtSignal()
    ask_land = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 860, 660)
        #self.setFixedSize(830, 630)
        self.setWindowTitle('Candifly')

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.scale(1,1)

        self.scene.setBackgroundBrush(BG_COL)

        # create elements
        self.droneStrip = DroneStrip(self)
        self.commandStrip = CommandStrip(self)
        self.commandViewer = CommandViewer(self)
        self.speedStrip = SpeedStrip(self)
        self.presetStrip = PresetStrip(self)
        self.commentStrip = CommentStrip(self)

        # add elements
        self.scene.addItem(self.droneStrip)
        self.scene.addItem(self.commandStrip)
        self.scene.addItem(self.commandViewer)
        self.scene.addItem(self.speedStrip)
        self.scene.addItem(self.presetStrip)
        self.scene.addItem(self.commentStrip)

        self.droneStrip.setPos(LEFT_ANCHOR, TOP_ANCHOR)
        self.commandStrip.setPos(LEFT_ANCHOR + self.droneStrip.boundingRect().width(), TOP_ANCHOR)
        self.commandViewer.setPos(LEFT_ANCHOR, TOP_ANCHOR + self.droneStrip.boundingRect().height())
        self.speedStrip.setPos(LEFT_ANCHOR,
                               TOP_ANCHOR + self.commandViewer.boundingRect().height() + self.droneStrip.boundingRect().height())
        self.presetStrip.setPos(LEFT_ANCHOR + self.commandViewer.boundingRect().width(), TOP_ANCHOR)
        self.commentStrip.setPos(LEFT_ANCHOR + self.speedStrip.boundingRect().width(),
                                 TOP_ANCHOR + self.commandViewer.boundingRect().height() + self.droneStrip.boundingRect().height())

        self.droneStrip.refresh.clicked.connect(self.refreshDroneAsked.emit)
        self.commandStrip.refresh.clicked.connect(self.refreshDeviceAsked.emit)

        self.commandStrip.modeGroup.buttonClicked.connect(lambda button: self.commandModeChanged.emit(button.text()))

        self.commandViewer.view.discrete_threshold_slider.slider.valueChanged.connect(
            lambda val: self.discrete_threshold_changed.emit(val / 100))
        self.commandViewer.view.discrete_duration_slider.slider.valueChanged.connect(
            lambda val: self.discrete_duration_changed.emit(val / 100))

    def update_battery(self, battery_val):
        self.droneStrip.update_battery_level(battery_val)

    def update_is_flying(self, is_flying):
        self.droneStrip.update_is_flying(is_flying)

    def update_drone_connection(self, connection_status):
        self.droneStrip.update_connection(connection_status)
        if connection_status != "on":
            self.droneStrip.update_battery_level(0)

    def update_riot_connection(self, is_connected):
        self.commandStrip.update_riot_connection(is_connected)

    def update_arduino_connection(self, is_connected):
        self.commandStrip.update_arduino_connection(is_connected)

    def set_max_vert_speed(self, val):
        self.speedStrip.vert_speed_slider.setValue(val)

    def set_max_horiz_speed(self, val):
        self.speedStrip.horiz_speed_slider.setValue(val)

    def set_max_rotation_speed(self, val):
        self.speedStrip.rotation_speed_slider.setValue(val)

    def set_axes(self, axes):
        self.commandViewer.set_axes(axes)

    def set_mode(self, _mode):
        self.commandStrip.set_mode(_mode)

    def set_calibration(self, _calibration):
        self.commandViewer.set_calibration(_calibration)

    def set_comments(self, comments):
        self.commentStrip.set_comments(comments)

    def set_discrete_threshold(self, _threshold):
        self.commandViewer.view.discrete_threshold_slider.setValue(_threshold)

    def set_discrete_duration(self, _duration):
        self.commandViewer.view.discrete_duration_slider.setValue(_duration)

    def get_max_vert_speed(self):
        return self.speedStrip.vert_speed_slider.get_value()

    def get_max_horiz_speed(self):
        return self.speedStrip.horiz_speed_slider.get_value()

    def get_max_rotation_speed(self):
        return self.speedStrip.rotation_speed_slider.get_value()

    def get_axes(self):
        return self.commandViewer.get_axes()

    def get_comments(self):
        return self.commentStrip.get_comments()

    def get_discrete_threshold(self):
        return self.commandViewer.view.discrete_threshold_slider.get_value()

    def get_discrete_duration(self):
        return self.commandViewer.view.discrete_duration_slider.get_value()

    def get_mode(self):
        return self.commandStrip.modeGroup.checkedButton().text()

    def get_calibration(self):
        return self.commandViewer.get_calibration()

    def set_current_preset(self, path):
        self.presetStrip.set_current(path)

    def get_current_preset(self):
        self.presetStrip.get_current()

    def closeEvent(self, event):
        self.closing.emit()

    def set_selected_controller(self, _controller_name):
        self.commandStrip.set_selected_control(_controller_name)
