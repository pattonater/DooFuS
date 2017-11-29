import json
import sys
import socket
import time
import threading
from node import Node



_nodes = {}

local_test = False

PORT = 8889

my_host = None
my_port = None
my_addr = None

seen_nodes = set()

def write_node_to_disc(host):
    try:
        # THIS DOESN"T WORK BUT IF you do open('', 'w+') json fails and erases file
        with open('config.json') as file:
            print("file")
            config = json.load(file)
            nodes = config["Nodes"]
            nodes.append({"host":host, "port":PORT})
            print("append")
            config.dump(nodes, file)
            print("Wrote node %s to disc" % (host))
    except:
        print("Failed to write new node to disc")

def connect_to_node(host):
    try:
        # for testing locally: 8825 -> 8826 and 8826 -> 8825
        port = 8825 + (my_port % 2) if local_test else PORT
        conn = socket.create_connection((host, port), 1)

        # change connection for old node, or create new node
        if host in _nodes:
            _nodes[host].set_connection(conn)
        else:   
            node = Node(host, port, conn)    
            _nodes[host] = node
            #
        print("Connection to %s (%d) succeeded" % (host, port))
        return True
    except:
        print("Connection to %s (%d) failed" % (host, port))
        return False

            
def connect_to_network():
    print("Connecting to network...")
    
    # switch to reading from a json file
    try:
        if local_test:
            host = my_host
            connect_to_node(host)
        else:
            with open('config.json') as file:
                config = json.load(file)
                for node in config["Nodes"]:
                    host = node["host"]
                    port = PORT #int(node["port"])
                    addr = (host,port)

                    seen_nodes.add(host)

                    not_mine = not addr == my_addr 
                    if not_mine:
                        port = node["port"]
                        connect_to_node(host)
    finally:
        # do something
        print("Tried all previously seen nodes")
    
    
            
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
                    print("Hearbeat sent to %s (%d)" % (node._host, node._port))
                else:
                    print("Node %s (%d) not found. Disconnecting" % (node._host, node._port))
                    node.close_connection()


#####################################
## Thread for recieving messages 
#####################################
def listen_for_messages(conn, addr):
    host = addr[0]
    port = addr[1]
    print("Listening to " + str(host))
    #print(_nodes)
    while True:

        # end thread if know node is offline
        if not _nodes[host].is_alive():
            print("No longer listening to %s (%d)" % (host, port))
            return
        
        msg = conn.recv(1024)
        
        if msg == b"H":
            print("Recieved heartbeat from %s (%d)" % (host, port))
            _nodes[host].record_pulse()


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

        if not local_test and not host in seen_nodes:
            write_node_to_disc(host)
            seen_nodes.add(host)

        # if is a new node or node coming back online, connect to it
        if host not in _nodes or not _nodes[host].is_alive():
            print("Node online")
            connected = connect_to_node(host)

            if not connected:
                conn.close()
                continue

        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, addr,)).start()
 
            
if __name__ == "__main__":

    my_host = sys.argv[1]
    local_test = len(sys.argv) > 2

    my_port = PORT if not local_test else int(sys.argv[2])
    my_addr = (my_host, my_port)

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

   
