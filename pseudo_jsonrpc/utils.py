#! /usr/bin/env python3
import struct


class RPCUtils(object):
    """
    Send and receive 'length-prefixed' message.
    """

    header_struct = struct.Struct('!I')
    timeout = 30

    def receive_block(self, sock, size):
        datas = []
        while size:
            data = sock.recv(size)
            if not data:
                raise EOFError('socket closed with {} bytes left'
                               ' in this block'.format(size))
            size -= len(data)
            datas.append(data)
        return b''.join(datas)

    def receive(self, conn):
        data = self.receive_block(conn, self.header_struct.size)
        (size,) = self.header_struct.unpack(data)
        return self.receive_block(conn, size)

    def send(self, sock, data):
        size = len(data)
        sock.send(self.header_struct.pack(size))
        sock.send(data)
