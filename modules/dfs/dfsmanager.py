## DFS Manager
## Soft state:
##  _fs: FS objet
##  _network: Network object
##  _file_list: initial file list from FS object

from threading import Lock
import modules.dfs.dfs as dfs
from modules.dfs.filewriter import Filewriter

class DFSManager:

    def __init__(self, network, my_id, log_name = None):
        self._network   = network
        self._id        = my_id
        self._fs        = dfs.DFS(log_name)
        self._file_list = self._fs.list_files()
        self._filewriter = Filewriter()

    # Based on our failure model, calculates number of replicas needed
    # given the priority and number of nodes
    def _compute_replica_count(priority, node_count):
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
            if not self._fs.check_file(name, uploader):
                self._fs.add_file(name, uploader)
            
    def acknowledge_replica(self, filename, uploader, replica_host):
        if self._fs.check_file(filename, uploader):
            self._fs.add_replica(filename, uploader, replica_host)
        else:
            self._fs.add_file(filename, uploader, [replica_host])


    def upload_file(self, filename, priority = 0.5):
        if self._fs.check_file(filename, self._id):
            raise dfs.DFSAddFileError(filename, self._id)

        ## choose replicas (all)
        total_nodes = len(self._network._connected)

        if not total_nodes:
            print("No nodes on network")
            raise DFSManagerAddFileError(filename)

        num_replicas = _compute_replica_count(priority, total_nodes)

        ## call network send file function
        i = 0
        ## currently just adds to host in order
        for host in self._network._connected:
            if i == num_replicas:
                break

            self._network.send_replica(host, filename, self._id, 1, 1)

            i += 1
        

    def store_replica(self, filename, uploader, part, total, data):
        ## add replica to dfs
        acknowledge_replica(filename, uploader)
        ## write data to filename
        self._filewriter.write(filename, part, total, data)

    def dump_replica(self, filename):
        ## remove from disk
        self._filewriter.remove(filename)
        ## remove from _fs
        self._fs.remove_file(filename)

    ## Throws DFSManagerDownloadError exception. Please catch it.
    def download_file(self, filename, dst):
        ## Check if you are a replica
        file_replicas = self._fs.list_files()
        if self._id in file_replicas:
            try:
                from shutil import copy2
                copy2("replicas/" + filename, "files/" + filename)
                return
            except IOError:
                ## Something bad happened. Let's try to get it from somebody else.
                pass

        ## Find active replicas
        active_hosts  = self._network._connected
        active_replicas = list(filter(lambda host: host in file_replicas, active_hosts))

        if len(active_replicas) == 0:
            raise DFSManagerDownloadError(filename, "No active replicas of file")

        self._network.request_file(active_replicas[0], filename, 1, 1)


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

###########################
## DFSManager Exceptions
###########################
class DFSManagerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class DFSManagerIOError(DFSManagerError):
    def __init__(self, msg):
        DFSError.__init__(self, "DFSManager i/o error: \n" + msg)

class DFSManagerDownloadError(DFSManagerError):
    def __init__(self, filename, additional = ""):
        DFSError.__init__(self, "DFSManager download file error: " + additional + "\nfilename: " + filename)

class DFSManagerAddFileError(DFSManagerError):
    def __init__(self, filename):
        DFSError.__init__(self, "DFSManager add file error: Could not upload file to replicas\n"
            + "filename: " + filename)

class DFSManagerRemoveFileError(DFSManagerError):
    def __init__(self, filename):
        DFSError.__init__(self, "DFS remove file error: Could not add file\n"
            + "filename: " + filename) 

