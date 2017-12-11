## DFS Manager
## Soft state:
##  _fs: FS objet
##  _network: Network object
##  _file_list: initial file list from FS object

from threading import Lock
from .dfs import DFS
from .filewriter import Filewriter

class DFSManager:

    def __init__(self, network, log_name = None):
        self._network = network
        self._fs = DFS(log_name)
        self._file_list = self._fs.list_files()
        self._filewriter = Filewriter()

    def upload_file(self, filename):
        ## choose replicas (all)
        ## call network send file function
        ## add to _fs
        ## EXCEPTIONS
        pass

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
        ## see who has replica
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
