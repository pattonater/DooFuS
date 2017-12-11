from .file import File

# stores a dict of files and writes to them
class Filewriter:

    def __init__(self):
        self._files = {}

    def write(self, filename, part, total, data):
        if not filename in self._files:
            self._files[filename] = File(filename, total)
        
        self._files[filename].write(part, data)

    def read(self, filename):
        return self._files[filename].read()

    def get_parts(self, filename):
        return self._files[filename].get_parts()

    def write_slice(self, filename, part, data):
        pass

    def remove(self, filename):
        self._files[filename].remove()
        del self._files[filename]

    def read_slice(filename, part):
        return self.files[filename].read_slice(part)