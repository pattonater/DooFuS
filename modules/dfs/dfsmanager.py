## DFS Manager
## Soft state:
##  _fs: FS objet
##  _network: Network object
##  _file_list: initial file list from FS object

from threading import Lock
from .dfs import DFS


class DFSManager:

    def __init__(self, network, log_name = None):
        self._network = network
        self._fs = DFS(log_name)
        self._file_list = self._fs.list_files()

    def upload_file(self, filename):
        ## choose replicas (all)
        ## call network send file function
        ## add to _fs
        ## EXCEPTIONS
        pass

    def store_replica(self, filename, bytes):
        ## add self to replica list on _fs 
        ## write bytes to filename
        ## throw exceptions if fail yadda yadda
        pass

    def dump_replica(self, filename):
        ## remove from disk
        ## remove from _fs
        pass

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