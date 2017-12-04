import json
import socket
from threading import Lock
from .entity import Entity
from .node import Node
from .networkconfig import NetworkConfig

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
        self._identities = set()

        self._lock = Lock()

        self._load_from_config()

    
######################################
## Network Outgoing Interface
#####################################
                
    def connect_to_host(self, host):
        if host in self._connected:
            return False

        print("Network: Attempting to connect to %s" % (host))

        try:
            # Connect to host
            # for testing locally: 8825 -> 8826 and 8826 -> 8825
            test_port = 8825 + (self._me.port % 2)
            port = test_port if self.TESTING_MODE else self.LISTEN_PORT

            conn = socket.create_connection((host, port), 1)
            node = Node(host, port, conn)

            # send host your credentials
            node.send_id(self._me.id)

            # add node to all relevant sets
            self._nodes[host] = node
            self._connected.add(host)
            self._seen.add(host)
            if host not in self._seen:
                self._new.add(host)

            msg_end = "Awaiting verification..." if not host in self._verified else "Connection and verification complete!"
            print("Network: Connection to %s succeeded. %s" % (host, msg_end))
            return True
        except:
            print("Network: Connection to %s failed" % (host))
            return False

        
    def broadcast_heartbeats(self):
        try:
            for host in self._connected:
                if host in self._verified:
                
                    if self._nodes[host].send_heartbeat():
                        print("Network: Hearbeat sent to %s" % (host))
                    else:
                        print("Network: Heartbeat to %s failed" % (host))
                        self.disconnect_from_host(host)
        except RuntimeError:
            # This is from _connected changing size
            pass

        
    def broadcast_host(self, new_host):
        if new_host not in self._verified:
            print("Network: Shouldn't broadcast an unverified host")
            return

        try:
            print("Network: Broadcasting %s" % (new_host))
            for host in self._connected:
                if host in self._verified and not host == new_host:
                    self._nodes[host].send_host(new_host)
        except RuntimeError:
            # This is from _connected changing size
            pass

    def send_dfs(self, host, files):
        pass

    def send_network_info(self, host):
        pass


    
        
######################################
## Network Internal Interface
#####################################

    def print_all(self):
        print(self._nodes)
        print(self._new)
        print(self._seen)
        print(self._connected)
        print(self._verified)
        print(self._identities)

                 
    def startup(self):
        try:
            for host in self._seen:
                self.connect_to_host(host)
        except RuntimeError:
            # This is from hosts being added to _seen
            pass


    def verify_host(self, host, id):
        verified = id in self._identities

        if verified:
            msg_end = "Awaiting connection..." if not host in self._connected else "Connection and verification complete!"
            print("Network: %s identity verified as %s. %s" % (host, id, msg_end))
            self._verified.add(host)

            # if this is a new host save it
            if (host not in self._seen or host in self._new) and not self.TESTING_MODE:
                self._config.store_host(host)
                self._new.add(host)
        else:
            print("Network: %s identity %s not recognized" % (host, id))

            # if there is a connection get rid of it
            if host in self._nodes:
                self.disconnect_from_host(host)
                
        return verified    

    def record_heartbeat(self, host):
        if not host in self._nodes:
            print("can't recieve heartbeat from nonexistent node")
            return            
        self._nodes[host].record_heartbeat()

        
    def disconnect_from_host(self, host):
        if host in self._connected: self._connected.remove(host)
        if host in self._verified: self._verified.remove(host)
        if host in self._nodes: self._nodes[host].close_connection()

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
        
######################################
## Helper Functions
#####################################

    def _load_from_config(self):
        for host in self._config.hosts():
            # don't add self (for running local test)
            if not self.TESTING_MODE and not host == self._me.host:
                self._seen.add(host)

        self._identities = set(self._config.identities())

                    
