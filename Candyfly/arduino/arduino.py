from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
from serial import Serial, SerialException
from serial.tools.list_ports import comports


def find_available_arduinos():
    arduino_ports = [
        p.device
        for p in comports(False)
        if (("usb" or "tty" or "arduino") in str(p.device).lower()) or ("arduino" in str(p.description).lower())
    ]
    return arduino_ports


class ArduinoController(QObject):
    connection = pyqtSignal(bool)
    sensors = pyqtSignal(float, float, float, float)
    clicked = pyqtSignal()

    def __init__(self, _port, _stream=False, _update_in_millis=100):
        super().__init__()
        print("Opening Arduino on port " + _port)
        self.update_in_millis = _update_in_millis
        self.stream = _stream
        self.running = False
        self.arduino_port = _port
        self.arduino = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process)
        self.thread = None
        self.prevSensorsValues = [0, 0, 0, 0]
        self.sensorsValues = [0, 0, 0, 0]
        self.buttonState = 0
        self.alive = False

    def readSerial(self):
        while self.alive:
            #print('loop')
            if self.arduino.isOpen():
                #print('loop', 'arduino open')
                try:
                    data = self.arduino.readline()[:-2]  # the last bit gets rid of the new-line chars
                    if data:
                        try :
                            data_string = data.decode("utf8")
                            datas = data_string.split()
                            #print('arduino datas', datas)
                            if len(datas) == 9:
                                self.sensorsValues[0] = (int(datas[1]) - int(datas[0])) / 1024
                                self.sensorsValues[1] = (int(datas[3]) - int(datas[2])) / 1024
                                self.sensorsValues[2] = (int(datas[5]) - int(datas[4])) / 1024
                                self.sensorsValues[3] = (int(datas[7]) - int(datas[6])) / 1024
                                button_value = int(datas[8])
                                if self.buttonState == 1 and button_value == 0:
                                    self.clicked.emit()
                                    self.buttonState = 0
                                elif self.buttonState == 0 and button_value == 1:
                                    self.buttonState = 1

                            else:
                                print('not enough data, needs 8 arguments')
                        except UnicodeDecodeError:
                            pass
                except(SerialException):
                    self.stop()

        if self.arduino.isOpen():
            self.arduino.close()

    def process(self):
        if self.arduino.isOpen():
            if self.stream:
                self.sensors.emit(self.sensorsValues[0], self.sensorsValues[1], self.sensorsValues[2],
                                  self.sensorsValues[3])

            else:
                if (self.sensorsValues[0] != self.prevSensorsValues[0] or
                        self.sensorsValues[1] != self.prevSensorsValues[1] or
                        self.sensorsValues[2] != self.prevSensorsValues[2] or
                        self.sensorsValues[3] != self.prevSensorsValues[3]
                ):
                    self.sensors.emit(self.sensorsValues[0], self.sensorsValues[1], self.sensorsValues[2],
                                      self.sensorsValues[3])

            self.prevSensorsValues = list(self.sensorsValues)

        if self.running:
            self.timer.run()

    def stop(self):
        print('arduino stop')
        self.alive = False
        self.timer.stop()
        self.connection.emit(False)

    def start(self):
        print('arduino start')
        self.arduino = Serial(port=self.arduino_port, baudrate=9600, timeout=0.2)
        self.alive = True
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self.readSerial, daemon=True)
            self.thread.start()
        self.timer.start(self.update_in_millis)
        self.connection.emit(True)
