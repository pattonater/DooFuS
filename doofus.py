import json
import sys
import socket
import time
import threading
import urllib.request

from modules.network.network import Network
from modules.network.entity import Entity
import modules.dfs.dfs as dfs # DFS exceptions
from modules.dfs.dfs import DFS # DFS itself


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
            print("Run 'startup' to attempt to join your network")
            #network.startup()
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
    
    start_time = time.time()
    verified = False
    while True:
        msg = bytes.decode(conn.recv(1024)).split("-")
        type = msg[0]

        time_to_die = False

        # don't handle messages from unverified hosts
        verified = verified or network.verified(host)
        if not verified:
            if type == "ID":
                time_to_die = handle_id_msg(msg, host)
            else:
                # should kill connection if not verified within 5 seconds
                time_to_die =  time.time() - start_time > 2        
        else:
            if not network.connected(host):
                time_to_die = True
            elif type == "H":
                print("Recieved heartbeat from %s" % (host))
                network.record_heartbeat(host)
            elif type == "HOST":
                time_to_die = handle_host_msg(msg, host)

        # end thread and connection if node is no longer connected
        if time_to_die:
            print("Node %s no longer alive. Disconnecting" % (host))
            network.disconnect_from_host(host)
            conn.close()
            return
                
    def handle_id_msg(msg, host):
        print("Received id from %s" % (host))
        id = msg[1] if len(msg) > 1 else None
        
        if not id:
            print("Parsing error for ID message")
            return False
        
        if network.verify_host(host, id):
            network.broadcast_host(host)
            
            # this host reached out to you, now connect to it
            if not network.connected(host):
                return network.connect_to_host(host)
            
        return True

    
    def handle_host_msg(msg, host):
        new_host = msg[1] if len(msg) > 1 else None

        if not new_host:
            print("Parsing error for HOST message")
            return False
        
        if not network.connected(new_host):
            print("Notified %s online by %s" % (new_host, host))
            network.connect_to_host(new_host)
            
        return True


#########################################
## Thread for recieving new connections 
#########################################
def listen_for_nodes(listen):
    # start accepting new connections
    print("Listening...")
    while True:
        conn, addr = listen.accept()
        host = addr[0]
        network.print_all()
        print("Contacted by node at " + str(host))
        
        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, host,)).start()


        
#########################################
## Thread for user interaction
#########################################
def user_interaction():
    print("Welcome to DooFuS.")
    while True:
        text = input("-> ")
        if text == "print node list":
            print_node_list()
        elif text == "add file":
            add_file()
        elif text == "print file list":
            print_file_list()
        elif text == "delete file":
            delete_file()
        elif text == "help":
            print_help()
        elif text == "quit":
            disconnect()
        elif text == "start":
            network.startup()

def print_node_list():
    seen_nodes = network.get_seen_nodes()
    for host in seen_nodes:
        print(host + "\t\t" + ("connected" if network.connected(host) else "not connected"))

def print_file_list():
    for file in dfs.list_files():
        replicas = ""
        for replica in file.replicas:
            replicas += replica
        print(file.filename + "\t\t Uploaded by " + uploader +
              ("\t\t replicated on the following machines: " + replicas + "\n"))

def add_file():
    file = input("Which file would you like to upload? \n->")
    dfs.add_file(file)

def delete_file():
    file = input("Which file would you like to delete? \n->")
    dfs.delete_file(file)

def print_help():
    print("Commands:\n print node list\n print file list\n add file\n delete file\n quit")

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

    # start up UI thread
    threading.Thread(target=user_interaction).start()



   
