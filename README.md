# Pseudo_jsonrpc
This is not a real JSON-RPC server, is a toy and does not follow the JSON-RPC protocol, read here:

- https://www.jsonrpc.org/

I wrote this for fun. Implementing a real JSON-RPC server will take you some time. To save
your time, check these out,

- https://github.com/tomerfiliba/rpyc
- https://github.com/irmen/Pyro4

# How to play it, example here

## For server
```python
!# /usr/bin/env python3
# Assume this code saved in a file named "server.py"
from pseudo_jsonrpc import JSONRPCServer

if __name__ == '__main__':
	def add(a, b):
		return a + b

	def sub(a, b):
		return a - b

	server = JSONRPCServer(("", 12321), "log.txt")
	# register procedures to be provided
	server.register(add)
	server.register(sub)
	# set workers
	# server.workers = 4
	# set max connections
	# server.connections = 64
	server.serve_forever()
```

## For client
``` python
#! /usr/bin/env python3
# Assume this code saved in a file named "client.py"
from pseudo_jsonrpc import JSONRPCClient

if __name__ == '__main__':
	client = JSONRPCClient(("", 12321))
	# print docs
	print(client.procedures_help())
	print(client.call("add", [1, 2]))
	print(client.call("add", [2, 3]))
	print(client.call("sub", [4, 2]))
	# or
	print(client.add(1, 2))
	print(client.sub(2, 3))
```
