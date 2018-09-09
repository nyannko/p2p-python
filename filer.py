from btpeer import *

PEERNAME = 'NAME'
LISTPEERS = 'LIST'
INSERTPEER = 'JOIN'
QUERY = 'QUER'
RESPONSE = 'RESP'
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
            RESPONSE: self.__handle_response,
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
        pass

    def __handle_response(self, peer_conn, data):
        pass

    def __handle_fileget(self, peer_conn, data):
        pass

    def __handle_peerquit(self):
        pass
