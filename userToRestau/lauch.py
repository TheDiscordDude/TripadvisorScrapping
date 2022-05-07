import time
import os
import psutil

current_time = time.time()
os.system('./runme.sh&')
print("Here")
while True:
    if current_time + 1 * 3600 < time.time():
        print("Restarting the program")
        os.system('./runme.sh&')
        current_time = time.time()

    last_received = psutil.net_io_counters().bytes_recv
    time.sleep(1)
    new_received = psutil.net_io_counters().bytes_recv
    total_received = (new_received - last_received) / 1024
    if total_received < 0.07:
        os.system('./runme.sh&')

    time.sleep(9)
