from entity import Entity


class NodeManager:
    def __init__(self, me):
        self._nodes = {}
        self._seen = set()
        self._verified = set()
        self.profile = profile

    ######################################
    ## NodeManager Interface
    #####################################

    def load_from_config(self, nodes):
        with open('config.json') as file:
            config = json.load(file)
            for node in config["Nodes"]:
                host = node["host"]
                port = int(node["port"])
                id = node["id"]

                # assume every id written to disc is verified for now
                self._seen.add(host)
                self._verified.add(host)
                
                not_mine = not host == profile.host and not port == profile.port 
                if not_mine:
                    port = node["port"]
                    self._connect_to_node(host)
    

    def _connect_to_node(host):
        try:
            # for testing locally: 8825 -> 8826 and 8826 -> 8825
            port = 8825 + (my_port % 2) if local_test else PORT
            conn = socket.create_connection((host, port), 1)

            # change connection for old node, or create new node
            if host in self._nodes:
                self._nodes[host].set_connection(conn)
            else:   
                node = Node(host, port, conn)    
                self._nodes[host] = node
            
            print("Connection to %s (%d) succeeded" % (host, port))

            # add new nodes to config file
            # TODO this shouldn't happen until a node is verified
            if not local_test and not host in self.seen:
                self._write_node_to_disc(host, port)
                self._seen.add(host)

            return True
        except:
            print("Connection to %s (%d) failed" % (host, port))
            return False

    def _write_node_to_disc(host, port):
        try:
            config = None
            # Reads out config (going to overwrite in a bit)
            with open('config.json', 'r') as file:
                config = json.load(file)

            # Add the new node.
            config["Nodes"].append({"host":host, "port":port, "id":"dweeb"})

            # Write back to the file.
            with open('config.json', 'w+') as file:
                json.dump(config, file)

            print("Added %s:%d to config file" % (host, PORT))

        except Exception as e:
            print("Failed to write new node to disc. Exception:\n" + e)

