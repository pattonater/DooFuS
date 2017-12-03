import json

class NetworkConfig:

    FILEPATH = 'data/config_network.json'


    def __init__(self):
        config = {}
        config["Nodes"] = []
        config["Identities"] = []
        
        try:
            with open(self.FILEPATH, 'r') as file:
                config = json.load(file)
        except Exception as e:
            print("Failed to open network config file. Exception: " + str(e))

        self._json = config

    def hosts(self):
        return [node["host"] for node in  self._json["Nodes"]]
    
    def identities(self):
        return [id for id in self._json["Identities"]]
                
    def add_host(self, host):
        self._json["Nodes"].append({"host":host})
        self._write_to_file()
        
        print("Added host %s to network config file" % (host))

    def add_id(self, id):
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


        
