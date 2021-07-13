from PyQt5.QtWidgets import QApplication, QPushButton
import os
import sys
import tello
import list_commands

DECOLLAGE = "décollage"
BATTERIE = "batterie"
ATTERRISSAGE = "atterrissage"
ALTITUDE = "altitude"
MERCI = "merci"
ALLER = "aller"
MONTER = "monter"
FLIP = "flip"
DESCENDRE = "descendre"
GAUCHE = "gauche"
DROITE = "droite"
STOP = "stop"
COUPER = "coupez"
CLOCKWISE = "clockwise"
C_CLOCKWISE = "counter_clockwise"
AVANCER = "avancer"
RECULER = "reculer"

class TelloVoice(tello.TelloDrone):
    """classe responsable du contrôle vocal"""
    def __init__(self):
        tello.TelloDrone.__init__(self)
        #list des commandes porbable
        self.decollage_list = list_commands.decollage_list
        self.atterissage_list = list_commands.atterissage_list
        self.altitude_list = list_commands.altitude_list
        self.batterie_list = list_commands.batterie_list
        self.merci_list = list_commands.merci_list
        self.aller_list = list_commands.aller_list
        self.MONTER_list = list_commands.MONTER_list
        self.DESCENDRE_list = list_commands.DESCENDRE_list
        self.FLIP_list = list_commands.FLIP_list
        self.GAUCHE_list = list_commands.GAUCHE_list
        self.DROITE_list = list_commands.DROITE_list
        self.AVANCE_list = list_commands.AVANCE_list
        self.GO_UP_list = list_commands.GO_UP_list
        self.GO_DOWN_list = list_commands.GO_DOWN_list
        self.RECULE_list = list_commands.RECULE_list
        self.AVANCE_list = list_commands.AVANCE_list
        self.AVANCE_PRECIS_list = list_commands.ANANCE_PRECISE_list
        self.STOP_list = list_commands.STOP_list
        self.EMERGENCY_list = list_commands.EMERGENCY_list

        #boolen for battery warning
        self.boolean_battery = True

    def speak(self,str,rate):
        """entrer un string pour que l'assistant vocal le dit à voix haute"""
        os.system('say --rate=%d %s' %(rate,str))

    def number_conversion(self,str):
        try:
            if str == "vingt":
                return int(20)
            elif str == "trente":
                return int(30)
            elif str == "quarante":
                return int (40)
            elif str == "cinquante":
                return int(50)
            elif str == "soixante":
                return int(60)
            elif str == "soixante-dix":
                return int(70)
            elif str == "quatre-vingts":
                return int(80)
            elif str == "quatre-vingt-dix":
                return int(90)
            elif str == "cent":
                return int(100)
        except:
            pass

    def warning_batterie(self,value):
        """fonction de rappelle pour batterie"""
        if self.pourcentage_batterie < 20 and self.boolean_battery:
            self.speak("il vous reste plus beaucoup de batterie",220)
            self.boolean_battery =False

    def filtration_command(self,commands):
        """fonction qui identifie la commande """
        print("Entendu : {}".format(commands))
        try:
            if commands in self.decollage_list:
                return DECOLLAGE
            if commands in self.atterissage_list:
                return  ATTERRISSAGE
            if commands in self.altitude_list:
                return ALTITUDE
            elif commands in self.batterie_list:
                return BATTERIE
            elif commands in self.merci_list:
                return MERCI
            elif commands in self.aller_list:
                return ALLER
            elif commands in self.MONTER_list:
                return MONTER
            elif commands in self.FLIP_list:
                return FLIP
            elif commands in self.DESCENDRE_list:
                return DESCENDRE
            elif commands in self.GAUCHE_list:
                return GAUCHE
            elif commands in self.DROITE_list:
                return DROITE
            elif commands in self.AVANCE_list:
                return AVANCER
            elif commands in self.RECULE_list:
                return RECULER
            elif commands in self.STOP_list:
                return STOP
            elif commands in self.EMMERGENCY_list:
                return COUPER
            return "pas compris"
        except:
            pass

    def filtration_command_valeur(self,commands):
        """fonction qui identifie la commande sachant les valeurs"""
        try:
            if commands in self.GO_UP_list:
                return MONTER
            elif commands in self.GO_DOWN_list:
                return DESCENDRE
            elif commands in self.DROITE_list:
                return DROITE
            elif commands in self.GAUCHE_list:
                return GAUCHE
            elif commands in self.AVANCE_PRECIS_list:
                return AVANCER
            elif commands in self.RECULE_list:
                return RECULER
            elif commands in list_commands.CLOCKWISE_list:
                return CLOCKWISE
            elif commands in list_commands.CLOCKWISE_list:
                return C_CLOCKWISE
            return "pas compris"
        except:
            pass

    def process_voice_command(self, commands):
        """fonction action """
        mess =str(self.filtration_command(commands))
        print("CMD retenu = ",mess)
        if (mess == DECOLLAGE):
            self.take_off()
        if(mess == BATTERIE):
            self.speak("La batterie est de {} pourcent".format(self.pourcentage_batterie), 200)
        elif (mess == ATTERRISSAGE):
            self.land()
        elif (mess==ALTITUDE):
            self.case_altitude = self.state_response.split(";")[9]
            self.value_altitude = self.case_altitude.split(":")[1]
            self.speak("Laltitude est de {} centimètre".format(int(self.value_altitude)),200)
        elif (mess == MERCI):
            self.speak("tinqiète bogoss",280)
        elif (mess == ALLER):
            self.speak("t'énerve pas s'il te plait",290)
        elif (mess == FLIP):
            self.send_command("flip b")
        elif (mess == DESCENDRE):
            self.send_command("down 30")
        elif (mess == MONTER):
            self.send_command("up 30")
        elif (mess == GAUCHE):
            self.send_command("right 30")
        elif (mess == DROITE):
            self.send_command("left 30")
        elif (mess==AVANCER):
            self.send_command("forward 30")
        elif (mess==RECULER):
            self.send_command("back 30")
        elif (mess == STOP):
            self.send_command("stop")
        elif (mess == COUPER):
            self.send_command("emergency")
        else:
           print("Je ne connais pas cette commande", mess)

    def process_motion_command(self,commands,valeur):
        """fonction proccess with accurate commands"""
        mess = str(self.filtration_command_valeur(commands))
        print(f'CMD = {mess} : valeur = {valeur}')
        if (mess == GAUCHE):
            self.left_by_cm(int(valeur))
            print("okayyyy")
        elif (mess == DROITE):
            self.right_by_cm(int(valeur))
            print("okayyyy")
        elif (mess==MONTER):
            self.up_by_cm(int(valeur))
        elif (mess == DESCENDRE):
            self.down_by_cmd(int(valeur))
        elif (mess==AVANCER):
            self.forward_by_cm(int(valeur))
        elif (mess==RECULER):
            self.back_by_cm(int(valeur))
        elif (mess==CLOCKWISE):
            self.CLW_by_cm(int(valeur))
        elif (mess==C_CLOCKWISE):
            self.C_CLW_by_cm(int(valeur))
        else:
            print("Je ne connais pas cette commande",mess)



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
