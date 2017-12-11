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
    def _compute_replica_count(priority, node_count):
        return node_count


    def get_DFS_ref(self):
        return self._fs

    def get_log(self):
        return self._fs.return_log()


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

    def download_file(self, filename, dst):
        ## see who has replica (if you do, skip next steps)
        ## request file from one of replicas
        ## if fails to receive from all replicas, throw exception
        ## write bytes to dst
        pass

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
        DFSError.__init__(self, "DFS i/o error: \n" + e)

class DFSManagerAddFileError(DFSManagerError):
    def __init__(self, filename):
        DFSError.__init__(self, "DFSManager add file error: Could not upload file to replicas\n"
            + "filename: " + filename)

class DFSManagerRemoveFileError(DFSManagerError):
    def __init__(self, filename):
        DFSError.__init__(self, "DFS remove file error: Could not add file\n"
            + "filename: " + filename) 

