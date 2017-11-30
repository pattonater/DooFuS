# DFS API
# Flat

# selfs:
#  _log_name
#  _log
#  

import json

class DFS:

    def __init__(self, log_name = None):
        # initialize DFS:
        self._log_name = log_name if log_name else "dfs.json"
        # flat structure (make one folder, put files inside)

        with open(self._log_name, 'r') as file:
            self._log = json.load(file)        

    def add_file(filename):
        # check to see if filename already exists
        # if not:
            # Add to log

    def delete_file(filename):
