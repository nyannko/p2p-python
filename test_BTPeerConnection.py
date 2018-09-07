from unittest import TestCase

import unittest

from btpeer import BTPeerConnection
from btpeer import BTPeer
import struct


class TestBTPeerConnection(TestCase):
    def setUp(self):
        # self.peer_A = BTPeer()
        # self.peer_A.main_loop()
        self.obj = BTPeerConnection('145.94.161.215:30000', '145.94.161.215', 30000)

    def test__make_msg(self):
        self.assertEqual(self.obj._make_msg(1, 'abc'), struct.pack('!LL%ds' % 3, 1, 3, 'abc'))

    def test_str_(self):
        self.assertEqual(str(self.obj), '145.94.161.215:30000')

    @unittest.skip("skipping")
    def test_send_data(self):
        self.obj.send_data(1, 'asdf')

    # todo recv data
    # @unittest.skip("skipping")
    def test_recv_data(self):
        self.assertTrue(self.obj.send_data(2, 'abc'))
        self.assertEqual(self.obj.recv_data(), (2, 'abc'))

    def test_close(self):
        self.obj.close()
        self.assertEqual(self.obj.s, None)
        self.assertEqual(self.obj.sd, None)
