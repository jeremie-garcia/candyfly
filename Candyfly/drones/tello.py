import re
import socket
import sys
from threading import Thread

from PyQt5.QtWidgets import QApplication, QPushButton

from drone import Drone


import pyttsx3 as py
import speech_recognition as sr
import vocal_controler_class as vc
import vosk
import argparse
import os
import queue
import sounddevice as sd

import sys

INTERVAL = 1


def clamp(x):
    return round(min(100, max(-100, x)))


class TelloDrone(Drone):

    def __init__(self):
        super().__init__()
        self.local_ip = ''

        # socket for receiving cmd ack
        self.cmd_port = 8889
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_sock.bind((self.local_ip, self.cmd_port))

        # socket for receiving state values
        self.state_port = 8890
        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.bind((self.local_ip, self.state_port))

        self.tello_address = ('192.168.10.1', self.cmd_port)

        self.running = True
        # thread for receiving cmd ack
        self.receive_cmd_thread = Thread(target=self._receive_cmd_thread)
        self.receive_cmd_thread.daemon = True
        self.receive_cmd_thread.start()

        # thread for receiving state
        self.receive_state_thread = Thread(target=self._receive_state_thread)
        self.receive_state_thread.daemon = True
        self.receive_state_thread.start()

        self.state_response = ""
        self.cmd_response = ""
        self.cmd_state = ""
        self._is_flying = False
        self.prev_cmd = ""


        self.q = queue.Queue()


    def send_command(self, cmd):
        self.cmd_sock.sendto(cmd.encode(encoding="utf-8"), self.tello_address)

    def init(self):
        self.cmd_state = "cmd"
        self.connection.emit("off")
        self.send_command('command')

    def take_off(self):
        if not self.is_flying():
            self.cmd_state = "takeoff"
            self.send_command('takeoff')

    def land(self):
        self.cmd_state = "land"
        self.send_command('land')

    def stop(self):
        self.land()
        self.running = False
        self.state_sock.close()
        self.cmd_sock.close()

    def up_by_cm(self, cm):
        #test cm between 20 and 500
        cm = min(500, max(20,cm))
        cmd = f"up {cm}"
        self.send_command(cmd)

    def down_by_cmd(self,cm):
        cm = min(500, max(20, cm))
        cmd = f"down {cm}"
        self.send_command(cmd)

    def left_by_cm(self, cm):
        #test cm between 20 and 500
        cm = min(500, max(20,cm))
        cmd = f"right {cm}"
        self.send_command(cmd)

    def right_by_cm(self, cm : int):
        cm = min(500, max(20, cm))
        cmd = f"left {cm}"
        self.send_command(cmd)

    def forward_by_cm(self,cm:int):
        cm = min(500, max(20, cm))
        cmd = f"forward {cm}"
        self.send_command(cmd)

    def back_by_cm(self,cm:int):
        cm = min(500,max(20,cm))
        cmd = f"back {cm}"
        self.send_command(cmd)

    def CLW_by_cm(self,cm:int):
        cm = min(500,max(20,cm))
        cmd = f"cw {cm}"
        self.send_command(cmd)

    def C_CLW_by_cm(self,cm:int):
        cm = min(500,max(20,cm))
        cmd = f"ccw {cm}"
        self.send_command(cmd)



    def int_or_str(self,text):
        """fonction responsable des arguemnt parsing"""
        try:
            return int(text)
        except ValueError:
            return text

    def callback(self,indata, frames, time, status):
        """Fonction appelé à chaque block d'itaration auditive."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def _receive_cmd_thread(self):
        """Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        while self.running:
            try:
                rep, ip = self.cmd_sock.recvfrom(1024)
                self.cmd_response = rep.decode('utf8')
                if self.cmd_response == 'ok':
                    if self.cmd_state == 'cmd':
                        print('tello connected')
                        self.connection.emit('on')
                    if self.cmd_state == 'takeoff':
                        self._is_flying = True
                        self.is_flying_signal.emit(True)
                    if self.cmd_state == 'land':
                        self._is_flying = False
                        self.is_flying_signal.emit(False)

                    print("command", self.cmd_state, "ACK")
                else:
                    print("command,", self.cmd_state, 'error', self.cmd_response)

                self.cmd_state = ""
            except socket.error as exc:
                print("CMD ERROR: %s" % exc)


    def _receive_state_thread(self):
        """Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        while self.running:
            try:
                rep, ip = self.state_sock.recvfrom(1024)
                self.state_response = rep.decode('utf8')
                self.bat = re.search(r"bat:(\d*)", self.state_response).group()[4:]
                self.batteryValue.emit(int(self.bat) * 0.043)  # hack...
                self.pourcentage_batterie = int(((int(self.bat) * 0.043) / 4.35) * 100)
                self.battery_low_signal.emit(str(self.pourcentage_batterie))
            except socket.error as exc:
                print("CMD ERROR: %s" % exc)

    def is_flying(self):
        return self._is_flying

    def process_motion(self, _up, _rotate, _front, _right):
        '''
        Need to be in -100 100 range for each commands
        '''
        if self.cmd_state != "land" and self.cmd_state != "takeoff":
            velocity_up_down = clamp(_up * 50 * self.max_vert_speed)
            velocity_yaw = clamp(_rotate/180 * 100 * self.max_rotation_speed)
            velocity_front_back = clamp(_front * 50 * self.max_horiz_speed)
            velocity_left_right = clamp(_right * 50 * self.max_horiz_speed)
            cmd = f"rc {velocity_left_right} {velocity_front_back} {velocity_up_down} {velocity_yaw}"
            #print("TELLO:", cmd)
            self.cmd_state = "rc"
            self.send_command(cmd)

"""
    def fonction_nec1(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        args, remaining = self.parser.parse_known_args()

        if args.list_devices:
            print(sd.query_devices())
            self.parser.exit(0)
        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[self.parser])
        self.parser.add_argument(
            '-f', '--filename', type=str, metavar='FILENAME',
            help='audio file to store recording to')
        self.parser.add_argument(
            '-m', '--model', type=str, metavar='MODEL_PATH',
            help='Path to the model')
        self.parser.add_argument(
            '-d', '--device', type=self.int_or_str,
            help='input device (numeric ID or substring)')
        self.parser.add_argument(
            '-r', '--samplerate', type=int, help='sampling rate')
        self.args = self.parser.parse_args(remaining)
        self.fonction_necessaire()

    def fonction_necessaire(self):
        try:
            if self.args.model is None:
                self.args.model = "model"
            if not os.path.exists(self.args.model):
                self.parser.exit(0)
            if self.args.samplerate is None:
                device_info = sd.query_devices(self.args.device, 'input')
                # soundfile considéré comme un int, sounddevice fourni un floattan normalement:
                self.args.samplerate = int(device_info['default_samplerate'])
            model = vosk.Model(self.args.model)
            if self.args.filename:
                dump_fn = open(self.args.filename, "wb")
            else:
                dump_fn = None
            with sd.RawInputStream(samplerate=self.args.samplerate, blocksize=8000, device=self.args.device, dtype='int16',
                                   channels=1, callback=self.callback):
                print('#' * 40)
                print('Appuyez sur  Ctrl+C pour arrêter')
                print('#' * 40)

                rec = vosk.KaldiRecognizer(model, self.args.samplerate)
                while True:
                        data = self.q.get()
                        if rec.AcceptWaveform(data):
                            try:
                                list_phrase = rec.Result().split()[1:-1]
                                list_phrase = " ".join(list_phrase[2:-1])
                                print(list_phrase)
                                if '"décollage"' in list_phrase:
                                    self.take_off()
                                if '"atterrissage"' in list_phrase:
                                    self.land()
                                if '"batterie"' in list_phrase:
                                    pourcentage_batterie = int(((int(self.bat)*0.043)/4.35)*100)
                                    print(pourcentage_batterie, "%")
                                    #self.assistant_temporel.speak("La batterie est {} pourcent".format(self.bat))
                                if '"altitude"' in list_phrase:
                                    print(int(self.state_response.split(";")[9].split(":")[1]),"cm")
                                    #self.assistant_temporel.speak("100m")
                                if '"ok"' in list_phrase:
                                    vc.voice_assistant.speak("je t'écoute bogoss")
                            except:
                                pass
                        else:
                            try:
                                list_phrase_corrige = rec.PartialResult().split()[1:-1]
                                print(list_phrase_corrige)
                                if '"décollage"' in list_phrase_corrige:
                                    self.take_off()
                                if '"batterie"' in list_phrase_corrige:
                                    pourcentage_batterie =int(((int(self.bat)*0.043)/4.35)*100)
                                    print(pourcentage_batterie,"%")
                                if '"altitude"' in list_phrase_corrige:
                                    print(int(self.state_response.split(";")[9].split(":")[1]), "cm")
                                    self.case_altitude = self.state_response.split(";")[9]
                                    self.value_altitude = self.case_altitude.split(":")[1]
                                    self.assistant_temporel.speak("L'altitude est de {} mètre".format(self.value_altitude))
                                if '"atterrissage"' in list_phrase_corrige:
                                    self.land()
                                if '"ok"' in list_phrase_corrige:
                                    vc.voice_assistant.speak("je t'écoute bogoss")
                            except:
                                pass
                        if dump_fn is not None:
                            dump_fn.write(data)
        except KeyboardInterrupt:
            print('\nDone')
            self.parser.exit(0)
        except Exception as e:
            self.parser.exit(type(e).__name__ + ': ' + str(e))
"""
if __name__ == "__main__":
    app = QApplication([])
    tello = TelloDrone()
    button = QPushButton("start")
    stp_button = QPushButton("stop")
    button.clicked.connect(tello.take_off)
    stp_button.clicked.connect(tello.land)
    button.show()
    stp_button.show()


    tello.batteryValue.connect(lambda status: print('batt', status))
    tello.is_flying_signal.connect(lambda status: print('flying?', status))
    tello.connection.connect(lambda status: print('connection', status))

    tello.init()
    assistant = tello
    assistant.fonction_nec1()
    sys.exit(app.exec_())
    tello.stop()
