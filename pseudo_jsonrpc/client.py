#!/usr/bin/env python3

import json
import socket
from contextlib import contextmanager
from .utils import RPCUtils


class JSONRPCClient(RPCUtils):
    """A JSON-RPC like client."""
    proces = None
    proxy = None

    def __init__(self, socketname):
        self.host, self.port = socketname
        self.proces = self.introspect()
        self.generate_proxy()

    def __getattr__(self, name):
        return getattr(self.proxy, name)

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(self.timeout)
        return sock

    def generate_proxy(self):
        proxy_class = "Proxy"
        bases = (object,)
        attrs = {}
        for procs in self.proces:
            key = procs["name"]
            value = lambda *args: self.call(key, args)
            attrs[key] = value
        self.proxy = type(proxy_class, bases, attrs)

    @contextmanager
    def connect(self):
        sock = self.create_socket()
        try:
            sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            pass
        try:
            yield sock
        except socket.timeout:
            print("Connection timed out")
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

    def call(self, procedure_name, args):
        with self.connect() as sock:
            request = json.dumps(
                {"procedure": procedure_name, "args": args})
            self.send(sock, request.encode())
            response = self.receive(sock)
            result = json.loads(response)
            return result.get("result", result.get("error"))

    def introspect(self):
        with self.connect() as sock:
            self.send(sock, b'INTROSPECT')
            data = self.receive(sock)
            if self.proces is None:
                response = json.loads(data)
                self.proces = response["proces"]
            return self.proces
        return []

    def procedures_help(self):
        print()
        helps = []
        for proc in self.proces:
            help_doc = proc["doc"]
            helps.append(help_doc)
        return "\n".join(helps)
