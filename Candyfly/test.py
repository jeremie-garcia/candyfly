import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit
import pygame
from pygame import joystick

from serial import Serial, SerialException
from serial.tools.list_ports import comports

import cflib.crtp

# TODO: this is a test file for pyintaller with all dependecies
# Initialize the low-level drivers (don't list the debug drivers)
cflib.crtp.init_drivers(enable_debug_driver=False)


def find_available_drones():
    return cflib.crtp.scan_interfaces()


app = QApplication(sys.argv)

root = QWidget()
root.resize(320, 240)
root.setWindowTitle('Hello, world!')
text = QLineEdit("test")
text.setParent(root)
root.show()


def find_available_frsky_ids():
    pygame.init()
    if joystick.get_init():
        joystick.quit()

    joystick.init()
    frsky_ids = [
        i
        for i in range(joystick.get_count())
        if ("frsky") in joystick.Joystick(i).get_name().lower()
    ]
    return frsky_ids


def find_available_arduinos():
    ports = list(comports(False))
    arduino_ports = [
        p.device
        for p in comports()
        if ("usb" or "tty" or "arduino") in str(p.device).lower()
    ]
    return arduino_ports


text.setText(str(find_available_arduinos()))
app.exec()
