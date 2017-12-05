import json
import sys
import socket
import time
import threading
import urllib.request
import logging
import os

from modules.network.network import Network
from modules.network.messagetags import MessageTags
from modules.network.entity import Entity
import modules.dfs.dfs as dfs # DFS exceptions
from modules.dfs.dfs import DFS # DFS itself

from modules.filewriter.filewriter import Filewriter # writes files

local_test = False

LISTEN_PORT = 8889

my_host = None
my_port = None
my_id = None

network = None

dfs = None

filewriter = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')

h = logging.FileHandler('logs/debug.log')
h.setLevel(logging.NOTSET)
h.setFormatter(formatter)

h2 = logging.FileHandler('logs/info.log')
h2.setLevel(logging.INFO)
h2.setFormatter(formatter)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(h)
logger.addHandler(h2)
logger.addHandler(ch)

def _get_ip():
    #Found from: https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python/
    return urllib.request.urlopen('http://ident.me').read().decode('utf8')

def connect_to_network():
    logger.info("Connecting to network...")

    # switch to reading from a json file
    try:
        if local_test:
            network.connect_to_host(my_host)
        else:
            network.startup()
    finally:
        logger.info("Tried all previously seen nodes")

def exit():
    print("Exiting DooFuS.")
    os._exit(0)

####################################
## Outgoing Network Threads
####################################
def send_heartbeats():
    while True:
        time.sleep(5)
        network.broadcast_heartbeats()

#####################################
## Incoming Network Communication
#####################################
def listen_for_messages(conn, host):
    logger.info("Listening to " + str(host))

    start_time = time.time()
    verified = False
    time_to_die = False
    while True:
        # end thread and connection if one of messages failed is no longer connected (and once was)
        if time_to_die:
            print("Disconnect from %s" % (host))
            logger.info("Node %s no longer alive. Disconnecting" % (host))
            network.disconnect_from_host(host)
            conn.close()
            return

        # determine the type of message
        type = bytes.decode(conn.recv(1))

        if type:
            # determine the size of the message
            size = ""
            max_digits = 10
            num_digits = 0
            while True:
                digit = bytes.decode(conn.recv(1))
                if digit == MessageTags.DELIM:
                    break
                size += digit

                # don't let size be more than 10 digits
                num_digits += 1
                if num_digits >= max_digits:
                    size = ""
                    break

            if size:
                # recieve the rest of the message
                size = int(size)
                msg = bytes.decode(conn.recv(size))

        # handle the message
        verified = verified or network.verified(host)
        well_formatted = type and msg # and MessageTags.valid_tag(type)

        if not verified:
                # don't handle any messages from unverified hosts except verify
                if type == MessageTags.VERIFY:
                    time_to_die = not handle_verify_msg(msg, host)

                if not time_to_die:
                    # kill connection if not verified within 2 seconds
                    time_to_die =  time.time() - start_time > 2
        else:
            if not network.connected(host):
                time_to_die = True
            elif well_formatted:
                # got an actual message
                print("got message %s%d~%s" % (type,size,msg))

                if type == MessageTags.HEARTBEAT:
                    logger.debug("Received heartbeat from %s" % (host))
                    network.record_heartbeat(host)
                elif type == MessageTags.HOST:
                    handle_host_msg(msg, host)
                elif type == MessageTags.AUTHORIZED:
                    handle_authorized_msg(msg)
                elif type == MessageTags.FILE:
                    handle_file(msg, host)
                elif type == MessageTags.CHUNK:
                    handle_chunk(msg)
                elif type == MessageTags.EOF:
                    handle_EOF(msg)

def handle_file(filename, host):
    print("Receiving file " + filename + " from " + host)
    # prepend to filename if testing locally
    filewriter.add_file(filename)

def handle_chunk(msg):
    msglist = msg.split(MessageTags.DELIM)
    filename = msglist[0]
    chunk = msglist[1]
    filewriter.add_chunk(filename, chunk)

def handle_EOF(filename):
    print("End of file " + filename)
    filewriter.write(filename)

def handle_authorized_msg(msg):
    ids = msg.split(MessageTags.DELIM)
    # TODO send them to network to store

