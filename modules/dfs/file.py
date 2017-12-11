import json

class File:

    # updates dict of indexed chunks and then writes all at once to a serialized json file
    def __init__(self, filename, size, chunk_size = 8):
        self._contents = {}
        self._filename = "files/" + filename
        self._size = size
        self._chunk_size = chunk_size
        self._num_chunks = -(-size//chunk_size)

    def add_chunk(self, chunk, index):
        self._contents[index] = chunk

    def write(self):
        with open(self._filename) as file:
            json.dump(self._contents, file)
        self.clear_contents()

    def read(self):
        with open(self._filename) as file:
            self._contents = json.load(self._filename)
        return self._contents

    def clear_contents(self):
        self._contents = ""

    def remove(self):
        os.remove(self._filename)

    def get_size(self):
        return self._size

    def get_chunk_indices(self):
        return list(self._contents.keys())
