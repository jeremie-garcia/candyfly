from serial import Serial, SerialException
from serial.tools.list_ports import comports
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QTimer
from threading import Thread


def find_available_arduinos():
    ports = list(comports(False))
    arduino_ports = [
        p.device
        for p in comports()
        if (("usb" or "tty" or "arduino") in str(p.device).lower()) or ("arduino" in str(p.description).lower())
    ]
    return arduino_ports


class ArduinoController(QObject):
    connection = pyqtSignal(bool)
    sensors = pyqtSignal(float, float, float, float)

    def __init__(self, _port, _stream=False, _update_in_millis=50):
        super().__init__()
        print("Opening Arduino on port " + _port)
        self.update_in_millis = _update_in_millis
        self.stream = _stream
        self.running = False
        self.arduino_port = _port
        self.arduino = Serial(port=self.arduino_port, baudrate=9600, timeout=0.2)
        self.timer = QTimer()
        self.timer.timeout.connect(self.process)
        self.thread = Thread(target=self.readSerial, daemon=True)
        self.prevSensorsValues = [0, 0, 0, 0]
        self.sensorsValues = [0, 0, 0, 0]
        self.alive = False

    def readSerial(self):
        while self.alive:
            if self.arduino.isOpen():
                try:
                    data = self.arduino.readline()[:-2]  # the last bit gets rid of the new-line chars
                    if data:
                        data_string = data.decode("utf8")
                        datas = data_string.split()
                        if len(datas) == 8:
                            self.sensorsValues[0] = (int(datas[1]) - int(datas[0])) / 1024
                            self.sensorsValues[1] = (int(datas[3]) - int(datas[2])) / 1024
                            self.sensorsValues[2] = (int(datas[5]) - int(datas[4])) / 1024
                            self.sensorsValues[3] = (int(datas[7]) - int(datas[6])) / 1024
                        else:
                            print('not enough data, needs 8 arguments')
                except(SerialException):
                    self.stop()

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
        self.connection.emit(False)
        self.timer.stop()
        # self.thread.stop()
        self.arduino.close()
        self.alive = False

    def start(self):
        self.alive = True
        self.connection.emit(True)
        self.timer.start(self.update_in_millis)
        self.thread.start()
        self.arduino = Serial(port=self.arduino_port, baudrate=9600, timeout=0.2)