def handle_verify_msg(id, host):
    logger.info("Received id from %s" % (host))

    if network.verify_host(host, id):
        network.broadcast_host(host)

        # this host reached out to you, now connect to it
        if not network.connected(host):
            if not network.connect_to_host(host):
                return False

        # do other handshake stuff
        # send them your dfs info
        files = dfs.list_files
        network.send_dfs(files, host)

        # send them network config info (trusted ids)
        network.send_network_info(host)
    return True

def handle_host_msg(new_host, host):
    if not network.connected(new_host):
        logger.info("Notified %s online by %s" % (new_host, host))
        network.connect_to_host(new_host)

#########################################
## Thread for recieving new connections
#########################################
def listen_for_nodes(listen):
    # start accepting new connections
    logger.info("Listening...")
    while True:
        conn, addr = listen.accept()
        host = addr[0]
        logger.info("Contacted by node at " + str(host))

        # start up a thread listening for messages from this connection
        threading.Thread(target=listen_for_messages, args=(conn, host,)).start()

#########################################
## Thread for user interaction
#########################################
def user_interaction():
    print("Welcome to DooFuS.")
    while True:
        text = input("-> ")
        if text == "nodes":
            print_node_list()
        elif text.startswith("upload"):
            add_file(text[7:])
        elif text == "files":
            print_file_list()
        elif text[:6] == "delete":
            dfs.delete_file(text[7:])
        elif text == "help":
            print_help()
        elif text == "quit":
            exit()
        elif text == "join":
            connect_to_network()
        elif text.startswith("connect"):
            network.connect_to_host(text[8:])
        elif text == "netinfo":
            network.print_all()
        elif text == "myinfo":
            print("%s as %s" % (my_host, my_id))
        elif text.startswith("verify"):
            print("I don't know how")
        elif text == "refresh":
            print("I don't know how")
        elif text == "debug":
            toggle_debug()
            network.toggle_debug()
        elif text == "info":
            toggle_info()
            network.toggle_info()

def add_file(filename):

    for file in dfs.list_files():
        if file.get("filename") == filename:
            print("File already exists. Delete the current version or choose a new name.")
            return
    
    # send to everyone
    for host in network.get_connected_nodes():
        network.send_file(host, filename)

    # add to dfs TODO add replicas
    dfs.add_file(filename, my_id)


def print_node_list():
    seen_nodes = network.get_seen_nodes()
    for host in seen_nodes:
        host = truncate(host, 22)
        print(host.ljust(25) + ("connected" if network.connected(host) else "not connected"))

def print_file_list():
    for file in dfs.list_files():
        filename = truncate(file.get("filename"), 22)
        uploader = truncate(file.get("uploader"), 22)
        print(filename.ljust(25) + "Uploaded by " + uploader.ljust(25) + "Replicated on " + (', '.join(str(replica) for replica in file.get("replicas"))))

# cuts off the end of the text for better formatting
def truncate(text, length):
    if len(text) > length:
        return text[:(length-3)] + "..."
    return text

def print_help():
    print("Commands:\n nodes - print node list\n files - print file list\n upload [file_name] - add a file to the dfs\n delete [file_name] - delete a file from the dfs\n join\n connect [host_name]\n myinfo - print ip addr and userid\n verify [user_id]\n refresh\n debug - toggle debugging mode\n info - toggle info mode\n quit")

def toggle_debug():
    if logger.handlers[2].level != logging.DEBUG:
        ch.setLevel(logging.DEBUG)
        logger.info("Starting debugging")
    else:
        logger.info("Stopping debugging")
        ch.setLevel(logging.WARNING)


def toggle_info():
    if logger.handlers[2].level != logging.INFO:
        ch.setLevel(logging.INFO)
        logger.info("Starting to print INFO")
    else:
        logger.info("Stopping printing of INFO")
        ch.setLevel(logging.WARNING)
    
#########################################
## Startup
#########################################
if __name__ == "__main__":

    dfs = DFS("test_dfs.json")

    filewriter = Filewriter()

    local_test = len(sys.argv) > 2

    if local_test:
        print("You are running in testing mode")

    my_host = _get_ip() if not local_test else "127.0.0.1"
    my_port = LISTEN_PORT if not local_test else int(sys.argv[2])

    my_id = sys.argv[1]

    profile = Entity(my_host, my_port, my_id)
    network = Network(profile, local_test)

    # hello
    logger.info("Starting up")

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
