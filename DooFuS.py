import json
import sys
import socket
import time
import threading


#    try:
 #       recovered_nodes = json.load(open('config.json'))
  #  finally:
        # do something

        
PORT = 8877        
_listen = None
_nodes = {}
_ipsDAsdA = ["137.165.163.84", "137.165.160.208"]
_ips = ["137.165.160.208"]

def _add_node(ip):
    try:
        conn = socket.socket()
        conn.settimeout(5)
        conn.connect((ip, PORT))
        node = Node(ip, conn)    
        _nodes[ip] = node
    except:
        print("ARGHSDF")


            
def _connect_to_network():
    for ip in _ips:
        # TODO make this check if is your own 
        not_mine = True
        if not_mine:
            # TODO select a free port?
            _add_node(ip)
    

def _send_heartbeats():
    while True:
        sleep(5)
        for node in _nodes:
            node.send_heartbeat()
            print("Hearbeat sent to " + str(node._ip))
    
            
            
if __name__ == "__main__":

    # hello
    print("Starting up")
    _connect_to_network()
    _heartbeat_thread = threading.Thread(target=_send_heartbeats)

    print("Connected to network")

    listen = socket.socket()
    #host = socket.gethostname()
    host = socket.gethostbyname('localhost')
    print(host)
    
    listen.bind((host, PORT))
    listen.listen()
    print("Listening...")

    while True:
        conn, addr = listen.accept()
        ip = addr[0]
        if ip in nodes:
            _nodes[ip].update_pulse()
            print("Recieved heartbeat from " + str(ip))
        else:
            _add_node(ip)
            _ips.append(ip)
            print("Contacted by new node at " + str(ip))

    

    
