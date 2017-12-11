from .file import File

# stores a dict of files and writes to them
class Filewriter:

    def __init__(self):
        self._files = {}

    def add_file(self, filename):
        if not filename in self._files:
            self._files[filename] = File(filename)
        else:
            self._files[filename].clear_contents()

    def add_chunk(self, filename, chunk, index):
        self._files[filename].add_chunk(chunk, index)

    def write(self, filename):
        #print("Writing " + filename)
        self._files[filename].write()

    def read(self, filename):
        return read self._files[filename].read()

    def get_chunk_indices(self, filename):
        return self._files[filename].get_chunk_indices()

    def remove(self, filename):
        self._files[filename].remove()
        del self._files[filename]
