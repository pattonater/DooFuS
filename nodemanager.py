from entity import Entity


class NodeManager:
    LISTEN_PORT = 8889
    
    def __init__(self, profile):
        self._nodes = {}
        self._seen = set()
        self._verified = set()
        #self._active = set()
        self.profile = profile

    def __iter__(self):
        for node in self._nodes.values():
            if node.is_alive():
                yield node

    def __getitem__(self, host):
        return self._nodes[host]
        
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
                not_mine = not host == self.profile.host:
                if not_mine:
                    self._seen.add(host)
                    self._verified.add(host)
                
    def add_node(self, node):


        self._nodes[node.host] = node
        if node.host in nodes:
        
        pass
    
    def verify_node(self, host, id):
        pass


    def active_nodes(self):
        return [node for node in self._nodes.values() if node.is_alive()]
    
        



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

    def _connect_to_network(self):
        for host in self._seen:

            #this will break the local testing
            not_mine = not host == self.profile.host:
            if not_mine:
                self._connect_to_node(host)

                    
    def _connect_to_node(host):
        try:
            # for testing locally: 8825 -> 8826 and 8826 -> 8825
            port = 8825 + (my_port % 2) if local_test else LISTEN_PORT
            conn = socket.create_connection((host, port), 1)

            # change connection for old node, or create new node
            if host in self._nodes:
                self._nodes[host].set_connection(conn)
            else:   
                node = Node(host, port, conn)    
                self._nodes[host] = node
            
            print("Connection to %s succeeded" % (host))

            # add new nodes to config file
            # TODO this shouldn't happen until a node is verified
            if not local_test and not host in self.seen:
                self._write_node_to_disc(host, "dweeb")
                self._seen.add(host)

            return True
        except:
            print("Connection to %s failed" % (host))
            return False

    def _write_node_to_disc(host, id):
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
            print("Failed to write new node to disc. Exception:\n" + e)


    def _send_heartbeats():
        while True:
            time.sleep(5)
            for node in _nodes.values():

                if node.is_alive():
                    success = node.send_heartbeat()
                
                    if success:
                        print("Hearbeat sent to %s (%d)" % (node._host, node._port))
                    else:
                        print("Node %s (%d) not found. Disconnecting" % (node._host, node._port))
                        node.close_connection()
