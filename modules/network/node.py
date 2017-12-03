import time

# This class will represent other nodes in the system
class Node:

    # Current heartrate is 0.2/sec, so this gives us time to miss
    # at most 1 heartbeat before we consider it dead.
    TIMEOUT = 12
    DELIMITER = "-"
    
    def __init__(self, host, port, socket):
        self._host = host
        self._port = port
        self._conn = socket

        self._last_heartbeat = time.time()

    def host(self):
        return self._host

    def record_heartbeat(self):
        self._last_heartbeat = time.time()

    def is_alive(self):
        return self._conn and (time.time() - self._last_heartbeat < self.TIMEOUT)

    def close_connection(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def send_heartbeat(self):
        return self._send_message("H")
    
    def send_id(self, id):
        return self._send_message("ID" + self.DELIMITER + str(id))

    def send_host(self, host):
        return self._send_message("HOST" + self.DELIMITER + str(host))

    def _send_message(self, msg):
        try:
            self._conn.send(str.encode(msg))
        except:
            return False

        return True


        

        

