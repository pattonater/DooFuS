import json

class NetworkConfig:

    FILEPATH = 'data/config_network.json'


    def __init__(self):
        self._json = {}
        self._json["Nodes"] = []
        self._json["Identities"] = []

        try:
            with open(self.FILEPATH, 'r') as file:
                self._json = json.load(file)
        except FileNotFoundError:
            self._write_to_file()

    def hosts(self):
        return [node["host"] for node in  self._json["Nodes"]]
    
    def identities(self):
        return [id for id in self._json["Identities"]]
                
    def store_host(self, host):
        self._json["Nodes"].append({"host":host})
        self._write_to_file()
        

    def store_id(self, id):
        self._json["Identities"].append(id)
        self._write_to_file()
        
        print("Added id %s to network config file" % (id))


    def _write_to_file(self):
        try:
            # Write back to the file.
            with open(self.FILEPATH, 'w+') as file:
                json.dump(self._json, file)
        except Exception as e:
            print("Failed to write network config file to disc. Exception: " + str(e))


        
