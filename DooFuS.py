import json
import sys
import socket
import time
import threading
import Node




        
PORT = 8877        
_listen = None
_nodes = {}
myip = "137.165.163.84"
_ips = ["137.165.163.84", "137.165.160.208", "137.165.162.149"]
#_ips = ["137.165.162.149"]

def _add_node(ip):
    try:
        conn = socket.socket()
        conn.settimeout(5)
        conn.connect((ip, PORT))
        node = Node.Node(ip, conn)    
        _nodes[ip] = node
        print("Connection to " + str(ip) + " succeeded")
    except:
        print("Connection to " + str(ip) + " failed")
    finally:
        if ip in _nodes:
            _nodes.remove(ip)


            
def _connect_to_network():
    # switch to reading from a json file
    #    try:
    #       recovered_nodes = json.load(open('config.json'))
    #  finally:
        # do something
    
    for ip in _ips:
        # TODO make this check if is your own or does it matter will just fail
        not_mine = True
        if not_mine:
            # TODO select a free port?
            _add_node(ip)
    

def _send_heartbeats():
    while True:
        time.sleep(5)
        for node in _nodes.values():
            node.send_heartbeat()
            print("Hearbeat sent to " + str(node._ip))


def _listen_for_messages(conn, ip):
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
    _connect_to_network()
    heartbeat_thread = threading.Thread(target=_send_heartbeats)
    heartbeat_thread.start()
    
    print("Connected to network")

    listen = socket.socket()
    #host = socket.gethostname()
    host = myip #socket.gethostbyname('localhost')

    print(myip)
    #print(socket.gethostbyname(socket.gethostname()))
    
    listen.bind((host, PORT))
    listen.listen()

    while True:
        print("Listening...")
        conn, addr = listen.accept()
        ip = addr[0]

        print("Contacted by node at " + str(ip))
        _add_node(ip)
        _ips.append(ip)

        thread = threading.Thread(target=_listen_for_messages, args=(conn, addr,))
        thread.start()


    

    
