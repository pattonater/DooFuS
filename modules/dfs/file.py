import json
from threading import Lock

class File:

    # updates dict of indexed chunks and then serializes chunks to json file
    def __init__(self, filename, num_parts=1):
        self._lock = Lock()

        # where you write downloads
        self._filename = "files/" + filename

        # where you write replicas
        self._replicaname = "replicas/" + filename + str(num_parts) + ".json"

        # if you already have the replica, load from file
        try:
            with open(self._replicaname) as file:
                jsonfile = json.load(file)
                self._total_parts = jsonfile[0]
                self._contents = jsonfile[1]   
        except:
            self._total_parts = num_parts            
            self._contents = {}
        
    def write_to_replica(self, part, data):
        self._lock.acquire()

        self._contents[part] = data

        with open(self._replicaname, "w+") as file:
            jsonfile = [self._total_parts, self._contents]
            json.dump(jsonfile, file)

        self._lock.release()

    def write_to_file(self, part, data):
        if data:
            self.write(part, data)
        
        if (len(self._contents) == num_parts):
            with open(self._filename, "ab+") as file:
                for i in range (0, num_parts):
                    file.write(self._contents[i])

    def read_from_replica(part):
        return self._contents[part]

    def remove(self):
        os.remove(self._replicaname)

    def get_parts(self):
        return list(self._contents.keys())
