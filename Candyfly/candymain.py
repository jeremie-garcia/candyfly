import io
import json

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QAction

from arduino import *
from candyGuiForm import CandyWinForm
from riot import *
from crazydrone import *

RIOT_ID = 1

MODE_AR_CONT = "Arduino Continu"
MODE_AR_DISCONT = "Arduino Discret"
MODE_RIOT_SPIN = "Riot Rotation"
MODE_RIOT_NRJ = "Riot Energie"


def scale_value(_val, _positive_params, _negative_params):
    """Scaling function to remap inputs within defined range"""
    is_positive = (_val >= 0)
    _params = _positive_params if is_positive else _negative_params

    _val = abs(_val)

    if _val < _params[0]:
        _val = 0
    elif _val > _params[1]:
        _val = 1
    else:
        _val = (_val - _params[0]) / (_params[1] - _params[0])

    if not is_positive:
        _val = _val * -1

    return _val


def get_script_dir():
    if getattr(sys, 'frozen', False):
        # TODO: test on other platforms (windows mostly)
        if sys.platform == 'win32' or sys.platform == 'win64' or sys.platform == 'linux':
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
    else:
        return os.path.dirname(os.path.realpath(__file__))


class CandyFly(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.aboutToQuit.connect(self.stop_all)

        self.candyWin = CandyWinForm()
        self.set_icon()
        self.candyWin.show()
        self.candyWin.setGeometry(0, 0, 1200, 800)

        exit_action = QAction('Quit', self)
        exit_action.triggered.connect(self.quit)
        menubar = self.candyWin.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(exit_action)

        self.drone = None
        self.arduino = None
        self.is_riot = False
        self.riot = None

        calibration = self.candyWin.get_calibration()
        self.calibration_values = [calibration['up'], calibration['down'], calibration['clock'],
                                   calibration['anticlock'], calibration['front'],
                                   calibration['back'], calibration['right'], calibration['left']]

        # used for discrete motion (click-like)
        self.discrete_mode_timer = QTimer()
        self.discrete_mode_timer.timeout.connect(self.update_motion_from_timer)
        self.discrete_states = ["idle", "idle", "idle", "idle"]
        self.discrete_motion_values = [0, 0, 0, 0]
        # states = idle, moving, waiting
        self.discrete_threshold = 0.5
        self.discrete_duration = 1000
        self.discrete_mode_timer_tick = 100  # ms

        self.candyWin.refreshArduinoAsked.connect(self.init_arduino)
        self.candyWin.refreshRiotAsked.connect(self.init_riot)
        self.candyWin.refreshDroneAsked.connect(self.init_drone_connection)

        self.candyWin.presetChanged.connect(self.load_params_from_file)
        self.candyWin.saveAsked.connect(self.save_as)
        self.candyWin.calibrationChanged.connect(self.update_calibration)
        self.candyWin.discrete_threshold_changed.connect(self.update_discrete_threshold)
        self.candyWin.discrete_duration_changed.connect(self.update_discrete_duration)

        self.candyWin.ask_land.connect(self.land)
        self.candyWin.ask_take_off.connect(self.take_off)

        self.candyWin.control_changed.connect(self.update_control_mode)
        # load presets
        script_dir = get_script_dir()
        self.presets_path = script_dir + os.path.sep + 'presets'
        self.candyWin.populate_presets(self.presets_path)

        # init resources
        self.init_arduino()
        self.init_drone_connection()
        self.init_riot()

        # init values to default
        self.candyWin.update_battery_level(0)

        self.set_icon()
        sys.exit(self.exec_())

    def update_discrete_threshold(self, _threshold):
        self.discrete_threshold = _threshold

    def update_discrete_duration(self, _duration):
        self.discrete_duration = _duration

    def set_motion_state(self, _index, _value):
        self.discrete_motion_values[_index] = _value

    def reset_motion_state_timer(self, index, value):
        QTimer.singleShot(self.discrete_duration, lambda: self.set_motion_state(index, value))

    def update_motion_from_timer(self):
        _up = self.discrete_motion_values[0]
        _rotate = self.discrete_motion_values[1]
        _front = self.discrete_motion_values[2]
        _right = self.discrete_motion_values[3]
        # ("Discrete Motion Command: ", _up, _rotate, _front, _right)
        if self.drone is not None and self.drone.is_flying():
            self.drone.process_motion(_up, _rotate, _front, _right)

    def process_discrete_motion(self, _up, _rotate, _front, _right):
        # detecting clicks with states
        # print("Discrete Motion Command PRE: ", _up, _rotate, _front, _right)
        self.process_discrete_motion_for_axis(0, _up)
        self.process_discrete_motion_for_axis(1, _rotate)
        self.process_discrete_motion_for_axis(2, _front)
        self.process_discrete_motion_for_axis(3, _right)

    def process_discrete_motion_for_axis(self, _axis_index, _axis):
        if self.discrete_states[_axis_index] == "idle" and _axis > self.discrete_threshold:
            self.discrete_states[_axis_index] = "pressed+"
        elif self.discrete_states[_axis_index] == "idle" and _axis < -self.discrete_threshold:
            self.discrete_states[_axis_index] = "pressed-"
        elif self.discrete_states[_axis_index] == "pressed+" and _axis < self.discrete_threshold:
            self.discrete_motion_values[_axis_index] = 1
            self.discrete_states[_axis_index] = "idle"
            self.reset_motion_state_timer(_axis_index, 0)
        elif self.discrete_states[_axis_index] == "pressed-" and _axis > -self.discrete_threshold:
            self.discrete_motion_values[_axis_index] = - 1
            self.discrete_states[_axis_index] = "idle"
            self.reset_motion_state_timer(_axis_index, 0)

    def stop_all(self):
        if self.drone:
            self.drone.stop()
        if self.arduino:
            self.arduino.stop()
        if self.riot:
            self.riot.stop()

    def set_icon(self):
        script_dir = get_script_dir()
        icon_path = script_dir + os.path.sep + 'img' + os.path.sep + 'icon.png'
        self.setWindowIcon(QIcon(icon_path))

    def load_params_from_file(self, file):
        if file is not None:
            script_dir = get_script_dir()
            json_file_path = script_dir + os.path.sep + 'presets' + os.path.sep + file
            json_file = io.open(json_file_path, 'r', encoding='utf8')
            data = json.load(json_file)
            self.set_params(data)
        else:
            self.set_params({})

    def save_as(self):
        # save as button
        script_dir = get_script_dir()
        json_file_path = script_dir + os.path.sep + 'presets'
        file_name, _ = QFileDialog.getSaveFileName(self.candyWin, "Enregistrer sous", json_file_path,
                                                   "JSON Files (*.json)")
        if file_name:
            self.save_current_params_in_file(file_name)

    def save_current_params_in_file(self, file):
        if file is not None:
            data = self.get_params()
            if ".json" not in file:
                file += ".json"

            outfile = io.open(file, 'w', encoding='utf8')
            json.dump(data, outfile, indent=2, ensure_ascii=False)
            outfile.close()

    def set_params(self, params):
        axes = [True, True, True, True]
        if "axes" in params:
            axes = params["axes"]

        horizontal = 0.5
        if "horizontal" in params:
            horizontal = float(params["horizontal"])

        vertical = 0.5
        if "vertical" in params:
            vertical = float(params["vertical"])

        rotation = 0.5
        if "rotation" in params:
            rotation = float(params["rotation"])

        mode = "Arduino Continu"
        if "mode" in params:
            mode = params["mode"]

        commentaires = ""
        if "commentaires" in params:
            commentaires = params["commentaires"]

        calibration = ""
        if "calibration" in params:
            calibration = params["calibration"]

        discrete_duration = 1000
        if "discrete_duration" in params:
            discrete_duration = params["discrete_duration"]

        discrete_threshold = 0.5
        if "discrete_threshold" in params:
            discrete_threshold = params["discrete_threshold"]

        self.candyWin.set_axes(axes)
        self.candyWin.set_max_horiz_speed(horizontal)
        self.candyWin.set_max_vert_speed(vertical)
        self.candyWin.set_max_rotation_speed(rotation)
        self.candyWin.set_control_mode(mode)
        self.candyWin.set_comments(commentaires)
        self.candyWin.set_calibration(calibration)
        self.update_control_mode(mode)
        self.candyWin.set_discrete_duration(discrete_duration)
        self.candyWin.set_discrete_threshold(discrete_threshold)

    def get_params(self):
        json_obj = {"axes": self.candyWin.get_axes(),
                    "commentaires": self.candyWin.get_comments(),
                    "horizontal": self.candyWin.get_max_horiz_speed(),
                    "vertical": self.candyWin.get_max_vert_speed(),
                    "rotation": self.candyWin.get_max_rotation_speed(),
                    "mode": self.candyWin.get_mode(),
                    "calibration": self.candyWin.get_calibration(),
                    "discrete_threshold": self.candyWin.get_discrete_threshold(),
                    "discrete_duration": self.candyWin.get_discrete_duration(),
                    }
        return json_obj

    def init_drone_connection(self):
        if self.drone:
            self.drone.stop()
        available = []
        available = find_available_drones()
        print("Available drones " + str(available))
        if len(available) > 0:
            self.drone = CrazyDrone(available[0][0])

            # init values
            self.drone.set_max_horizontal_speed(self.candyWin.get_max_horiz_speed())
            self.drone.set_max_vertical_speed(self.candyWin.get_max_vert_speed())
            self.drone.set_max_rotation_speed(self.candyWin.get_max_rotation_speed())

            # add signal/slots
            self.drone.connection.connect(self.candyWin.update_drone_connection)
            self.drone.batteryValue.connect(self.candyWin.update_battery_level)
            self.candyWin.verticalSpeedValueChanged.connect(self.drone.set_max_vertical_speed)
            self.candyWin.horizontalSpeedValueChanged.connect(self.drone.set_max_horizontal_speed)
            self.candyWin.rotationSpeedValueChanged.connect(self.drone.set_max_rotation_speed)

            self.drone.is_flying_signal.connect(self.candyWin.update_is_flying)
        else:
            self.drone = None
            print('No Crazyflies found, Refresh')

    def process_takeoff_button(self):
        if not (self.drone is None):
            if self.drone.is_flying():
                print("land")
                self.land()
            else:
                print('take off')
                self.take_off()

    def init_arduino(self):
        if self.arduino:
            self.arduino.connection.disconnect()
            self.arduino.stop()

        available = find_available_arduinos()
        if len(available) > 0:
            self.arduino = ArduinoController(available[0])
            self.arduino.connection.connect(self.candyWin.update_arduino_connection)
            self.process_arduino_sensors(0, 0, 0, 0)
        else:
            self.arduino = None

    def init_riot(self):
        if self.riot:
            self.riot.stop()
        self.riot = Riot(RIOT_ID)
        self.riot.connection.connect(self.candyWin.update_riot_connection)

    def process_acc(self, _x, _y, _z):
        norm, x, y, z = self.riot.intensity(_x, _y, _z)
        # print('intensity', norm, _x, _y, _z)
        self.candyWin.update_riot_energy_gauge(norm)

    def process_gyro(self, _gx, _gy, _gz):
        x, y, z = self.riot.spin_filtered(_gx, _gy, _gz)
        # print("filtered_spin",x,y,z)
        norm = spin(_gx, _gy, _gz)
        self.candyWin.update_riot_spin_gauge(norm * 20)

    def update_calibration(self):
        calib = self.candyWin.get_calibration()
        self.calibration_values = [calib['up'], calib['down'], calib['clock'], calib['anticlock'], calib['front'],
                                   calib['back'], calib['right'], calib['left']]

    def update_control_mode(self, _mode):

        if self.drone is not None:
            self.drone.process_motion(0, 0, 0, 0)

        self.discrete_mode_timer.stop()
        if self.riot is not None:
            try:
                self.riot.gyro.disconnect()
                self.riot.acc.disconnect()
            except TypeError:
                pass

        if self.arduino is not None:
            try:
                self.arduino.sensors.disconnect()
                self.arduino.clicked.disconnect()
            except TypeError:
                pass

        if 'Arduino' in _mode:
            if self.riot is not None:
                self.riot.stop()

            if self.arduino is not None:
                self.arduino.start()
                self.arduino.sensors.connect(self.process_arduino_sensors)
                self.arduino.clicked.connect(self.process_takeoff_button)
            else:
                print('No Arduino device found... refresh')

        elif 'Riot' in _mode:
            if self.arduino is not None:
                self.arduino.stop()
            self.discrete_mode_timer.stop()

            if self.riot is not None:
                self.riot.start()
            else:
                print('No Riot device found... refresh')

        if _mode == MODE_AR_CONT:
            pass
        elif _mode == MODE_AR_DISCONT:
            self.discrete_mode_timer.start(self.discrete_mode_timer_tick)
        elif _mode == MODE_RIOT_NRJ:
            self.riot.acc.connect(self.process_acc)
        elif _mode == MODE_RIOT_SPIN:
            self.riot.gyro.connect(self.process_gyro)

    def update_selected_controller(self):
        if self.is_riot:
            self.candyWin.set_selected_controller("Riot")

            self.init_riot()
        else:
            self.candyWin.set_selected_controller("Arduino")
            self.riot.stop()
            self.init_arduino()
            self.update_discrete_motion_timer()

    def take_off(self):
        if not (self.drone is None):
            self.drone.take_off()

    def land(self):
        if not (self.drone is None):
            self.drone.land()

    def apply_calibration(self, _up, _rotate, _front, _right):
        parameters = self.calibration_values
        _up = scale_value(_up, parameters[0], parameters[1])
        _rotate = scale_value(_rotate, parameters[2], parameters[3])
        _front = scale_value(_front, parameters[4], parameters[5])
        _right = scale_value(_right, parameters[6], parameters[7])
        return _up, _rotate, _front, _right

    def process_arduino_sensors(self, _up, _rotate, _front, _right):
        self.candyWin.display_raw_inputs(_up, _rotate, _front, _right)

        # calibrate input and display
        _up, _rotate, _front, _right = self.apply_calibration(_up, _rotate, _front, _right)
        self.candyWin.display_processed_inputs(_up, _rotate, _front, _right)

        # set inactive axes to zero
        axes = self.candyWin.get_axes()
        if not axes[0]:
            _up = 0
        if not axes[1]:
            _rotate = 0
        if not axes[2]:
            _front = 0
        if not axes[3]:
            _right = 0

        if self.drone is not None:
            # route depending on mode (discrete or continous)
            print(self.candyWin.get_control_mode())
            if self.candyWin.get_control_mode() == MODE_AR_DISCONT:
                self.process_discrete_motion(_up, _rotate, _front, _right)
            elif self.candyWin.get_control_mode() == MODE_AR_CONT:
                self.drone.process_motion(_up, _rotate, _front, _right)


if __name__ == '__main__':
    import sys

    try:
        app = CandyFly(sys.argv)
        pass
    except KeyboardInterrupt:
        sys.exit()
