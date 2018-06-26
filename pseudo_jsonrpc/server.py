#!/usr/bin/env python3

import inspect
import json
import socket
from threading import Thread
from .utils import RPCUtils


class JSONRPCServer(RPCUtils):
    """
    A RPC like Server.
    This is not a real JSON-RPC server, it does
    not follow the JSON-RPC protocol, read here:
    https://www.jsonrpc.org/.

    I wrote this for fun. Implementing a real JSON-RPC
    server will take you some time. To save your time,
    check these out,
    https://github.com/tomerfiliba/rpyc
    https://github.com/irmen/Pyro4
    """
    workers = 4
    max_connections = 64

    def __init__(self, socketname, logfile=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(socketname)
        self.logfile = logfile
        self.socket = sock
        self.registers = {}

    def log(self, string, end="\n"):
        if self.logfile is None:
            print(string, file=self.logfile, end=end)
        else:
            with open(self.logfile, "a") as log:
                print(string, file=log, end=end)

    def data_to_dict(self, data):
        """ return dict object"""
        return json.loads(data)

    def dict_to_data(self, _dict):
        """ return data"""
        return json.dumps(_dict).encode()

    def register(self, procedure):
        assert callable(procedure)
        self.registers[procedure.__name__] = procedure

    def unregister(self, procedure_name, err=False):
        if err:
            procedure = self.registers.pop(procedure_name)
        else:
            procedure = self.registers.pop(procedure_name, None)
            if procedure:
                self.log("Successful to unregister {}".format(procedure_name))
            else:
                self.log("Failed to unregister {}".format(procedure_name))

    def handle(self, procedure_name, args):
        """ Call the procedure """
        procedure = self.registers.get(procedure_name, None)
        if procedure is None:
            return None
        else:
            return procedure(*args)

    def procedure_list(self):
        procs = []
        for name, proc in self.registers.items():
            sign = ', '.join(key for key in
                             inspect.signature(proc).parameters)
            data = dict(name="%s" % (name,),
                        sign="%s" % (sign,),
                        doc="{name}({sign})\n{doc}"
                        .format(name=name,
                                sign=sign,
                                doc=(proc.__doc__ or "NO DOCS")))
            procs.append(data)
        response = json.dumps(dict(proces=procs)).encode()
        return response

    def handle_conversation(self):
        while True:
            try:
                conn, address = self.socket.accept()
                conn.settimeout(self.timeout)
                request = self.receive(conn)
                if request == b"INTROSPECT":
                    self.send(conn, self.procedure_list())
                else:
                    data = self.data_to_dict(request)
                    self.log("Connection from {}".format(address))
                    self.log("-> {}".format(data))
                    procedure_name = data["procedure"]
                    args = data.get("args", None)
                    result = self.handle(procedure_name, args)
                    if result is None:
                        error = NameError("No such procedure provided")
                        data = {"error": repr(error)}
                    else:
                        data = {"result": result}
                    self.log("<- {}".format(data))
                    response = self.dict_to_data(data)
                    self.send(conn, response)
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
            except socket.timeout:
                self.log("Connection from {} timed out".format(address))
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                continue
            except EOFError as e:
                self.log(
                    "Connection from {} didn't closed normally."
                    .format(address))
            except Exception as e:
                self.log("{}".format(e))

    def serve_forever(self):
        self.socket.listen(self.max_connections)
        print("Listening at {}".format(self.socket.getsockname()))
        for i in range(self.workers):
            Thread(target=self.handle_conversation).start()
