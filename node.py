import time

# This class will represent other nodes in the system
class Node:

    TIMEOUT = 5000
    
    def __init__(self, host, port, socket, pulse = None):
        self._host = host
        self._port = port
        self._conn = socket

        # TODO set to now maybe
        self._last_pulse = time.time()


    def record_pulse(self):
        # TODO set to now maybe
        self._last_pulse = time.time()

    def is_alive(self):
        return self._conn and (time.time() - self._last_pulse < self.TIMEOUT)

    def close_connection(self):
        self._conn.close()
        self._conn = None

    def set_connection(self, conn):
        self._conn = conn
        self.record_pulse()

    def send_heartbeat(self):
        try:
            self._conn.send(b"H")
        except:
            return False

        return True
        

