from unittest import TestCase
from filer import *


class TestFilerPeer(TestCase):
    def setUp(self):
        # self.peer_B = FilerPeer(2, server_port=30001)
        # Build connections to this address
        self.conn = BTPeerConnection('145.94.161.215:30000', '145.94.161.215', 30000)

    def test___handle_insertpeer(self):
        # The format of JOIN msg should be "peer_id, host, port"
        data = "145.94.161.215:30000 145.94.161.215 30000"
        self.assertTrue(self.conn.send_data('JOIN', data))

    def test__handle_peername(self):
        data = ""
        self.assertTrue(self.conn.send_data('NAME', data))

    def test__handle_listpeers(self):
        data = ""
        self.assertTrue(self.conn.send_data('LIST', data))
