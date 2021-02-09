from tello import Tello
import sys
from datetime import datetime
import time

start_time = str(datetime.now())

file_name = sys.argv[1]

f = open(file_name, "r")
commands = f.readlines()

tello = Tello()


log = tello.get_log()

out = open('log/' + start_time + '.txt', 'w')
for stat in log:
    stat.print_stats()
    str = stat.return_stats()
    out.write(str)
