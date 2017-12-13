import json
import sys
import socket
import time
import threading
import urllib.request
import logging
import os

from modules.network.network import Network
from modules.network.message import Message
from modules.network.entity import Entity
import modules.dfs.dfs as dfs # DFS exceptions
from modules.dfs.dfs import DFS # DFS itself
import modules.dfs.dfsmanager as DFSM

from modules.dfs.filewriter import Filewriter # writes files

from modules.logger.log import Log

local_test = False

LISTEN_PORT = 8889

my_host = None
my_port = None
my_id = None

network = None

manager = None

filewriter = None

log = None
logger = None

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
            print("Node %s no longer alive. Disconnecting" % (host))
            network.disconnect_from_host(host)
            conn.close()
            return

        # determine the type of message
        type = bytes.decode(conn.recv(1))
        if type:
            # try to determine the size of the message
            size =  bytes.decode(conn.recv(Message.LENGTH_SIZE))
            if size:
                # recieve the rest of the message (the actual data)
                size = int(size)
                msg = bytes.decode(conn.recv(size))


        verified = verified or network.verified(host)
        well_formatted = type and msg
        
        # handle the actual message
        if not verified:
                # don't handle any messages from unverified hosts except verify
            if type == Message.Tags.IDENTITY:
                time_to_die = not handle_verify_msg(msg, host)
                
            if not time_to_die:
                # kill connection if not verified within 2 seconds
                time_to_die =  time.time() - start_time > 2
        else:
            # TODO get rid of unnecessary nesting
            if not network.connected(host):
                # this is where we will see when the connection should die mostly
                time_to_die = True
            elif well_formatted:
                # got an actual message
                logger.debug("got message %s:%d:%s" % (type,size,msg))

                if type == Message.Tags.HEARTBEAT:
                    logger.debug("Received heartbeat from %s" % (host))
                    network.record_heartbeat(host)
                elif type == Message.Tags.HOST_JOINED:
                    handle_host_msg(msg, host)
                elif type == Message.Tags.USER_INFO:
                    handle_users_msg(msg)
                elif type == Message.Tags.DFS_INFO:
                    handle_dfs_info_message(msg)
                elif type == Message.Tags.STORE_REPLICA:
                    handle_store_replica(msg, host)
                elif type == Message.Tags.REQUEST_FILE:
                    handle_request_file(msg, host)
                elif type == Message.Tags.FILE_SLICE:
                    handle_file_slice(msg)
                elif type == Message.Tags.HAVE_REPLICA:
                    handle_have_replica(msg, host)
                elif type == Message.Tags.POKE:
                    print("%s poked you!" % network.id(host))
                elif type == Message.Tags.UPLOAD_FILE:
                    handle_upload(msg, host)

def handle_request_file(msg, host):
    msg = msg.split(Message.DELIMITER)
    file_name = msg[0]
    part_num = msg[1]
    total_parts = msg[2]
    logger.info("Request for part %s/%s of %s from %s" % (part_num, total_parts, file_name, host))
    
    # read file data from replica
    data = filewriter.read_from_replica(file_name, part_num)
    
    # send to requester
    network.serve_file_request(host, file_name, part_num, total_parts, data)

def handle_store_replica(msg, host):
    msg = msg.split(Message.DELIMITER)
    file_name = msg[0]
    uploader = msg[1]
    part_num = msg[2]
    total_parts = msg[3]
    data = msg[4]
    logger.info("Receiving " + uploader + "'s file " + file_name + " from " + host + "...")

    # add file data to replica file
    manager.store_replica(file_name, uploader, part_num, total_parts, data)
    
    # tell other nodes to update their dfs
    logger.info("Broadcasting successful replica reception to network")
    network.broadcast_replica(file_name, uploader, part_num, total_parts)
    logger.info("Finished alerting other nodes in network")

def handle_have_replica(msg, host):
    msg = msg.split(Message.DELIMITER)
    file_name = msg[0]
    replica_node = network.id(host)
    
    # update my dfs with new replica info
    manager.add_replica(file_name, replica_node)
    
