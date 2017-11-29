import json
import sys
import socket
import time
import threading
import Node



PORT = 8889 
_listen = None
_nodes = {}
myip = "137.165.163.84"
_ips = ["137.165.163.84", "137.165.160.208", "137.165.121.193", "137.165.175.204"]

def add_node(ip):
    try:
        conn = socket.socket()
        conn.settimeout(5)
        connected = not conn.connect_ex((ip, PORT))
        if connected:
            node = Node.Node(ip, conn)    
            _nodes[ip] = node
            print("Connection to " + str(ip) + " succeeded")
        else:
            print("Connection to " + str(ip) + " failed")
    except:
        print("Connection to " + str(ip) + " failed")



            
def connect_to_network():
    # switch to reading from a json file
    #    try:
    #       recovered_nodes = json.load(open('config.json'))
    #  finally:
        # do something
    
    print("Connecting to network...")
    for ip in _ips:
        # TODO make this check if is your own or does it matter will just fail
        not_mine = not ip == myip 
        if not_mine:
            # TODO select a free port?
            add_node(ip)

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
                    


def listen_for_messages(conn, ip):
    conn.setblocking(True)
    print("Listening to " + str(ip))
    while True:
        msg = conn.recv(1024)
        
        if msg == b"H":
            print("Recieved heartbeat from " + str(ip))
            _nodes[ip].record_pulse()
            
if __name__ == "__main__":

    # hello
    print("Starting up")

    listen = socket.socket()
    host = myip 

    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen.bind((host, PORT))
    
    listen.listen()

    threading.Thread(target=connect_to_network).start()
    threading.Thread(target=send_heartbeats).start()

    while True:
        print("Listening...")
        conn, addr = listen.accept()
        ip = addr[0]

        print("Contacted by node at " + str(ip))

        if ip not in _nodes:
            add_node(ip)
            print("This is a new node")
        else:
            _nodes[ip].set_connection(conn)

        threading.Thread(target=listen_for_messages, args=(conn, ip,)).start()
