import json
import sys
import socket
import time
import threading
import urllib.request

from network import Network
from entity import Entity
import dfs # DFS exceptions
from dfs import DFS # DFS itself



local_test = False

LISTEN_PORT = 8889
ID = "r5"

my_host = None
my_port = None

network = None

def _get_ip():
    #Found from: https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python/22157882#22157882
    return urllib.request.urlopen('http://ident.me').read().decode('utf8')
            
def connect_to_network():
    print("Connecting to network...")
    
    # switch to reading from a json file
    try:
        if local_test:
            network.connect_to_host(my_host)
        else:
            network.startup()
    finally:
        print("Tried all previously seen nodes")
    
    
            
####################################
## Outgoing Network Communication 
####################################
def send_heartbeats():
    while True:
        time.sleep(5)
        network.broadcast_heartbeats()


#####################################
## Incoming Network Communication
#####################################
def listen_for_messages(conn, host):    
    print("Listening to " + str(host))

    while True:
        # end thread if node is now offline
        if not network.connected(host):
            print("Node %s no longer alive. Disconnecting" % (node.host()))
            return

        msg = bytes.decode(conn.recv(1024)).split("-")
        type = msg[0]

        if type == "ID":
            print("Received id from %s" % (host))
            id = msg[1] if len(msg) > 1 else "notanid"
            verified = network.verify_identity(host, id)
            if verified:
                network.broadcast_host(host)
        elif network.verified(host):
            if type == "H":
                print("Recieved heartbeat from %s" % (host))
                network.record_heartbeat(host)
            elif type == "HOST":
                new_host = msg[1] if len(msg) > 2 else "notahost"
                if not network.connected(new_host):
                    print("Notified %s online by %s" % (new_host, host))
                    network.connect_to_host(new_host)
            


#########################################
## Thread for recieving new connections 
#########################################
def listen_for_nodes(listen):
    # start accepting new connections
    print("Listening...")
    while True:
        conn, addr = listen.accept()
        host = addr[0]

        print("Contacted by node at " + str(host))

        # if is a new node or node coming back online, connect to it
        if not network.connected(host):
            print("who?")
            connected = network.connect_to_host(host)
            if not connected:
                # don't start up a thread to listen to this node and kill the connection
                conn.close()
                continue
        
        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, host,)).start()

#########################################
## Startup 
#########################################
if __name__ == "__main__":
    local_test = len(sys.argv) > 2

    if local_test:
        print("You are running in testing mode")

    my_host = _get_ip() if not local_test else "127.0.0.1"    
    my_port = LISTEN_PORT if not local_test else int(sys.argv[2])
    my_id = sys.argv[1]
    
    profile = Entity(my_host, my_port, my_id)
    network = Network(profile, local_test)
    
    # hello
    print("Starting up")

    listen = socket.socket()

    # tell os to recycle port quickly
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # start up listening socket and thread
    listen.bind((my_host, my_port))
    listen.listen()
    threading.Thread(target=listen_for_nodes, args=(listen,)).start()


    
    # attempt to connect to previously seen nodes
    # should this be on a separate thread?
    # pros: user can interact with program right away
    # cons: possible race conditions?
    threading.Thread(target=connect_to_network).start()

    # start up heatbeat thread
    threading.Thread(target=send_heartbeats).start()


    # TODO handle user interaction

   
