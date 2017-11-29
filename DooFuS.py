import json
import sys
import socket
import time
import threading
import Node



PORT = 8875 
_listen = None
_nodes = {}
myip = "137.165.163.84"
#_ips = ["137.165.163.84", "137.165.160.208", "137.165.162.149", "137.165.175.204"]
_ips = ["137.165.160.208", "137.165.162.149", "vaca.cs.williams.edu", "137.165.175.204"]

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
        not_mine = True
        if not_mine:
            # TODO select a free port?
            add_node(ip)
    print("Connected to network")

def send_heartbeats():
    while True:
        time.sleep(5)
        for node in _nodes.values():
            node.send_heartbeat()
            print("Hearbeat sent to " + str(node._ip))


def listen_for_messages(conn, ip):
    print("Listening to " + str(ip))
    while True:
        msg = conn.recv(1024)
        print("Message: " + str(msg) + " from " + str(ip))

        if msg == b"H":
            print("Recieved heartbeat from " + str(ip))
            _nodes[ip].update_pulse()
            
if __name__ == "__main__":

    # hello
    print("Starting up")

    listen = socket.socket()
    #host = socket.gethostname()
    host = myip #socket.gethostbyname('localhost')

    #print(myip)
    #print(socket.gethostbyname(socket.gethostname()))
    
    listen.bind((host, PORT))
    listen.listen()

    threading.Thread(target=connect_to_network).start()
    heartbeat_thread = threading.Thread(target=send_heartbeats)
    heartbeat_thread.start()

    while True:
        print("Listening...")
        conn, addr = listen.accept()
        ip = addr[0]

        print("Contacted by node at " + str(ip))
        add_node(ip)

        threading.Thread(target=listen_for_messages, args=(conn, addr,)).start()


    

    
