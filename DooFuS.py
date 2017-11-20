import json
import sys
import socket

def start_node():

    try:
        recovered_nodes = json.load(open('nodes.json'))
        
        for node in recovered_nodes["Nodes"]:
            # reach out
            socket = socket()
            host = socket.gethostname()
            port = 8877

            socket.bind(host, port)
            

    finally:
        # do something
        


if __name__ == "__main__":

    # hello
    print("Starting up")
