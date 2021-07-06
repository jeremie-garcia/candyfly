import pyttsx3 as py
import speech_recognition as sr
import vosk
import argparse
import os
import queue
import sounddevice as sd
import sys


class voice_assistant():
    def __init__(self):
        self.engine = py.init()                                                 #on crée un objet
        self.voices = self.engine.getProperty('voices')                         #Obtenir les détails de la voie actuelle inexistante, c'est une liste d'objet "voice"
        self.indice = int(38)
        self.lang = self.voices[self.indice].languages                          #on récupère l'indice de la langue française_France, car il y a français Québéquois etc
        self.genre = "VoiceGenderMale"
        self.engine.setProperty('voice', self.voices[38].id)                    #on initialise la langue en français
        self.q = queue.Queue()  # maxsize est un entier définissant le nombre maximal d'éléments pouvant être mis dans la file. L'insertion sera bloquée lorsque cette borne supérieure sera atteinte,


    def speak(self,str):
        """entrer un string pour que l'assistant vocal le dit à voix haute"""
        self.engine.say(str)
        self.engine.runAndWait()


    def change_language(self, language='fr_FR', genre='VoiceGenderFemale'):
        """changer de langue / veuillez consulter le dictionnaire en txt"""
        res = []
        for (indice,voix) in enumerate(self.voices):
            try:
                if language in voix.languages and genre == voix.gender:
                    while len(res) < 1:                                     #On s'arrête à la première voix utilisable
                        res.append(voix.id)
                        self.engine.setProperty('voice',res[0])           # Avec le bon identifiant de la voix correspondante
                        self.indice = indice
                        self.speak("done")
                        print("voice_changing successfully avec indice {}".format(self.indice))
            except:
                    self.speaker("echec, please retry")
                    raise Exception("Language '{}' pour le genre '{}' est introuvable".format(language, genre))


    def change_vitesse(self,coef):
        """changement de vitesse vocal le coefficient 200 représente une vitesse vocal normal"""
        self.engine.setProperty('rate',coef)


    def change_volume(self,coef):
        """changement de volume, le coefficient est comrpis entre 0 et 1"""
        self.engine.setProperty('volume',coef)


    def __repr__(self):
        """afficher les propriétés de la voix actuelles"""
        identifiant = self.voices[self.indice].id
        nom = self.voices[self.indice].name
        langue = self.voices[self.indice].languages
        return ("L'ID  :  {} \n Nom : {} \nLangue : {}\n ".format(identifiant, nom, langue))


    def reconnaissance_vocal(self,str):
        """"fonction responsable de la reconnaissance vocal plus commande"""
        self.reconnaissance_object = sr.Recognizer()  # On crée un object pour faire de la reconnaissance vocal
        self.speak("je t'écoute Bogoss")
        with sr.Microphone() as source:
            try:
                print("Parlez maintenant")
                self.audio_data = self.reconnaissance_object.listen(source)
                print("patientez svp, on bosse dur là...")
                self.text = self.reconnaissance_object.recognize_google(self.audio_data,language ="fr")
                print(self.text)
                self.phrase = self.text.split()
                self.mot1, self.mot2= "batterie", "Batterie"
                if self.mot1 in self.phrase or self.mot2 in self.phrase:
                    self.speak("str")
                else:
                    self.speak("pas comprendo")
            except sr.UnknownValueError:
                self.speak("on a pas compris")
            except InterruptedError:
                pass



    """"toute la suite représente des fonctions qui ne peut ne pas fonctionner quand il n'y pas de wifi ou connexion tout court"""
    def int_or_str(self,text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text


    def callback(self,indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))


    def fonction_nec1(self,cas1 = None):
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
        self.fonction_necessaire(cas1)

    def fonction_necessaire(self,cas1 =None):
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
                print('Press Ctrl+C to stop the recording')
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
                                    print(1)
                            except:
                                pass
                        else:
                            try:
                                print(rec.PartialResult().split()[1:-1])
                            except:
                                pass
                        if dump_fn is not None:
                            dump_fn.write(data)
        except KeyboardInterrupt:
            print('\nDone')
            self.parser.exit(0)
        except Exception as e:
            self.parser.exit(type(e).__name__ + ': ' + str(e))




if __name__ == '__main__':
    assistant = voice_assistant()
    assistant.speak("bonjour mon age est {}".format(3))
    assistant.change_language('en_US','VoiceGenderFemale')
    #assistant.change_vitesse(300)
    #assistant.change_volume(1)
    #assistant.speak("hello")
    #print(assistant)
    assistant.reconnaissance_vocal("la batterie est de 50%")
    #assistant.fonction_nec1()

