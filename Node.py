import time

# This class will represent other nodes in the system
class Node:

    TIMEOUT = 10
    
    def __init__(self, ip,socket, pulse = None):
        self._ip = ip
        self._conn = socket

        # TODO set to now maybe
        self._last_pulse = pulse


    def update_pulse(self):
        # TODO set to now maybe
        self._last_pulse = time.time()


    def is_alive(self):
        return time.time() - self._last_pulse < TIMEOUT


    def send_heartbeat(self):
        self._conn.write("H")

