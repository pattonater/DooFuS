import time
from threading import Lock # _lock
from .message import Message

# This class will represent other nodes in the system
# Soft state:
#   _host: ip address of connection
#   _port: port of connection
#   _conn: socket object for connection
#   _last_heartbeat: timestamp of last-received heartbeat from node
#   _lock: Thread safety for message transmission
class Node:

    # Current heartrate is 0.2/sec, so this gives us time to miss
    # at most 1 heartbeat before we consider it dead.
    TIMEOUT = 12

    def __init__(self, host, port, socket):
        self._host = host
        self._port = port
        self._conn = socket

        self._id = None
        self._last_heartbeat = time.time()

        self._lock = Lock()

    def host(self):
        return self._host

    # Not currently useful
    def record_heartbeat(self):
        self._last_heartbeat = time.time()

    # Confirms that node is alive
    def is_alive(self):
        return self._conn and (time.time() - self._last_heartbeat < self.TIMEOUT)

    # Closes socket.
    def close_connection(self):
        self._lock.acquire()
        try:
            if self._conn:
                self._conn.close()
                self._conn = None
        except Exception as e:
            # if the logger is ever passed in, put this info in there
            pass
        finally:
            self._lock.release()

    def send_poke(self):
        return self._send_message(Message.Tags.POKE, "poke")
    
    # Sends single byte message as heartbeat to host. Primarily used to test
    # the connection; if it doesn't go through, we assume the host is down.
    def send_heartbeat(self):
        return self._send_message(Message.Tags.HEARTBEAT, "hi")

    def send_dfs_info(self, dfs_json_str):
        return self._send_message(Message.Tags.DFS_INFO, dfs_json_str)

    # Identifies self to host
    def send_verification(self, id):
        return self._send_message(Message.Tags.IDENTITY, id)

    # Sends new node information to host
    def send_host_joined(self, host):
        return self._send_message(Message.Tags.HOST_JOINED, host)

    def send_verified_ids(self, ids):
        return self._send_message(Message.Tags.USER_INFO, ids)

    def add_file(self, file_name, my_id):
        return self._send_message(Message.Tags.UPLOAD_FILE, [file_name, my_id])

    def replica_alert(self, file_name, uploader, part_num, total_parts):
        return self._send_message(Message.Tags.HAVE_REPLICA, [file_name, uploader, part_num, total_parts])

    def request_file(self, file_name, part_num, total_parts):
        return self._send_message(Message.Tags.REQUEST_FILE, [file_name, part_num, total_parts])

    def serve_file_request(self, file_name, part_num, total_parts, file):
        return self._send_message(Message.Tags.FILE_SLICE, [file_name, part_num, total_parts, file])

    
    # Since network.py will theoretically be sending heartbeats and other messages on different
    # threads (but on the same port), it's important to lock around the
    def _send_message(self, tag, data):
        self._lock.acquire()
        try:
            msg = Message.data_to_str(tag, data)
            self._conn.send(str.encode(msg))
        except Exception as err:
            print(err)
            self._lock.release()
            return False

        self._lock.release()
        return True


    def send_replica(self, file_name, id, part_num, total_parts):
        # read file in binary mode
        file = open("files/" + file_name, "r")
        
        replica = file.read()
        
        print("Sending " + file_name +  " to " + self._host + "...")
        self._send_message(Message.Tags.STORE_REPLICA, [file_name, id, "1", "1", replica])

#        while True:
            #TODO change chunk size and make constantx
 #           chunk = file.read(8)
            #print ("Sending chunk: " + bytes.decode(chunk))
  #          if not chunk:
   #             break  # EOF
            
    #        self._send_message(Message.Tags.CHUNK, [file_name, bytes.decode(chunk)])

     #   self._send_message(Message.Tags.EOF, [file_name])

        print("Finished sending %s to %s" % (file_name, self._host))
        file.close()

