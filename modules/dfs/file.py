import json
from threading import Lock

class File:

    # updates dict of indexed chunks and then serializes chunks to json file
    def __init__(self, filename, num_parts):
        self._lock = Lock()

        self._filename = "files/" + filename
        self._replicaname = "replicas/" + filename + ".json"
        self._num_parts = num_parts        

        try:
            with open(self._replicaname) as file:
                self._contents = json.load(self._filename)
        except:
            self._contents = {}
        
    def write(self, part, data):
        self._lock.acquire()

        self._contents[part] = data

        with open(self._replicaname, "w+") as file:
            json.dump(self._contents, file)

        self._lock.release()

    def write_slice(self, part, data):
        self.write(part, data)
        
        if (len(self._contents) == num_parts):
            self.write_to_files()

    def write_to_files():
        with open(self._filename, "ab+") as file:
            for i in range (0, num_parts):
                file.write(self._contents[i])

    def read_slice(part):
        return self._contents[part]

    def remove(self):
        os.remove(self._replicaname)

    def get_parts(self):
        return list(self._contents.keys())