def handle_file_slice(msg):
    msg = msg.split(Message.DELIMITER)
    filename = msg[0]
    part = msg[1]
    total = msg[2]
    data = msg[3]

    logger.info("Receiving %s/%s of file %s" % (part, total, filename))
   
    # write file data to files/filename
    filewriter.write_to_file(filename, part, total, data)

def handle_users_msg(msg):
    ids = msg.split(Message.DELIMITER)
    network.add_users(ids)

def handle_dfs_info_message(dfs_json_str):
    dfs_json = json.loads(dfs_json_str)
    manager.update_with_dfs_json(dfs_json)

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
        network.send_network_info(host)
        network.send_dfs_info(host, manager.get_log())

        # send them network config info (trusted ids)
        network.send_network_info(host)
    return True

def handle_host_msg(new_host, host):
    if not network.connected(new_host):
        logger.info("Notified %s online by %s" % (new_host, host))
        network.connect_to_host(new_host)

def handle_upload(msg, host):
    msglist = msg.split(Message.DELIMITER)
    filename = msglist[0]
    uploader = msglist[1]

    manager.add_to_fs(filename, uploader)

        
#########################################
## Thread for recieving new 1;5B1;5Bconnections
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
            filepath = text[7:]
            manager.upload_file(filepath)
        elif text.startswith("download"):
            try:
                end_filename = text.index(" ", 9)
                filename = text[9:end_filename]
                path = text[end_filename + 1:]
                manager.download_file(filename, path)
            except ValueError:
                print("please specify destination path")
        elif text == "files":
            print_file_list()
        elif text.startswith("delete"):
            manager.delete_file(text[7:])
        elif text == "help":
            print_help()
        elif text == "quit" or text == "q":
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
            user = text[7:]
            network.add_users([user])
        elif text == "refresh":
            print("I don't know how")
        elif text == "clear files":
            manager.clear_files()
        elif text == "debug":
            log.toggle_debug()
        elif text == "info":
            log.toggle_info()
        elif text.startswith("poke"):
            user = text[5:]
            network.send_poke(user)
        elif text == "users":
            network.display_users()
            #print(network.users())

def print_node_list():
    seen_nodes = network.get_seen_nodes()
    for host in seen_nodes:
        host = truncate(host, 22)
        print(host.ljust(25) + ("connected" if network.connected(host) else "not connected"))

def print_file_list():
    manager.display_files()
    
# cuts off the end of the text for better formatting
def truncate(text, length):
    if len(text) > length:
        return text[:(length-3)] + "..."
    return text

def print_help():
    print("Commands:")
    print("nodes - print node list")
    print("files - print file list")
    print("upload [file_path] - add a file to the dfs")
    print("download [file_name] [path] - download file from the dfs")
    print("delete [file_name] - delete a file from the dfs")
    print("join")
    print("connect [host_name]")
    print("myinfo - print ip addr and userid")
    print("verify [user_id]")
    print("refresh")
    print("debug - toggle debugging mode")
    print("info - toggle info mode")
    print("quit")
    
#########################################
## Startup
#########################################
if __name__ == "__main__":

    filewriter = Filewriter()

    local_test = len(sys.argv) > 2

    if local_test:
        print("You are running in testing mode")

    my_host = _get_ip() if not local_test else "127.0.0.1"
    my_port = LISTEN_PORT if not local_test else int(sys.argv[2])

    my_id = sys.argv[1]

    profile = Entity(my_host, my_port, my_id)
    network = Network(profile, local_test)

    manager = DFSM.DFSManager(network, my_id, filewriter, "modules/dfs/dfs.json")

    log = Log()
    logger = log.get_logger()
    log.toggle_debug()
    
    # hello
    logger.info("Starting up")

    listen = socket.socket()

    # tell os to recycle port quickly
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # start up listening socket and thread
    listen.bind((my_host, my_port))
    listen.listen()
    threading.Thread(target=listen_for_nodes, args=(listen,)).start()

    # start up heatbeat thread
    threading.Thread(target=send_heartbeats).start()

    # start up UI thread
    threading.Thread(target=user_interaction).start()

