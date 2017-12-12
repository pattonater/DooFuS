## DFS Manager
## Soft state:
##  _fs: FS objet
##  _network: Network object
##  _file_list: initial file list from FS object

from threading import Lock
import modules.dfs.dfs as dfs
from modules.dfs.filewriter import Filewriter

class DFSManager:

    def __init__(self, network, my_id, filewriter, log_name = None):
        self._network   = network
        self._id        = my_id
        self._fs        = dfs.DFS(log_name)
        self._file_list = self._fs.list_files()
        self._filewriter = filewriter

    # Based on our failure model, calculates number of replicas needed
    # given the priority and number of nodes
    def _compute_replica_count(self, priority, node_count):
        return node_count

    def get_DFS_ref(self):
        return self._fs

    def get_log(self):
        return self._fs.return_log()

    def update_with_dfs_json(self, dfs):
        files = dfs["files"]
        for file in files:
            name = file["filename"]
            uploader = file["uploader"]
            replicas = file["replicas"]
            if not self._fs.check_file(name, uploader):
                self._fs.add_file(name, uploader, replicas)
            else:
                self._fs.add_replicas(name, replicas)
            
    def acknowledge_replica(self, filename, uploader, replica_host):
        if self._fs.check_file(filename, uploader):
            self._fs.add_replicas(filename, replica_host)
        else:
            self._fs.add_file(filename, uploader, [replica_host])

    def upload_file(self, filename, priority = 0.5):
        if self._fs.check_file(filename, self._id):
            print("This file is already on the dfs")
            return False
            #raise dfs.DFSAddFileError(filename, self._id)

        # send dfs with updated file list to everyone
        print("hello?")
        for host in self._network.get_connected_nodes():
            print("about to tell host %s the new dfs" % (host))
            self._network.add_file(host, filename, self._id) # Send metadata telling hosts about new file   

        ## choose replicas (all)
        total_nodes = len(self._network._connected)

        if not total_nodes:
            print("No nodes on network")
            return False
        #raise DFSManagerAddFileError(filename)

        num_replicas = self._compute_replica_count(priority, total_nodes)

        ## call network send file function
        i = 0
        ## currently just adds to host in order
        for host in self._network._connected:
            if i == num_replicas:
                break
            print("Called send replica on network: filename=%s, id=%s" % (filename, self._id))
            self._network.send_replica(host, filename, self._id, 1, 1)

            i += 1
        

    def store_replica(self, filename, uploader, part, total, data):
        ## add replica to dfs
        self.acknowledge_replica(filename, uploader, self._id)
        ## write data to filename
        self._filewriter.write(filename, part, total, data)

    def dump_replica(self, filename):
        ## remove from disk
        self._filewriter.remove(filename)
        ## remove from _fs
        self._fs.remove_file(filename)

    ## Throws DFSManagerDownloadError exception. Please catch it.
    def download_file(self, filename, dst = ""):
        ## Check if you are a replica
        file = self._fs.get_file(filename)
        if not file:
            print("Invalid name")
            return

        file_replicas = file["replicas"]

        if self._id in file_replicas:
            try:
                from shutil import copy2
                copy2("replicas/" + filename, "files/" + filename)
                return
            except IOError:
                print("Cannot retrieve")
                ## Something bad happened. Let's try to get it from somebody else.
                pass

        ## Find active replicas
        active_hosts  = self._network._connected
        active_replicas = list(filter(lambda host: host in file_replicas, active_hosts))

        if len(active_replicas) == 0:
            print("No active replicas of file")
            return
            #raise DFSManagerDownloadError(filename, "No active replicas of file")

        self._network.request_file(active_replicas[0], filename, "1", "1")


    def delete_file(self, filename):
        ## remove from disk (if present)
        ## remove from _fs
        ## tell network to tell replicas
        pass

    def set_priority(self, filename, priority):
        ## punt
        pass

    def node_offline(self, node):
        ## punt
        pass

    def node_online(self, node):
        ## punt
        pass
    
    def display_files(self):
        online = []
        offline = []
        for file in self._fs.list_files():
            if self._file_online(file):
                online.append(file)
            else:
                offline.append(file)
                
        print("*Online*")
        for file in online:
            self._display_file(file)
            
        print("")
        print("*Offline*")
        for file in offline:
            self._display_file(file)

    def _display_file(self, file):                
        filename = truncate(file.get("filename"), 22).ljust(25)
        uploader = truncate(file.get("uploader"), 22).ljust(25)
        replicas = (', '.join(str(replica) for replica in file.get("replicas")))

        print("%s Uploaded by %s Replicated on %s" % (filename, uploader, replicas))


    def _file_online(self, file):
        replicas = file.get("replicas")

        for r in replicas:
            if self._network.user_connected(r):
                return True
            
        return False



##########################
## Utilities
#########################

# cuts off the end of the text for better formatting
def truncate(text, length):
    if len(text) > length:
        return text[:(length-3)] + "..."
    return text

        

###########################
## DFSManager Exceptions
###########################
class DFSManagerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class DFSManagerIOError(DFSManagerError):
    def __init__(self, msg):
        DFSManagerError.__init__(self, "DFSManager i/o error: \n" + msg)

class DFSManagerDownloadError(DFSManagerError):
    def __init__(self, filename, additional = ""):
        DFSManagerError.__init__(self, "DFSManager download file error: " + additional + "\nfilename: " + filename)

class DFSManagerAddFileError(DFSManagerError):
    def __init__(self, filename):
        DFSManagerError.__init__(self, "DFSManager add file error: Could not upload file to replicas\n"
            + "filename: " + filename)

class DFSManagerRemoveFileError(DFSManagerError):
    def __init__(self, filename):
        DFSManagerError.__init__(self, "DFS remove file error: Could not add file\n"
            + "filename: " + filename) 

