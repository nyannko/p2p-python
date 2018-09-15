from unittest import TestCase
from btpeer import BTPeer
import socket


class TestBTPeer(TestCase):
    def test___init__(self):
        pass

    def setUp(self):
        self.peer_A = BTPeer()
        self.peer_B = BTPeer(server_port=30001)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('example.com', 80))
        self.address = sock.getsockname()[0]
        self.a_addr = self.address + ':30000'
        self.b_addr = self.address + ':30001'

    def test_get_my_id(self):
        self.assertEqual(self.peer_A.my_id, self.a_addr)
        self.assertEqual(self.peer_B.my_id, self.b_addr)

    def test_set_my_id(self):
        self.peer_A.my_id = self.a_addr
        self.assertEqual(self.peer_A.my_id, self.a_addr)

    def test_get_peer(self):
        self.peer_A.add_peer(self.a_addr, self.address, 30001)
        self.assertEqual(self.peer_A.get_peer(self.a_addr), (self.address, 30001))

    def test_remove_peer(self):
        self.peer_A.add_peer(self.a_addr, self.address, 30000)
        self.peer_A.remove_peer(self.a_addr)
        self.assertEqual(self.peer_A.peers, {})

    def test_get_all_peers(self):
        self.peer_A.add_peer(self.a_addr, self.address, 30000)
        self.assertEqual(self.peer_A.get_all_peers(), [self.a_addr])

    def test_peer_nums(self):
        self.peer_A.add_peer(self.a_addr, self.address, 30000)
        self.assertEqual(self.peer_A.peer_nums(), 1)

    def test_max_peers_reached(self):
        self.peer_A.add_peer(self.a_addr, self.address, 30000)
        self.assertTrue(self.peer_A.max_peers_reached())

    def test_check_live_peers(self):
        self.peer_B.add_peer(self.a_addr, self.address, 30000)
        peer_conn = self.peer_B.check_live_peers()
        # Should be empty dict if peer down
        self.assertEqual(self.peer_B.peers, {})
        # print self.peer_B.handlers
        # print peer_conn.recv_data()
