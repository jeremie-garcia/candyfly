import pyttsx3 as py
import speech_recognition as sr
import vosk
import argparse
import os
import queue
import sounddevice as sd
import sys

# tx = input("Text to say >>> ")
# tx = repr(tx)
# print(tx)
# print(type(tx))
import os
import platform
"""

a = "bonjour"

syst = platform.system()
if syst == 'Linux' and platform.linux_distribution()[0] == "Ubuntu":
    os.system('spd-say %s' % a)
elif syst == 'Windows':
    os.system('PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(%s);"' % tx)
elif syst == 'Darwin':
    os.system('say %s' % a)
else:
    raise RuntimeError("Operating System '%s' is not supported" % syst)
"""

print('a' == "a")
prenom = 'alain'
print(prenom)
print(prenom.replace('"',''))

print('a'=='"a')

os.system('say %s' %prenom)