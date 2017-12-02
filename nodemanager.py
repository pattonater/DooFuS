from entity import Entity
import json

class NodeManager:
    LISTEN_PORT = 8889
    
    def __init__(self, profile):
        self._nodes = {}
        self._seen = set()
        self._new = set()
        self._online = set()
        self._verified = set()
        self.profile = profile

    # iterate over active, verified nodes
    def __iter__(self):
        for host in self._nodes:
            if host in self._online and host in self._verified:
                yield self._nodes[host]

    def __getitem__(self, host):
        return self._nodes[host]
    
    # TODO is this necessary?
  #  def __contains__(self, host):
        # Just active so don't double connect to the same node before it's verified
        # kinda hacky, is there a better way to decide this? maybe a separate method but don't think this 'in' is used for anything else
   #     return host in self._online
        
######################################
## NodeManager Interface
#####################################

    def load_from_config(self):
        with open('config.json') as file:
            config = json.load(file)
            for node in config["Nodes"]:
                host = node["host"]
                id = node["id"]

                self._seen.add(host)
                
    def set_online(self, node):
        host = node.host()

        if host not in self._seen:
            print("NodeManager: First time seeing host %s" % (host))
            self._new.add(host)

        # node active, but not yet verified
        self._online.add(host)
        self._seen.add(host)
        self._nodes[host] = node
        print("NodeManager: Node %s online. Awaiting verification..." % (host))

    def set_offline(self,node):
        host = node.host()
        node.close_connection()
        self._online.remove(host)
        print("NodeManager: %s offline" % (host))
    
    def verify(self, node, id):
        # TODO have this test (from a file presumably) whether id is appropiate
        verified = True
        
        host = node.host()

        if verified:
            print("NodeManager: Node %s identity verified as %s" % (host, id))
            self._verified.add(host)
            if host in self._new:
                self._write_node_to_disc(host)
            
        else:
            print("NodeManager: Node %s identity %s not recognized" % (host, id))

            # don't call remove here because will happen automatically in the listen thread and don't want it to happen twice
            # calling close_connection speeds up that process though
            node.close_connection()
        return verified


    def not_connected(self, host):
        return host not in self._online

    def check_new(self, node):
        host = node.host()
        return host in self._new

    def inactive_hosts(self):
        return [host for host in self._seen if host not in self._active]


        
######################################
## Helper Functions
#####################################

                    
    def _write_node_to_disc(self, host):
        try:
            config = None
            # Reads out config (going to overwrite in a bit)
            with open('config.json', 'r') as file:
                config = json.load(file)

            # Add the new node.
            # TODO does this really need the id, going to re-verify everytime anyway?
            config["Nodes"].append({"host":host})

            # Write back to the file.
            with open('config.json', 'w+') as file:
                json.dump(config, file)

            print("Added %s to config file" % (host))

        except Exception as e:
            print("Failed to write new node to disc. Exception: " + str(e))

