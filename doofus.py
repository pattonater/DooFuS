import json
import sys
import socket
import time
import threading
from node import Node



PORT = 8889 
_listen = None
_nodes = {}
myip = "137.165.163.84"
_ips = ["137.165.163.84", "137.165.160.208", "137.165.121.193", "137.165.175.204"]



def connect_to_node(ip):
    try:
        conn = socket.create_connection((ip, PORT), 1)

        # change connection for old node, or create new node
        if ip in _nodes:
            _nodes[ip].set_connection(conn)
        else:   
            node = Node(ip, conn)    
            _nodes[ip] = node
        print("Connection to " + str(ip) + " succeeded")
        return True
    except:
        print("Connection to " + str(ip) + " failed")
        return False

            
def connect_to_network():
    # switch to reading from a json file
    #    try:
    #       recovered_nodes = json.load(open('config.json'))
    #  finally:
        # do something
    
    print("Connecting to network...")
    for ip in _ips:
        not_mine = not ip == myip 
        if not_mine:
            connect_to_node(ip)

            
####################################
## Thread for sending heartbeats
####################################
def send_heartbeats():
    while True:
        time.sleep(5)
        for node in _nodes.values():

            if node.is_alive():
                success = node.send_heartbeat()
                
                if success:
                    print("Hearbeat sent to " + str(node._ip))
                else:
                    print("Node " + str(node._ip) + " not found. Disconnecting")
                    node.close_connection()


#####################################
## Thread for recieving messages 
#####################################
def listen_for_messages(conn, ip):
    print("Listening to " + str(ip))
    print(_nodes)
    while True:

        # end thread if know node is offline
        if not _nodes[ip].is_alive():
            print("No longer listening to " + str(ip))
            return
        
        msg = conn.recv(1024)
        
        if msg == b"H":
            print("Recieved heartbeat from " + str(ip))
            _nodes[ip].record_pulse()


#########################################
## Thread for recieving new connections 
#########################################
def listen_for_nodes(listen):
    # start accepting new connections
    print("Listening...")
    while True:
        conn, addr = listen.accept()
        ip = addr[0]

        print("Contacted by node at " + str(ip))
        
        # if is a new node or node coming back online, connect to it
        if ip not in _nodes or not _nodes[ip].is_alive():
            print("Node online")
            connected = connect_to_node(ip)

            if not connected:
                conn.close()
                continue

        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, ip,)).start()
 
            
if __name__ == "__main__":

    # hello
    print("Starting up")

    listen = socket.socket()

    # tell os to recycle port quickly
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # start up listening socket and thread
    listen.bind((myip, PORT))
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

   
