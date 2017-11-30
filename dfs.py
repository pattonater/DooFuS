# DFS API
# Flat

# selfs:
#  _log_name
#  _log
#  

import json

class DFS:

    # Initializes the DFS. Reads from the log file.
    def __init__(self, log_name = None):
        self._log_name = log_name if log_name else "dfs.json"

        try:
            with open(self._log_name, 'r') as file:
                self._log = json.load(file)
        except IOError as e:
            print("Failed to read log. Error:\n" + e)

    def _update():
        try:
            with open(self._log_name, 'w+') as file:
                json.dump(self._log, self._log_name)
        except IOError as e:
            print("Failed to update log. Error:\n" + e)

    # Adds file object to log
    def add_file(filename, uploader):
        for f in self._log["files"]:
            if f["filename"] == filename and f["uploader"] == uploader:
                print("File already exists in DFS.")
                return
        
        self._log["files"].append({
            "filename" : filename,
            "replicas" : [],
            "uploader" : uploader})

        self._update()
        
    # Removes dile object from log
    def delete_file(filename):
        self._log["files"][:] = [f for f in self._log["files"]
                                 if f.get("filename") != filename]
                
        self._update()
        
