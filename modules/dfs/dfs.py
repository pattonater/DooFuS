# DFS API
# Flat

# class instance soft state:
#  _log_name: json file name
#  _log: json object read from file at startup, updated by all operations
#  _UPDATE_PERIOD: how many times update needs to be called between disk writes
#  _current_update: number of updates since last disk write
#  _lock: thread safety lock

import json                 # _log, file i/o
from threading import Lock  # _lock

###########################
## DFS Class
###########################
class DFS:

    # Initializes the DFS. Reads from the log file.
    def __init__(self, log_name = None, update_period = None):
        self._UPDATE_PERIOD = update_period if update_period else 1
        self._current_update = 0
        self._log_name = log_name if log_name else "dfs.json"
        self._lock = Lock()

        try:
            with open(self._log_name, 'r') as file:
                self._log = json.load(file)
        except FileNotFoundError:
            # Instantiating new file
            self._log = {"files" : []}
            self.update_disk()
            

    # Takes the current json instance and writes it back to disk.
    # This should be called with some regularity, but not necessarily
    # after every operation. Frequency controlled by self._UPDATE_PERIOD
    def _update(self, toFile=False):
        # Early abort if we don't want to write to disk yet
        if not toFile:
            self._current_update += 1

        if self._current_update < self._UPDATE_PERIOD and not toFile:
            return

        # Time to write to disk
        try:
            with open(self._log_name, 'w+') as file:
                json.dump(self._log, file)
        except IOError as e:
            raise DFSIOError(e)

        # Reset disk write time track
        self._current_update = self._current_update if toFile else 0          


    # Adds file object to _log
    def add_file(self, filename, uploader):
        self._lock.acquire()

        # Verify the file doesn't already exist (name collision)
        for f in self._log["files"]:
            if f["filename"] == filename and f["uploader"] == uploader:
                raise DFSAddFileError(filename, uploader)                
        
        # No name collision. Add file
        self._log["files"].append({
            "filename" : filename,
            "replicas" : [],
            "uploader" : uploader})

        self._update()

        self._lock.release()
        
    # Removes file object from _log
    def delete_file(self, filename):
        self._lock.acquire()

        initial_file_count = len(self._log["files"]) 
        self._log["files"][:] = [f for f in self._log["files"]
                                 if f.get("filename") != filename]
        
        if len(self._log["files"]) == initial_file_count:
            raise DFSRemoveFileError(filename)

        self._update()

        self._lock.release()

    # Returns list of files
    def list_files(self):
        return self._log["files"]

    # Forces a write to disk
    def update_disk(self):
        self._lock.acquire()
        self._update(True)
        self._lock.release()

###########################
## DFS Exceptions
###########################
class DFSError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class DFSInstantiationError(DFSError):
    def __init__(self):
        DFSError.__init__(self, "DFS instatiation error: Failed to instantiate DFS")

class DFSIOError(DFSError):
    def __init__(self, msg):
        DFSError.__init__(self, "DFS i/o error: \n" + e)

class DFSAddFileError(DFSError):
    def __init__(self, filename, uploader):
        DFSError.__init__(self, "DFS add file error: Could not add file\n"
            + "filename: " + filename + "\nuploader: " + uploader)

class DFSRemoveFileError(DFSError):
    def __init__(self, filename):
        DFSError.__init__(self, "DFS remove file error: Could not add file\n"
            + "filename: " + filename) 
