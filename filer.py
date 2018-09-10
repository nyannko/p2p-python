from btpeer import *

PEERNAME = 'NAME'
LISTPEERS = 'LIST'
INSERTPEER = 'JOIN'
QUERY = 'QUER'
QRESPONSE = 'RESP'
FILEGET = 'FGET'
PEERQUIT = 'QUIT'
REPLY = 'REPL'
ERROR = 'ERRO'


class FilerPeer(BTPeer):

    def __init__(self, my_id=None, server_host=None, server_port=30000, max_peers=1):
        BTPeer.__init__(self, my_id, server_host, server_port, max_peers)
        self.files = {}
        self.add_router(self.router)

        handlers = {
            LISTPEERS: self.__handle_listpeers,
            INSERTPEER: self.__handle_insertpeer,
            PEERNAME: self.__handle_peername,
            QUERY: self.__handle_query,
            QRESPONSE: self.__handle_qresponse,
            FILEGET: self.__handle_fileget,
            PEERQUIT: self.__handle_peerquit
        }

        for hd in handlers:
            self.add_handler(hd, handlers[hd])
        print(self.handlers)

    def add_router(self, peer_id):
        if peer_id in self.get_all_peers():
            router = [peer_id]
            router.extend(self.peers[peer_id])
            return router
        else:
            return None, None, None

    # self.handlers[msg_type](peer_conn, msg_data)
    def __handle_insertpeer(self, peer_conn, data):
        """
        Handle JOIN request
        The format of JOIN msg should be "peer_id, host, port"
        """
        peer_id, host, port = data.split()

        if self.max_peers_reached():
            self.logger.info("Max peers reached, cannot insert peer {}".format(peer_id))
            peer_conn.send_data(ERROR, "ERROR: Max peers reached, cannot be add to the list")
        elif peer_id not in self.peers:
            self.add_peer(peer_id, host, port)
            self.logger.info("Add peer {} to list".format(peer_id))
            peer_conn.send_data(REPLY, "REPLY: Add peer {} to list".format(peer_id))
            print "self.peers.status", self.peers
        else:
            self.logger.info("Peer {} has already existed in the list".format(peer_id))
            peer_conn.send_data(ERROR, "ERROR: Peer {} has already existed in the list".format(peer_id))

    def __handle_listpeers(self, peer_conn, data):
        self.logger.info("Listing peers {}".format(self.peer_nums()))
        for peer_id in self.get_all_peers():
            host, port = self.get_peer(peer_id)
            peer_conn.send_data(REPLY, "REPLY: {} {} {}".format(peer_id, host, port))

    def __handle_peername(self, peer_conn, data):
        """
        Reply with peer id
        """
        print "id", self.my_id
        return peer_conn.send_data(REPLY, str(self.my_id))

    def __handle_query(self, peer_conn, data):
        peer_id, key, ttl = None, None, None
        try:
            peer_id, key, ttl = data.split()
            peer_conn.send_data(REPLY, 'Query ACK: {}'.format(key))
        except:
            self.logger("Invalid query {}:{}".format(peer_conn, data))
            peer_conn.send_data(ERROR, 'Error: incorrect arguments')

        t = threading.Thread(target=self.__process_query, args=([peer_id, key, int(ttl)]))
        t.start()

    def __process_query(self, peer_id, key, ttl):
        for fname in self.files.keys():
            if key in fname:
                fpeer_id = self.files[fname]
                if not fpeer_id:
                    fpeer_id = self.my_id
                host, port = peer_id.split(':')
                self.connect_and_send(host, int(port), QRESPONSE,
                                      '{} {}'.format(fname, fpeer_id), pid=peer_id)
            return
        if ttl > 0:
            msg_data = "{} {} {}".format(peer_id, key, ttl - 1)
            for next_pid in self.get_all_peers():
                self.send_to_peer(next_pid, QRESPONSE, msg_data)

    def __handle_qresponse(self, peer_conn, data):
        fname, fpeer_id = data.split()
        if fname in self.files:
            self.logger.info("{} has been add to file list".format(fname))
        else:
            self.files[fname] = fpeer_id

    def __handle_fileget(self, peer_conn, data):
        fname = data
        if fname not in self.files:
            self.logger.info("File {} not found".format(fname))
            peer_conn.send_data(ERROR, 'ERROR: File not found')
            return
        try:
            with open(fname, 'r') as fr:
                data = fr.read()
        except:
            self.logger.info("Error reading file")
            peer_conn.send_data(ERROR, "Error: Error reading file")
            return
        peer_conn.send_data(REPLY, data)

    def __handle_peerquit(self, peer_conn, data):
        peer_id = data.strip()
        if peer_id in self.get_all_peers():
            msg = "QUIT: peer removed: {}".format(peer_id)
            self.logger.debug(msg)
            peer_conn.send_data(REPLY, msg)
            self.remove_peer(peer_id)
        else:
            msg = "Peer {} not found".format(peer_id)
            self.logger.debug(msg)
            peer_conn.send_data(ERROR, msg)

    def add_local_file(self, file_name):
        self.files[file_name] = None
        self.logger.info("Add local file {}".format(file_name))

    def build_peers(self, host, port, hops=1):
        """
        Attempt to build the local peer list up to the limit stored by
	    self.maxpeers, using a simple depth-first search given an
	    initial host and port as starting point. The depth of the
	    search is limited by the hops parameter.
        """

        if self.max_peers_reached() or not hops:
            return
        peer_id = None
        self.logger.info("Building peers from {}:{}".format(host, port))

        # __handle_peername
        _, peer_id = self.connect_and_send(host, port, PEERNAME, '')[0]
        self.logger.info("Contacted {}".format(peer_id))

        # __handle_insertpeer
        resp = self.connect_and_send(host, port, INSERTPEER, "{} {} {}"
                                     .format(self.my_id, self.server_host, self.server_port))[0]

        if resp[0] != REPLY or peer_id not in self.get_all_peers():
            return

        self.add_peer(peer_id, host, port)

        # do recursive depth first search to add more peers
        # __handle_listpeers
        # "REPLY: {} {} {}".format(peer_id, host, port), get all peer id
        resp = self.connect_and_send(host, port, LISTPEERS, '', peer_id=peer_id)
        if len(resp) > 1:
            resp.reverse()
            resp.pop()  # get rid of header count reply
            while len(resp):
                next_pid, host, port = resp.pop()[1].split()
                if next_pid != self.my_id:
                    self.build_peers(host, port, hops - 1)
