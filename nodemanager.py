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

    # iterate over active, verified nodes
    def __iter__(self):
        for host in self._nodes:
            if host in self._active and host in self._verified:
                yield self._nodes[host]

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

                # add every host as seen
                not_mine = not host == self.profile.host
                #if not_mine:
                self._seen.add(host)
                
    def online(self, node):
        host = node._host

        # node active, but not yet verified
        self._active.add(host)
        self._seen.add(host)
        self._nodes[host] = node
        print("NodeManager: added %s" % (host))

    def offline(self,node):
        host = node._host
        node.close_connection()
        self._active.remove(host)
        print("NodeManager: removed %s" % (host))
    
    def verify(self, node, id):
        # TODO have this test (from a file presumably) whether id is appropiate
        verified = True
        
        host = node._host

        if verified:
            print("NodeManager: Node %s identity verified as %s" % (host, id))
            self._verified.add(host)
            if host not in self._seen:
                self._write_node_to_disc(host, "dweeb")
        else:
            print("NodeManager: Node %s identity %s not recognized" % (host, id))
            node.close_connection()
            # don't call remove here because will happen automatically in the listen thread
            # calling close_connection speeds up that process though
            

    def active_nodes(self):
        return [node for node in self._nodes.values() if node.is_alive()]
    
    def inactive_hosts(self):
        return [host for host in self._seen if host not in self._active]


        
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

