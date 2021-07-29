# Candyfly: Supporting people with disabilities to fly drones

This is an open-source project developped by ENAC - Articlect FabLab and Elheva

#installation
The python code requires the follwing dependencies to be satisfied
pygame
pyqt5
pyserial
cflib
openCv
os
vosk (vocal recognition package)
argparse

#Downlaod the model data base through this link by choosing your language.
https://alphacephei.com/vosk/models

#Adding file
A 3Go Model File will be need to enable the vocal recognition call model (please do not change the name of that file)

#Vocal Command Guide:
Say:  "l'altitude"                                                                              --->  order: get the current altitude
say:  "batterie or la batterie"                                                                 ----> order: get the current battery level (%)
say:  "décollage" or "on décolle"                                                               ----> order: tell will take off
#wait 3 seconds after each take off time before sending commands
say:  "monter" or "gauche" or "recule" or "droite" or "descend" or "tout droit" or "avance"     ----> order: move 30cm to the direction 
say:  "monte de 50cm" (40,50,60,70,80,90,100cm, 2m,3m,4m,5m)                                    ----> order: move up with accurate distance
say:  "va à gauche de 50cm" (40,50,60,70,80,90,100cm, 2m,3m)                                    ----> order: move to the left with accurate distance
say:  "va à droite de 50 cm" (40,50,60,70,80,90,100cm, 2m,3m)                                   ----> order: move to the right withe accurate distance
say:  "avance de 50 cm" (40,50,60,70,80,90,100cm, 2m,3m)                                        ----> order: move forwards with accurate distance
say:  "recule de 50 cm" (40,50,60,70,80,90,100cm, 2m,3m)                                        ----> order: move back with accurate distance
say:  "Stop"                                                                                    ----> order: drone will keep it's position
say:  "dis moi ce qu'il y a dans 5 m" (2m, 3m, 5m)                                              ----> order: drone will move 5 metre forward 
say:  "Merci"                                                                                   ----> order: drone will reply you
say:  "dépêche"                                                                                 ----> order: drone will reply you
press on the 'c' button (for at least one full second) to capture the image, the detection result will be save into Image_detection, and then drone will go back to the initial place.

#To save the image in the right place, don't forget to change the absolute directory in TelloVoiceObjectReco
#If you want to have gesture control without the camera streaming code, juste run the tellovoice_reco will be enough.


Thank you, enjoy your moment with your drone