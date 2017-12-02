# DFS API
# Flat

# selfs:
#  _log_name
#  _log

import json

class DFS:

    # Initializes the DFS. Reads from the log file.
    def __init__(self, log_name = None, update_period = None):
        # How often we write to disk using _update(), since this will become
        # fairly expensive for big file systems. When it's set to 1, it will
        # update to disk every time _update() is called.
        self._UPDATE_PERIOD = update_period if update_period else 1

        self._log_name = log_name if log_name else "dfs.json"
        self._current_update = 0

        try:
            with open(self._log_name, 'r') as file:
                self._log = json.load(file)
        except IOError as e:
            raise DFSInstantiationError()


    # Takes the current json instance and writes it back to disk.
    # This should be called with some regularity, but not necessarily
    # after every operation. Perhaps we should keep some additional
    # state to track that?
    def _update(self):
        # Early abort if we don't want to write to disk yet
        self._current_update += 1
        if self._current_update < self._UPDATE_PERIOD:
            return

        # Time to write to disk
        try:
            with open(self._log_name, 'w+') as file:
                json.dump(self._log, file)
        except IOError as e:
            raise DFSIOError(e)

        # Reset disk write time track
        self._current_update = 0            


    # Adds file object to log object
    def add_file(self, filename, uploader):
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

        
    # Removes file object from log
    def delete_file(self, filename):    
        self._log["files"][:] = [f for f in self._log["files"]
                                 if f.get("filename") != filename]
                
        self._update()
        

        
#####################
## DFS Exceptions
#####################
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
