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

    def add_chunk(self, filename, chunk):
        self._files[filename].add_chunk(chunk)

    def write(self, filename):
        print("Writing " + filename)
        self._files[filename].write()
