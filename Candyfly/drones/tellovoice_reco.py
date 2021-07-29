from threading import Thread
from PyQt5.QtWidgets import QApplication, QPushButton
import vosk
import argparse
import os
import queue
import sounddevice as sd
import sys
import telloVoice


class TelloVoiceReco(telloVoice.TelloVoice):
    """classe responsable du contrôle vocal"""
    def __init__(self):
        telloVoice.TelloVoice.__init__(self)

        #implemente à l'ajout multi-process pour les threads
        self.q = queue.Queue()

        # thread for speech recognizing
        self.reco_thread = Thread(target=self._process_reco_thread)
        self.reco_thread.daemon = True
        self.reco_thread.start()

        self.text_signal_1.connect(self.process_voice_command)
        self.text_signal_2.connect(self.process_motion_command)

    """The next two are Offline require fonction"""
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

    def _process_reco_thread(self):
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
                while self.running:
                        data = self.q.get()
                        if rec.AcceptWaveform(data):
                            try:
                                self.entendu_phrase = str(rec.Result().split(":")[1].replace("}","").replace('"','').strip())
                                print(self.entendu_phrase)
                                if len(self.entendu_phrase.split()) <= 3:
                                    for mot in self.entendu_phrase.split():
                                        self.chaque_mot = mot.replace('"', '')
                                        #print(self.chaque_mot)
                                        self.text_signal_1.emit(str(self.chaque_mot))

                                else:
                                    self.value_2_int= self.number_conversion(str(self.entendu_phrase.split()[-2]))
                                    self.text_signal_2.emit(str(self.entendu_phrase),str(self.value_2_int))
                            except:
                                pass
                        if dump_fn is not None:
                            dump_fn.write(data)
        except KeyboardInterrupt:
            print('\nDone')
            self.parser.exit(0)
        except Exception as e:
            self.parser.exit(type(e).__name__ + ': ' + str(e))

    def warning_batterie(self,value):
        """fonction de rappelle pour batterie quand elle est en dessous de 20%"""
        if self.pourcentage_batterie < 20 and self.boolean_battery:
            self.speak("il vous reste plus beaucoup de batterie",220)
            self.boolean_battery =False

if __name__ == "__main__":
    app = QApplication([])
    tello = TelloVoiceReco()
    button = QPushButton("start")
    stp_button = QPushButton("stop")
    button.clicked.connect(tello.take_off)
    stp_button.clicked.connect(tello.land)
    button.show()
    stp_button.show()
    tello.battery_low_signal.connect(lambda value : tello.warning_batterie(value))
    #tello.batteryValue.connect(lambda status: print('batt', status))
    tello.is_flying_signal.connect(lambda status: print('flying?', status))
    tello.connection.connect(lambda status: print('connection', status))
    tello.init()
    sys.exit(app.exec_())
    tello.stop()
