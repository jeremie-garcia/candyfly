import sys
from threading import Thread

from PyQt5.QtCore import QObject, QThread, QCoreApplication
from time import sleep

from PyQt5.QtWidgets import QApplication

from drones.drone import Drone
import socket
import re

INTERVAL = 1

class TelloDrone(Drone):

    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip = ''
        local_port = 8890
        self.sock.bind((local_ip, local_port))

        self.connection.emit("progress")
        print("connecting to tello drone")
        self.tello_address = ('192.168.10.1', 8889)
        self.sock.sendto('command'.encode(encoding="utf-8"), self.tello_address)
        self.connection.emit("on")
        print('connected')


        self.running = False

    def start_logger(self):
        self.thread = Thread(target=self.read_socket, daemon=True)
        self.thread.start()

    def take_off(self):
        self.sock.sendto('takeoff'.encode(encoding="utf-8"), self.tello_address)

    def land(self):
        self.sock.sendto('land'.encode(encoding="utf-8"), self.tello_address)

    def stop(self):
        self.sock.sendto('land'.encode(encoding="utf-8"), self.tello_address)
        self.running.stop()
        self.sock.close()

    def read_socket(self):
        self.running = True
        try:
            while self.running:
                response, ip = self.sock.recvfrom(1024)
                response = response.decode('utf-8')
                if response == 'ok':
                    continue
                bat = re.search(r"bat:(\d*)", response).group()[4:]
                self.batteryValue.emit(int(bat))
                sleep(INTERVAL)
        except KeyboardInterrupt:
            print('stopped')



    def process_motion(self, _up, _rotate, _front, _right):
        '''
        Need to be in -100 100 range for each commands
        '''
        velocity_up_down = _up * 100 * self.max_vert_speed
        velocity_yaw = _rotate * 100 * self.max_rotation_speed
        velocity_front_back = _front * 100 * self.max_horiz_speed
        velocity_left_right = _right * -1 * 100 * self.max_horiz_speed
        cmd = str(velocity_left_right, velocity_front_back, velocity_up_down, velocity_yaw).encode(encoding="utf-8")
        print("TELLO to " , cmd)
        self.sock.sendto(cmd, self.tello_address)

if __name__ == "__main__":
    app = QApplication([])
    tello = TelloDrone()
    tello.start_logger()
    tello.batteryValue.connect(print)
    tello.take_off()
    sleep(8)
    tello.land()
    sys.exit(app.exec_())