from unittest import TestCase
from btpeer import BTPeer


class TestBTPeer(TestCase):
    def test___init__(self):
        pass

    def setUp(self):
        self.peer_A = BTPeer()
        self.peer_B = BTPeer()

    def test_get_my_id(self):
        self.assertEqual(self.peer_A.my_id, '145.94.161.215:30000')
        self.assertEqual(self.peer_B.my_id, '145.94.161.215:30000')

    def test_set_my_id(self):
        self.peer_A.my_id = '145.94.161.215:30000'
        self.assertEqual(self.peer_A.my_id, ('145.94.161.215:30000'))

    def test_get_peer(self):
        self.peer_A.add_peer('145.94.161.215:30000', '145.94.161.215', 30001)
        self.assertEqual(self.peer_A.get_peer('145.94.161.215:30000'), ('145.94.161.215', 30001))

    def test_remove_peer(self):
        self.peer_A.add_peer('145.94.161.215:30000', '145.94.161.215', 30000)
        self.peer_A.remove_peer('145.94.161.215:30000')
        self.assertEqual(self.peer_A.peers, {})

    def test_get_all_peers(self):
        self.peer_A.add_peer('145.94.161.215:30000', '145.94.161.215', 30000)
        self.assertEqual(self.peer_A.get_all_peers(), ['145.94.161.215:30000'])

    def test_peer_nums(self):
        self.peer_A.add_peer('145.94.161.215:30000', '145.94.161.215', 30000)
        self.assertEqual(self.peer_A.peer_nums(), 1)

    def test_max_peers_reached(self):
        self.peer_A.add_peer('145.94.161.215:30000', '145.94.161.215', 30000)
        self.assertTrue(self.peer_A.max_peers_reached())
