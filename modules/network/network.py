import json
import socket
import logging
import sys
from threading import Lock
from .entity import Entity
from .node import Node
from .networkconfig import NetworkConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')

h = logging.FileHandler('logs/debug.log')
h.setLevel(logging.NOTSET)
h.setFormatter(formatter)

h2 = logging.FileHandler('logs/info.log')
h2.setLevel(logging.INFO)
h2.setFormatter(formatter)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(h)
logger.addHandler(h2)
logger.addHandler(ch)

class Network:
    LISTEN_PORT = 8889
    TESTING_MODE = False

    def __init__(self, me, test):
        self._me = me
        self.TESTING_MODE = test

        self._nodes = {}
        self._seen = set()
        self._new = set()
        self._connected = set()
        self._verified = set()
        self._config = NetworkConfig()
        self._authorized = set()

        self._lock = Lock()

        self._load_from_config()


######################################
## Network Outgoing Interface
#####################################

    def connect_to_host(self, host):
        if host in self._connected:
            return False

        logger.info("Network: Attempting to connect to %s" % (host))

        try:
            # Connect to host
            # for testing locally: 8825 -> 8826 and 8826 -> 8825
            test_port = 8825 + (self._me.port % 2)
            port = test_port if self.TESTING_MODE else self.LISTEN_PORT

            conn = socket.create_connection((host, port), 1)
            node = Node(host, port, conn)

            # send host your credentials
            node.send_verification(self._me.id)

            # add node to all relevant sets
            self._nodes[host] = node
            self._connected.add(host)
            self._seen.add(host)
            if host not in self._seen:
                self._new.add(host)

            msg_end = "Awaiting verification..." if not host in self._verified else "Connection and verification complete!"
            logger.info("Network: Connection to %s succeeded. %s" % (host, msg_end))
            return True
        except:
            logger.info("Network: Connection to %s failed" % (host))
            return False

    def disconnect_from_host(self, host):
        if host in self._connected: self._connected.remove(host)
        if host in self._verified: self._verified.remove(host)
        if host in self._nodes: self._nodes[host].close_connection()
        logger.info("Network: %s disconnected" % (host))


    def broadcast_heartbeats(self):
        try:
            for host in self._connected:
                if host in self._verified:
                    if self._nodes[host].send_heartbeat():
                        logger.debug("Network: Heartbeat sent to %s" % (host))
                    else:
                        logger.error("Network: Heartbeat to %s failed" % (host))
                        self.disconnect_from_host(host)
        except RuntimeError:
            # This is from _connected changing size
            pass


    def broadcast_host(self, new_host):
        if new_host not in self._verified:
            logger.warning("Network: Shouldn't broadcast an unverified host")
            return

        try:
            logger.info("Network: Broadcasting %s" % (new_host))
            for host in self._connected:
                if host in self._verified and not host == new_host:
                    self._nodes[host].send_host(new_host)
        except RuntimeError:
            # This is from _connected changing size
            pass

    def send_dfs(self, files, host):
        pass

    def send_file(self, host, file_name):
        if not self.connected(host):
            print("Tried to send file to disconnected host")
            return
        
        self._nodes[host].send_file(file_name)
    
    def send_network_info(self, host):
        if not host in self._nodes:
            return

        node = self._nodes[host]
        node.send_verified_ids(list(self._authorized))

        # send hosts

######################################
## Network Internal Interface
#####################################
    def print_all(self):
        print(self._nodes)
        print(self._new)
        print(self._seen)
        print(self._connected)
        print(self._verified)
        print(self._authorized)

    def startup(self):
        try:
            for host in self._seen:
                self.connect_to_host(host)
        except RuntimeError:
            # This is from hosts being added to _seen
            pass

    def verify_host(self, host, id):
        verified = id in self._authorized

        if verified:
            msg_end = "Awaiting connection..." if not host in self._connected else "Connection and verification complete!"
            logger.info("Network: %s identity verified as %s. %s" % (host, id, msg_end))
            self._verified.add(host)

            # if this is a new host save it
            if (host not in self._seen or host in self._new) and not self.TESTING_MODE:
                self._config.store_host(host)
                self._new.add(host)
        else:
            logger.info("Network: %s identity %s not recognized" % (host, id))

            # if there is a connection get rid of it
            if host in self._nodes:
                self.disconnect_from_host(host)

        return verified

    def record_heartbeat(self, host):
        if not host in self._nodes:
            logger.error("can't recieve heartbeat from nonexistent node")
            return
        self._nodes[host].record_heartbeat()

    def connected(self, host):
        if not host in self._connected: return False

        node = self._nodes[host]
        alive = node.is_alive()

        if not alive:
            self.disconnect_from_host(host)

        return alive

    def verified(self, host):
        return host in self._verified

    def get_seen_nodes(self):
        return list(self._seen)

    def get_connected_nodes(self):
        return list(self._connected)

    def toggle_debug(self):
        if (logger.handlers[2].level != logging.DEBUG):
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.WARNING)

    def toggle_info(self):
        if (logger.handlers[2].level != logging.INFO):
            ch.setLevel(logging.INFO)
        else:
            ch.setLevel(logging.WARNING)

######################################
## Helper Functions
#####################################

    def _load_from_config(self):
        for host in self._config.hosts():
            # don't add self (for running local test)
            if not self.TESTING_MODE and not host == self._me.host:
                self._seen.add(host)

        self._authorized = set(self._config.identities())
