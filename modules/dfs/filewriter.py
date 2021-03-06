from .file import File
from os import listdir

# stores a dict of files and writes to them
class Filewriter:

    def __init__(self):
        self._files = {}
        replicas = listdir("replicas/")
        # add all existing files
        for file in replicas:
            filename = file[:-5]
            ext = file[-5:]
            if ext == ".json":
                print("loading %s replica" % filename)
                self.add_file(filename)

    def add_file(self, filename, total = None):
        if not filename in self._files:
            self._files[filename] = File(filename, total)
        elif total:
            self._files[filename].set_total(total)

    def write_to_replica(self, filename, part, total, data):
        self.add_file(filename, total)
        self._files[filename].write_to_replica(part, data)

    def write_to_file(self, filename, part = None, total = None, data = None):
        self.add_file(filename, total)
        self._files[filename].write_to_file(part, data)

    def read_from_replica(self, filename, part):
        return self._files[filename].read_from_replica(part)

    def read_from_file(self, filepath):
        try:
            with open(filepath, "r") as file:
                return file.read()
        except FileNotFoundError:
            return False

    def remove(self, filename):
        self._files[filename].remove()
        del self._files[filename]

    def get_parts(self, filename):
        return self._files[filename].get_parts()

    def set_path(self, filename, path):
        self.add_file(filename)
        self._files[filename].set_path(path)
