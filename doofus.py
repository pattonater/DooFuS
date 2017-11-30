import json
import sys
import socket
import time
import threading
import urllib.request

from node import Node
from nodemanager import NodeManager
from entity import Entity



local_test = False

LISTEN_PORT = 8889
ID = "r5"


my_host = None
my_port = None

node_manager = None

def _get_ip():
    #Found from: https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python/22157882#22157882
    return urllib.request.urlopen('http://ident.me').read().decode('utf8')

def write_node_to_disc(host):
    try:
        config = None
        # Reads out config (going to overwrite in a bit)
        with open('config.json', 'r') as file:
            config = json.load(file)

        # Add the new node.
        config["Nodes"].append({"host":host, "port":LISTEN_PORT,"id":"dweeb"})

        # Write back to the file.
        with open('config.json', 'w+') as file:
            json.dump(config, file)

        print("Added %s:%d to config file" % (host, LISTEN_PORT))

    except Exception as e:
        print("Failed to write new node to disc. Exception:\n" + e)

def connect_to_node(host):
    node = None
    try:
        # for testing locally: 8825 -> 8826 and 8826 -> 8825
        port = 8825 + (my_port % 2) if local_test else LISTEN_PORT
        conn = socket.create_connection((host, port), 1)

        # create new node
        node = Node(host, port, conn)
        
        print("Connection to %s succeeded" % (host))
    except:
        print("Connection to %s failed" % (host))

    return node

            
def connect_to_network():
    print("Connecting to network...")
    
    # switch to reading from a json file
    try:
        if local_test:
            connect_to_node(my_host)
        else:
            for host in node_manager.inactive_hosts():
                    node = connect_to_node(host)
                    if node:
                        node_manager.add(node)
    finally:
        print("Tried all previously seen nodes")
    
    
            
####################################
## Outgoing Network Communication 
####################################
def send_heartbeats():
    while True:
        time.sleep(5)
        for node in node_manager:
            if node.is_alive():
                if node.send_heartbeat():
                    print("Hearbeat sent to %s (%d)" % (node._host, node._port))
                else:
                    node_manager.remove(node)
                    print("Node %s (%d) not found. Disconnecting" % (node._host, node._port))


def notify_network_new_node(host):
    for node in node_manager:
        # TODO tell them about the new node 
        print("hello")


#####################################
## Incoming Network Communication
#####################################
def listen_for_messages(conn, host):
    node = node_manager[host]
    
    print("Listening to " + str(host))

    while True:
        # end thread if know node is offline
        if not node.is_alive():
            print("No longer listening to %s" % (host))
            return
        
        msg = conn.recv(1024)
        if msg == b"H":
            print("Recieved heartbeat from %s" % (host))
            node.record_heartbeat()


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
        if host not in node_manager:
            print("Node online")
            node = connect_to_node(host)

            if node:
                node_manager.add(node)
            else:
                conn.close()
                continue
               
        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, host,)).start()

#########################################
## Startup 
#########################################
if __name__ == "__main__":
    local_test = len(sys.argv) > 1

    my_host = _get_ip() #if not local_test else "127.0.0.1"    
    my_port = LISTEN_PORT if not local_test else int(sys.argv[1])
    my_id = ID
    
    profile = Entity(my_host, my_port, my_id)
    node_manager = NodeManager(profile)
    node_manager.load_from_config()
    
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

   
