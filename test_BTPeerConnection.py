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
        self.assertEqual(self.obj._make_msg(1, 'ping'), struct.pack('!LL%ds' % 4, 1, 3, 'ping'))

    def test_str_(self):
        self.assertEqual(str(self.obj), '145.94.161.215:30000')

    def test_send_data(self):
        self.obj.send_data(1, 'ping')

    def test_close(self):
        self.obj.close()
        self.assertEqual(self.obj.sock, None)
