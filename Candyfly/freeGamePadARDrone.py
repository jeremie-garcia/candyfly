import pygame
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
from pygame import joystick


# init py-game and Joystick lib


def find_available_free_ids():
    pygame.init()
    if joystick.get_init():
        joystick.quit()

    joystick.init()

    for i in range(joystick.get_count()):
        print(joystick.Joystick(i).get_name().lower())

    frsky_ids = [
        i
        for i in range(joystick.get_count())
        if ("joystick") in joystick.Joystick(i).get_name().lower()
    ]
    return frsky_ids


class FreeGamePad(QObject):
    values = pyqtSignal(float, float, float, float)
    connection = pyqtSignal(bool)
    buttons = pyqtSignal(int, int, str)

    def __init__(self, _stream=False, _update_in_millis=50, _id=0):
        super().__init__()
        self.update_in_millis = _update_in_millis
        self.stream = _stream
        self.running = False
        self.id = _id
        self.buttonTags = ["SA", "SB", "SC", "SD", "SE", "SF", "SG", "SH"]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)

        # retrieve the connected and initialize
        print("Opening FRSKY on iD " + str(_id))
        self.stick = joystick.Joystick(self.id)
        self.stick.init()

        self.name = self.stick.get_name()
        self.axes = self.stick.get_numaxes()

        self.axesValues = [0] * self.axes
        self.prevAxesValues = [0] * self.axes

        self.buttons_count = self.stick.get_numbuttons()
        self.buttonsValues = [False] * self.buttons_count
        self.prevButtonsValues = [True] * self.buttons_count

    def emit_button_for_index(self, index):
        self.buttons.emit(index + 1, self.buttonsValues[index], "Button")

    def stop(self):
        self.timer.stop()
        self.connection.emit(False)

    def process(self):
        # necessary to update the event queue
        events = pygame.event.get()
        # retrieve data
        for i in range(self.axes):
            self.axesValues[i] = self.stick.get_axis(i)
        for i in range(self.buttons_count):
            self.buttonsValues[i] = self.stick.get_button(i)

        # update y axis (reversed)
        self.axesValues[1] = - self.axesValues[1]
        self.axesValues[3] = - self.axesValues[3]

        # fire events in streaming conditions
        if self.stream:
            self.values.emit(self.axesValues[0], self.axesValues[1], self.axesValues[2], self.axesValues[3])
            for i in range(self.buttons_count):
                self.emit_button_for_index(i)
                self.prevButtonsValues[i] = self.buttonsValues[i]

        else:
            # fire events only if value changed
            if self.prevAxesValues[0] != self.axesValues[0] or self.prevAxesValues[3] != self.axesValues[3] or \
                    self.prevAxesValues[1] != self.axesValues[1] or self.prevAxesValues[2] != self.axesValues[2]:
                self.prevAxesValues[3] = self.axesValues[3]
                self.prevAxesValues[0] = self.axesValues[0]
                self.prevAxesValues[1] = self.axesValues[1]
                self.prevAxesValues[2] = self.axesValues[2]
                self.values.emit(self.axesValues[0], self.axesValues[1], self.axesValues[2], self.axesValues[3])

            for i in range(self.buttons_count):
                if self.prevButtonsValues[i] != self.buttonsValues[i]:
                    self.emit_button_for_index(i)
                    self.prevButtonsValues[i] = self.buttonsValues[i]

    def send_last_values(self):
        self.values.emit(self.axesValues[0], self.axesValues[1], self.axesValues[2], self.axesValues[3])

    def start(self):
        self.timer.start(self.update_in_millis)
        self.connection.emit(True)


if __name__ == "__main__":
    import sys
    from PyQt5.QtCore import QCoreApplication
    from pyparrot.Bebop import Bebop

    app = QCoreApplication([])
    stream = True
    refresh_duration_in_millis = 50
    id = find_available_free_ids()
    gamepad = FreeGamePad(stream, refresh_duration_in_millis, id[0])
    success = False
    easy = True


    def takeoff():
        if success:
            bebop.safe_takeoff(5)


    def landing():
        if success:
            bebop.safe_land(5)


    @pyqtSlot(float, float, float, float)
    def value_updated(x, y, x2, y2):
        '''slot to listen to the stick values, index, x, y'''
        if success:
            yaw = 20 * x
            if easy:
                yaw = 0

            vertical_movement = 20 * y
            pitch = 20 * y2

            if easy:
                pitch = 0

            roll = 20 * x2
            my_roll = bebop._ensure_fly_command_in_range(roll)
            my_pitch = bebop._ensure_fly_command_in_range(pitch)
            my_yaw = bebop._ensure_fly_command_in_range(yaw)
            my_vertical = bebop._ensure_fly_command_in_range(vertical_movement)
            command_tuple = bebop.command_parser.get_command_tuple("ardrone3", "Piloting", "PCMD")
            bebop.drone_connection.send_single_pcmd_command(command_tuple, my_roll, my_pitch, my_yaw,
                                                            my_vertical)


    @pyqtSlot(int, int, str)
    def button_updated(id, value, tag):
        if success:
            '''slot to listen to the button values, index, state'''
            if id == 7 and value == 1:
                takeoff()
            elif id == 8 and value == 1:
                landing()


    bebop = Bebop()
    print("connecting")
    success = bebop.connect(10)
    print(success)

    gamepad.values.connect(value_updated)
    gamepad.buttons.connect(button_updated)
    gamepad.start()

    app.aboutToQuit.connect(gamepad.stop)
    app.aboutToQuit.connect(landing)
    sys.exit(app.exec_())
