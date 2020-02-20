#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 6000        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    request = "GET /getpeers HTTP/1.1\r\nHost:%s\r\nUser-agent: client_4\r\n" % HOST
    client.sendall(request.encode())
    response = client.recv(1024)

print('Received', repr(response))
http_response = repr(response)
http_response_len = len(http_response)

# display the response
print("[RECV] - length: %d" % http_response_len)
print(http_response)