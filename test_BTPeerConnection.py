from unittest import TestCase

from btpeer import BTPeerConnection
from btpeer import BTPeer
import struct


class TestBTPeerConnection(TestCase):
    def setUp(self):
        # self.peer_A = BTPeer()
        # self.peer_A.main_loop()
        self.obj = BTPeerConnection('145.94.161.215:30000', '145.94.161.215', 30000)

    def test__make_msg(self):
        # (msgtype(4 char), msg_len, msg(%d))
        self.assertEqual(self.obj._make_msg('ping', 'Are you here?'),
                         struct.pack('!4sL%ds' % 13, 'ping', 13, 'Are you here?'))

    def test_str_(self):
        self.assertEqual(str(self.obj), '145.94.161.215:30000')

    def test_send_data(self):
        self.obj.send_data('ping', 'Are you here?')

    def test_close(self):
        self.obj.close()
        self.assertEqual(self.obj.sock, None)
