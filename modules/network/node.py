import time
from threading import Lock # _lock
from .messagetags import MessageTags

# This class will represent other nodes in the system
# Soft state:
#   _host: ip address of connection
#   _port: port of connection
#   _conn: socket object for connection
#   _last_heartbeat: timestamp of last-received heartbeat from node
#   _lock: Thread safety for message transmission
class Node:

    # Current heartrate is 0.2/sec, so this gives us time to miss
    # at most 1 heartbeat before we consider it dead.
    TIMEOUT = 12

    def __init__(self, host, port, socket):
        self._host = host
        self._port = port
        self._conn = socket

        self._last_heartbeat = time.time()

        self._lock = Lock()

    def host(self):
        return self._host

    # Not currently useful
    def record_heartbeat(self):
        self._last_heartbeat = time.time()

    # Confirms that node is alive
    def is_alive(self):
        return self._conn and (time.time() - self._last_heartbeat < self.TIMEOUT)

    # Closes socket.
    def close_connection(self):
        self._lock.acquire()
        try:
            if self._conn:
                self._conn.close()
                self._conn = None
        except:
            pass
        finally:
            self._lock.release()

    # Sends single byte message as heartbeat to host. Primarily used to test
    # the connection; if it doesn't go through, we assume the host is down.
    def send_heartbeat(self):
        msg = MessageTags.HEARTBEAT + "2" + MessageTags.DELIM + "hi"
        return self._send_message(msg)

    # Identifies self to host
    def send_id(self, id):
        msg = MessageTags.VERIFY + str(len(id)) + MessageTags.DELIM + str(id)
        return self._send_message(msg)

    # Sends new node information to host
    def send_host(self, host):
        msg = MessageTags.HOST + str(len(host)) + MessageTags.DELIMITER + str(host)
        return self._send_message(msg)

    # Since network.py will theoretically be sending heartbeats and other messages on different
    # threads (but on the same port), it's important to lock around the
    def _send_message(self, msg):
        self._lock.acquire()
        try:
            print("Sending message %s" % (msg))
            self._conn.send(str.encode(msg))
        except:
            self._lock.release()
            return False

        self._lock.release()
        return True
