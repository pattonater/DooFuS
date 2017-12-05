class File:

    # updates contents with each chunk and then writes all at once
    def __init__(self, filename):
        self._contents = ""
        self._filename = "files/" + filename

    def add_chunk(self, chunk):
        self._contents += chunk

    def write(self):
        file = open(self._filename,"w+")
        file.write(self._contents)
        file.close()

    def clear_contents(self):
        self._contents = ""
