import json

class File:

    # updates dict of indexed chunks and then serializes chunks to json file
    def __init__(self, filename, num_parts):
        self._filename = "files/" + filename
        self._num_parts = num_parts        

        try:
            with open(self._filename) as file:
                self._contents = json.load(self._filename)
        except:
            self._contents = {}
        
    def write(self, part, data):
        self._contents[part] = data
        with open(self._filename) as file:
            json.dump(self._contents, file)

    def read_from_file():
        pass

    def read(self):
        return self._contents

    def remove(self):
        os.remove(self._filename)

    def get_parts(self):
        return list(self._contents.keys())
