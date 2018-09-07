import socket
import logging
import struct
import threading


def setup_logger(logger_name=None, level=logging.DEBUG):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class BTPeer(object):

    def __init__(self, my_id=None, server_host=None, server_port=30000, max_peers=1):

        # todo too complicated
        if server_host:
            self.server_host = server_host
        else:
            self._init_server_host()

        self.server_port = int(server_port)

        # todo too complicated
        if my_id:
            self._my_id = my_id
        else:
            index = '{}:{}'.format(self.server_host, self.server_port)
            self._my_id = index

        self.max_peers = int(max_peers)
        self.peers = {}
        self.shut_down = False
        self.handlers = {}
        self._router = None
        self.logger = setup_logger()

    def _init_server_host(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('www.example.com', 80))
        self.server_host, _ = s.getsockname()

    @property
    def my_id(self):
        return self._my_id

    @my_id.setter
    def my_id(self, my_id):
        self._my_id = my_id

    @property
    def router(self):
        return self.router

    @router.setter
    def router(self, router):
        """
        Registers a routing function with this peer. The setup of routing is as follows:
        This peer maintains a list of other known peers, the routing function should take
        the name of the known peer(which may not necessarily be present in self.peers)
        and decide which of the known peers a message should be routed to next in order to
        (hopefully) reach the desired peer. The router function should return a tuple of three
        values: (next_peer_id, host, port). If the message cannot be routed, the next_peer_id
        should be None.
        :param router:
        :return: None
        """
        self._router = router

    def add_handler(self, msg_type, handler):
        assert len(msg_type) == 4
        self.handlers[msg_type] = handler

    def add_peer(self, peer_id, host, port):
        if peer_id not in self.peers and (len(self.peers) < self.max_peers or self.max_peer == 0):
            self.peers[peer_id] = (host, int(port))
            return True
        else:
            return False

    def get_peer(self, peer_id):
        return self.peers[peer_id]

    def remove_peer(self, peer_id):
        if peer_id in self.peers:
            del self.peers[peer_id]

    # todo
    def add_peer_at(self, loc, peer_id, host, port):
        self.peers[loc] = (peer_id, host, int(port))

    # todo
    def get_peer_at(self, loc):
        if loc not in self.peers:
            return None
        return self.peers[loc]

    # todo
    def remove_peer_at(self, loc):
        self.remove_peer(loc)

    def get_all_peers(self):
        return self.peers.keys()

    def peer_nums(self):
        return len(self.peers)

    def max_peers_reached(self):
        assert self.max_peers == 0 or len(self.peers) <= self.max_peers
        return 0 < self.max_peers == len(self.peers)

    def make_server_socket(self, port, backlog=5):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(backlog)
        return s

    def main_loop(self):
        s = self.make_server_socket(self.server_port)
        # s.settimeout(2)

        self.logger.info('Server started at {}:{}'.format(self.server_host, self.server_port))

        while not self.shut_down:
            try:
                self.logger.info('Listening for connections')
                client_sock, client_addr = s.accept()
                t = threading.Thread(target=self._handle_peer, args=[client_sock])
                t.start()
            except KeyboardInterrupt:
                self.logger.info('KeyboardInterrupt')
                self.shut_down = True
                continue
        self.logger.info('Main loop existing')
        s.close()

    def _handle_peer(self, client_sock):
        """
        Dispatches message from socket connections
        :param sock:
        :return:
        """
        try:
            host, port = client_sock.getpeername()
            peer_conn = BTPeerConnection(None, host, port, client_sock)

            msg_type, msg_data = peer_conn.recv_data()
            # if msg_type: msg_type = msg_type.upper()
            if msg_type not in self.handlers and msg_type:
                self.logger.info('Message type {}, {} not handled'.format(msg_type, msg_data))
            else:
                self.logger.info('Handle message type{}, {}'.format(msg_type, msg_data))
                self.handlers[msg_type] = peer_conn, msg_data
        except KeyboardInterrupt:
            self.logger.info('KeyboardInterrupt')
            raise

        self.logger.info('Disconnecting {}'.format(client_sock.getpeername()))
        peer_conn.close()

    def send_to_peer(self):
        pass

    def connect_and_send(self):
        pass

    def check_live_peers(self):
        pass


class BTPeerConnection(object):

    def __init__(self, peer_id, host, port, client_sock=None):
        self.peer_id = peer_id
        self.host = host
        self.port = int(port)
        if not client_sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = client_sock

        self.sd = self.s.makefile('rw', 0)

        self.logger = setup_logger()

    def __str__(self):
        return self.peer_id

    def _make_msg(self, msg_type, msg_data):
        msg_len = len(msg_data)
        msg = struct.pack('!LL%ds' % msg_len, msg_type, msg_len, msg_data)
        return msg

    def send_data(self, msg_type, msg_data):
        try:
            msg = self._make_msg(msg_type, msg_data)
            self.sd.write(msg)
            self.sd.flush()
        except KeyboardInterrupt:
            self.logger.info('KeyboardInterrupt')

        self.logger.info('Data sent')
        return True

    def recv_data(self):
        msg_type, msg_data = '', ''
        try:
            length = self.sd.read(4)
            if not length:
                return None, None
            msg_len = struct.unpack('!L', length)
            msg_type = self.sd.read(4)
            if not msg_type:
                return None, None

            msg_type, = struct.unpack('!L', msg_type)

            msg_data = ''
            while len(msg_data) != msg_len:
                data_block = self.sd.read(1)
                if not data_block:
                    break
                msg_data += data_block

        except KeyboardInterrupt:
            self.logger.info('KeyboardInterrupt')

        return msg_type, msg_data

    def close(self):
        self.s.close()
        self.s = None
        self.sd = None
