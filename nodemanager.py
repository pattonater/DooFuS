from entity import Entity
import json

class NodeManager:
    LISTEN_PORT = 8889
    
    def __init__(self, profile):
        self._nodes = {}
        self._seen = set()
        self._verified = set()
        self._active = set()
        self.profile = profile

    # iterate over active nodes
    def __iter__(self):
        for node in self._nodes.values():
            if node.is_alive():
                yield node

    def __getitem__(self, host):
        return self._nodes[host]

    def __contains__(self, host):
        return host in self._active
        
######################################
## NodeManager Interface
#####################################

    def load_from_config(self):
        with open('config.json') as file:
            config = json.load(file)
            for node in config["Nodes"]:
                host = node["host"]
                id = node["id"]

                # assume every id written to disc is verified for now
                not_mine = not host == self.profile.host
                if not_mine:
                    self._seen.add(host)
                    self._verified.add(host)
                
    def add(self, node):
        host = node._host

        # this assumes every node is verified
        if not host in self._seen:
            self._verified.add(host)
            self._write_node_to_disc(host, "dweeb")

        self._seen.add(host)
        self._nodes[host] = node
        self._active.add(host)

    def remove(self,node):
        host = node._host
        self._active.remove(host)
    
    def verify_node(self, host, id):
        pass


    def active_nodes(self):
        return [node for node in self._nodes.values() if node.is_alive()]
    
    def inactive_hosts(self):
        return [host for host in self._seen if host not in self._active]



    def join_network(self):
        # attempt to connect to previously seen nodes
        # should this be on a separate thread?
        # pros: user can interact with program right away
        # cons: possible race conditions?
        threading.Thread(target=self._connect_to_network).start()

        # start up heatbeat thread
        threading.Thread(target=self._send_heartbeats).start()


        
######################################
## Helper Functions
#####################################

                    
    def _write_node_to_disc(self, host, id):
        try:
            config = None
            # Reads out config (going to overwrite in a bit)
            with open('config.json', 'r') as file:
                config = json.load(file)

            # Add the new node.
            config["Nodes"].append({"host":host, "id":id})

            # Write back to the file.
            with open('config.json', 'w+') as file:
                json.dump(config, file)

            print("Added %s (%s) to config file" % (host, id))

        except Exception as e:
            print("Failed to write new node to disc. Exception: " + str(e))

