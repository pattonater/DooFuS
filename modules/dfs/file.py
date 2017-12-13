import json
from threading import Lock

class File:

    # updates dict of indexed chunks and then serializes chunks to json file
    def __init__(self, filename, num_parts=1):
        self._lock = Lock()

        self._filename = filename

        # default download folder
        self._path = "files/"

        # where you write replicas
        self._replicaname = "replicas/" + filename + ".json"

        # if you already have the replica, load from file
        try:
            with open(self._replicaname) as file:
                jsonfile = json.load(file)
                self._total_parts = int(jsonfile[0])
                self._contents = jsonfile[1]   
        except:
            self._total_parts = int(num_parts)            
            self._contents = {}
        
    def write_to_replica(self, part, data):
        self._lock.acquire()

        # add part to contents and dump to json
        self._contents[str(part)] = data
        
        with open(self._replicaname, "w+") as file:
            jsonfile = [self._total_parts, self._contents]
            json.dump(jsonfile, file)

        self._lock.release()

    def write_to_file(self, part, data):
        # if you don't have this part add it to replicas TODO don't do this
        if data:
            self.write_to_replica(part, data)
        
        print("%d/%d parts written" % (len(self._contents), self._total_parts))
        
        # if you have all parts write to disk
        if (len(self._contents) == self._total_parts):
            print("writing %s to disk" % (self._filename))
            
            # clear contents of file
            open(self._path + self._filename, 'w+').close()
            
            # append each part to file
            with open(self._path + self._filename, "a+") as file:
                for i in range (1, self._total_parts + 1):
                    file.write(self._contents[str(i)])

    def read_from_replica(self, part):
        return self._contents[str(part)]

    def remove(self):
        os.remove(self._replicaname)

    def get_parts(self):
        return list(self._contents.keys())

    def set_path(self, path):
        
        if not path[-1] == "/":
            path += "/"

        self._path = path

    def set_total(self, total):
        self._total_parts = int(total)
