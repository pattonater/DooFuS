import json
import socket
from .entity import Entity
from .node import Node


class Network:
    LISTEN_PORT = 8889
    TESTING_MODE = False
    
    def __init__(self, me, test):
        self._nodes = {}
        self._seen = set()
        self._new = set()
        self._connected = set()
        self._verified = set()
        self._me = me
        self.TESTING_MODE = test

        self._load_from_config()

    
######################################
## NodeManager Interface
#####################################
    def startup(self):
        for host in self._seen:
            if not host == self._me.host:
                self.connect_to_host(host)
                
    def connect_to_host(self, host):
        if host in self._connected:
            print("Already connected to host... this shouldn't happen sooo")
            return False
            
        print("Network: Attempting to connect to %s" % (host))

        try:
            # Connect to host
            # for testing locally: 8825 -> 8826 and 8826 -> 8825
            port = 8825 + (self._me.port % 2) if self.TESTING_MODE else self.LISTEN_PORT
            conn = socket.create_connection((host, port), 1)
            node = Node(host, port, conn)

            # send host your credentials
            node.send_id(self._me.id)

            # add node to all relevant sets
            self._nodes[host] = node

            if host not in self._seen:
                self._new.add(host)

            # node active, but not verified
            self._connected.add(host)
            self._seen.add(host)

            msg_end = "Awaiting verification..." if not host in self._verified else "Connection and verification complete!"
            print("Network: Connection to %s succeeded. %s" % (host, msg_end))

            return True
        except:
            print("Network: Connection to %s failed" % (host))
            return False

    def verify_host(self, host, id):
        # TODO have this test (from a file presumably) whether id is appropiate
        verified = id == "hugo"
        
        if verified:
            msg_end = "Awaiting connection..." if not host in self._connected else "Connection and verification complete!"
            print("Network: %s identity verified as %s. %s" % (host, id, msg_end))
            self._verified.add(host)
            
            if (host not in self._seen or host in self._new) and not self.TESTING_MODE:
                self._write_node_to_disc(host)
        else:
            print("Network: %s identity %s not recognized" % (host, id))

            # if there is a connection get rid of it
            if host in self._nodes:
                self._disconnect_host(host)
                
        return verified    


    def broadcast_heartbeats(self):
        for host in self._connected:
            if host in self._verified:
                
                if self._nodes[host].send_heartbeat():
                    print("Network: Hearbeat sent to %s" % (host))
                else:
                    print("Network: Heartbeat to %s failed" % (host))

    def record_heartbeat(self, host):
        if not host in self._nodes:
            print("can't send heartbeat to nonexistent node")
            return
            
        self._nodes[host].record_heartbeat()
        
    def broadcast_host(self, new_host):
        if new_host not in self._verified:
            print("Network: Shouldn't broadcast an unverified host")
            return
        
        print("Network: Broadcasting %s" % (new_host))
        for host in self._connected:
            if host in self._verified and not host == new_host:
                self._nodes[host].send_host(new_host)
    

    def connected(self, host):
        if not host in self._connected: return False
        
        node = self._nodes[host]
        alive = node.is_alive()

        if not alive:
            self._disconnect_from_host(host)
        
        return alive

    def verified(self, host):
        return host in self._verified

        
######################################
## Helper Functions
#####################################

    def _disconnect_from_host(self, host):
        self._connected.remove(host)
        self._nodes[host].close_connection()
        print("Network: %s offline" % (host))


    def _load_from_config(self):
        file_name = 'data/config_network.json'
        with open(file_name) as file:
            config = json.load(file)
            for node in config["Nodes"]:
                host = node["host"]

                # don't add self (for testing purposes)
                if not host == self._me.host:
                    self._seen.add(host)

                    
    def _write_node_to_disc(self, host):
        file_name = '/data/config_network.json'
        try:
            config = None
            # Reads out config (going to overwrite in a bit)
            with open(file_name, 'r') as file:
                config = json.load(file)

            # Add the new node.
            # TODO does this really need the id, going to re-verify everytime anyway?
            config["Nodes"].append({"host":host})

            # Write back to the file.
            with open(file_name, 'w+') as file:
                json.dump(config, file)

            print("Added %s to config file" % (host))

        except Exception as e:
            print("Failed to write new node to disc. Exception: " + str(e))

