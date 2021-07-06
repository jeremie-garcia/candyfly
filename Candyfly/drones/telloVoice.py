from threading import Thread
from PyQt5.QtWidgets import QApplication, QPushButton
import vosk
import argparse
import os
import queue
import sounddevice as sd
import sys
import tello

DECOLLAGE = "décollage"


class TelloVoice(tello.TelloDrone):

    """classe responsable du contrôle vocal"""
    def __init__(self):
        tello.TelloDrone.__init__(self)
        #list des commandes porbable
        self.decollage_list = ["décollage","déollage","décolle","l'ouvrage","d'école","décollez","d'accord","toi","paul","vol","terasse","décoller","collège","nicolas","deco","désolé","désolée","l'épauler","collègiens","coulées","bébé","les","volets","dévoilé","dévoilée","douleur","voilet","poulet","épaulé","poète","togolais","débra","découvrez","dec","dès","collègues","nicolas","découverte","eco","des"]
        self.atterissage_list = ["atterissage","attends","atterrissage","matrix","mathrix","matrice","atteris","interieur","intérieur","attends","ça","stop","descends","casse-toi","descendre","patère","terre","adieu","rien","puissant","acquérir"]
        self.altitude_list = ["altitude","attitude","aptitude","l'attitude","article","hauteur","auteur","humm","hum","julie","joli","joli"]
        self.batterie_list = ["batterie","bat","paris","Paris","battez","entrée","Papa","prix","varient","varie","vatican","après","patrick","s'entasse","pourcentage","il","ville","pile"]
        self.merci_list = ["merci","beaucoup","thanks","trop","sympa"]
        self.aller_list =["dépeche","vite","putain","merde","dépêche-toi","allez","bon"]

        #implementer l'ajout multi-process pour les threads
        self.q = queue.Queue()

        # thread for speech recognizing
        self.reco_thread = Thread(target=self._process_reco_thread)
        self.reco_thread.daemon = True
        self.reco_thread.start()

        self.text_signal_1.connect(lambda value:  self.process_voice_command(value))

    def speak(self,str,rate):
        """entrer un string pour que l'assistant vocal le dit à voix haute"""
        os.system('say --rate=%d %s' %(rate,str))

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
                                #print([str(x).replace('"','') for x in rec.Result().split()[3:-1]])
                                for mot in rec.Result().split()[3:-1]:
                                    chaque_mot = mot.replace('"','')
                                    print(chaque_mot)
                                    self.text_signal_1.emit(str(chaque_mot))
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
        """fonction de rappelle pour batterie"""
        self.speak("il vous reste plus beaucoup de batterie")

    def filtration_command(self,commands):
        """fonction qui identifie la commande """
        try:
            if commands in self.decollage_list:
                return DECOLLAGE
            if commands in self.atterissage_list:
                return  "atterrissage"
            if commands in self.altitude_list:
                return "altitude"
            elif  commands in self.batterie_list:
                return "batterie"
            elif  commands in self.merci_list:
                return "merci"
            elif  commands in self.aller_list:
                return "aller"
        except:
            pass

    def process_voice_command(self, commands):
        """fonction action """
        mess =str(self.filtration_command(commands))
        print(mess)
        if (mess == DECOLLAGE):
            self.take_off()
        if(mess == "batterie"):
            #print("batterie okay")
            self.speak("La batterie est de {} pourcent".format(self.pourcentage_batterie), 200)
        elif (mess == "atterrissage"):
            self.land()
        elif (mess=="altitude"):
            self.case_altitude = self.state_response.split(";")[9]
            self.value_altitude = self.case_altitude.split(":")[1]
            self.speak("Laltitude est de {} centimètre".format(int(self.value_altitude)),200)
        elif (mess == "merci"):
            #print("merci = entendu")
            self.speak("tinqiète bogoss",280)
        elif (mess == "aller"):
            # print("merci = entendu")
            self.speak("t'énerve pas s'il te plait",290)
        else:
           print("Je ne connais pas cette commande", mess)


if __name__ == "__main__":
    app = QApplication([])
    tello = TelloVoice()
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
